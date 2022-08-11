import time
from typing import Dict, List, Union

import requests
from requests.exceptions import RequestException
from telebot.types import CallbackQuery, InputMediaPhoto

from config_data.config import NoSuitableValueError, bot
from database.dbworker import get_parameter, get_results
from utils.misc.api_request import request_to_api
from utils.misc.reset import reset


def check_photo(photo_url: str) -> bool:
    """
    Функция. Проверяет ссылку на фото на поврежденность.
    """
    try:
        photo = requests.get(url=photo_url, timeout=30)
        if photo.status_code == 200:
            return True
        return False
    except RequestException:
        return False


def media_group_generation(urls_lst: List[str], caption: str) -> list:
    """
    Функция. Формирует медиагруппу с фотографиями отеля.
    """
    media_group = list()
    photo_num = 0

    for i_url in urls_lst:
        if check_photo(i_url):
            if urls_lst.index(i_url) == 0:
                media_group.append(InputMediaPhoto(media=i_url, caption=caption))
            else:
                media_group.append(InputMediaPhoto(media=i_url))
            photo_num += 1

        if photo_num == 5:
            break
    else:
        for _ in range(5 - photo_num):
            media_group.append(InputMediaPhoto(media='https://upload.wikimedia.org/wikipedia/commons/thumb/a/'
                                                     'ac/No_image_available.svg/1024px-No_image_available.svg.png'))

    return media_group


def photo_issuing_handler(call: CallbackQuery) -> None:
    """
    Функция. Обрабатывает Inline кнопки с ответом на вопрос о необходимости выдачи фото
    и формирует сообщения пользователю с информацией по отелям
    """
    user_id = call.from_user.id
    request_res = get_results(user_id)

    if str(call.data) == 'yes':
        bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id,
                              text='Мы ищем для вас фото в лучшем качестве. '
                              'Формирование ответа займет некоторое время.'
                              'Пожалуйста, ожидайте.',
                              reply_markup=None)

        parameters = dict()
        url = 'https://hotels4.p.rapidapi.com/properties/get-hotel-photos'
        pattern = r'(?<=,)"hotelImages".+?(?=,"roomImages")'

        for i_hotel in request_res:
            try:
                parameters["id"] = i_hotel['hotel_id']
                photos = request_to_api(url, parameters, pattern)
                if photos is None:
                    raise NoSuitableValueError
                urls = [i['baseUrl'].format(size="w") for i in photos["hotelImages"]]
                bot.send_media_group(chat_id=user_id,
                                     media=media_group_generation(urls, message_generation(i_hotel, call.from_user.id)))
            except NoSuitableValueError:
                blank_img = 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/' \
                            'No_image_available.svg/1024px-No_image_available.svg.png'
                media_group = [(InputMediaPhoto(media=blank_img, caption=message_generation(i_hotel, call.from_user.id))
                               if i_num == 1 else InputMediaPhoto(media=blank_img)) for i_num in range(5)]
                bot.send_media_group(chat_id=user_id, media=media_group)
            except RequestException:
                bot.send_message(chat_id=user_id,
                                 text='К сожалению произошла внутренняя ошибка. Попробуйте снова.')
    elif str(call.data) == 'no':
        bot.edit_message_reply_markup(chat_id=user_id, message_id=call.message.message_id, reply_markup=None)
        for i_hotel in request_res:
            bot.send_message(chat_id=user_id,
                             text=message_generation(i_hotel, user_id),
                             disable_web_page_preview=True)

    time.sleep(3)
    bot.send_message(chat_id=user_id,
                     text='Спасибо за использование нашего бота. Всего вам доброго!')
    reset(call)


def message_generation(user_dict: Dict[str, Union[str, int]], user_id: int) -> str:
    """
    Функция. Формирует сообщение пользователю с информацией по отелям.
    """
    residence_period = 1
    address = user_dict['address']
    hotel_url = user_dict['hotel_url']
    distance = user_dict['distance']
    cost = float(user_dict['cost'])

    year_from, month_from, day_from = str(get_parameter(user_id, 'date_from')).split('-')
    year_to, month_to, day_to = str(get_parameter(user_id, 'date_to')).split('-')

    if month_to != month_from:
        if month_from in ['01', '03', '05', '07', '08', '10', '12']:
            residence_period = (31 - int(day_from)) + int(day_to)
        elif month_from in ['04', '06', '09', '11']:
            residence_period = (31 - int(day_from)) + int(day_to)
        elif month_from == '02' and ((int(year_from) - 2020) // 4 == 0):
            residence_period = (29 - int(day_from)) + int(day_to)
        elif month_from == '02':
            residence_period = (28 - int(day_from)) + int(day_to)
    else:
        residence_period = int(day_to) - int(day_from)

    if cost == 0:
        cost, total_cost = ('Информация отсутствует' for _ in range(2))
    else:
        total_cost = str(round(cost * residence_period, 2)) + ' RUB'
        cost = str(cost) + ' RUB'

    message = f"🏨 Название отеля: {user_dict['hotel_name']}" \
              f"\n🌎 Адрес отеля: {address} " \
              f"\n↔ Расстояние от центра: {distance}" \
              f"\n1️⃣ Цена за сутки: {cost}" \
              f"\n💳 Итоговая цена: {total_cost}" \
              f"\n🌐 Ссылка на отель: {hotel_url}"
    return message
