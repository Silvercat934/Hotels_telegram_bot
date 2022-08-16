from requests.exceptions import ReadTimeout, RequestException
from telebot.types import CallbackQuery

from config_data.config import bot, calendar, translator_two
from database.dbworker import (States, get_parameter, set_state,
                               update_parameter, update_results)
from handlers.api_handlers.high_or_low_price import hotels_founding
from keyboards.photo_request_inline import photo_markup
from keyboards.price_range_inline import prices_markup


def bestdeal_destination_id_handler(call: CallbackQuery) -> None:
    """
    Функция - обработчик Inline кнопок с районами города. Также запрашивает у пользователя дату заезда в отель.
    """
    user_id = call.from_user.id
    update_parameter(user_id, 'destination_id', call.data)

    bot.edit_message_reply_markup(chat_id=user_id, message_id=call.message.message_id, reply_markup=None)
    bot.send_message(
        chat_id=user_id,
        text=f'Выберите дату заезда.',
        reply_markup=calendar
        )
    set_state(user_id, States.enter_arrival_date_state.value)


def distances_handler(call: CallbackQuery) -> None:
    """
    Функция - обработик Inline кнопок с вариантами диапазона расстояний.
    """
    user_id = call.from_user.id

    update_parameter(user_id, 'distance_range', "'" + call.data + "'")
    bot.edit_message_reply_markup(chat_id=user_id, message_id=call.message.message_id, reply_markup=None)
    bot.send_message(chat_id=user_id,
                     text='Спасибо, укажите диапазон цен.',
                     reply_markup=prices_markup())
    set_state(user_id, States.enter_prices_state.value)


def prices_handler(call: CallbackQuery) -> None:
    """
    Функция - обработик Inline кнопок с вариантами диапазона цен.
    Также обрабатывает результат запроса к API и отсекает отели, не подходящие по условию.
    Результат отбора записывается в БД
    """
    user_id = call.from_user.id
    hotels = dict()
    parameters = {"destinationId": get_parameter(call.from_user.id, 'destination_id'),
                  "sortOrder": 'DISTANCE_FROM_LANDMARK', "currency": 'RUB', "locale": "ru_RU"}
    bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id, text='Ожидайте. Идет обработка запроса.',
                          reply_markup=None)

    time = get_parameter(user_id, 'time')
    parameters["priceMin"], parameters["priceMax"] = [int(i_price) for i_price in call.data.split('-')]
    distance_from, distance_to = [int(distance) for distance in
                                  get_parameter(user_id, 'distance_range').split('-')]
    condition_matches, hotels_info = list(), list()

    try:
        hotels = hotels_founding(parameters)
    except ReadTimeout:
        bot.send_message(chat_id=user_id,
                         text='Продолжаю поиск.')
        hotels = hotels_founding(parameters)
    except RequestException:
        bot.send_message(chat_id=user_id,
                         text='К сожалению произошла внутренняя ошибка. Попробуйте снова.')

    if hotels is None:
        bot.send_message(chat_id=user_id,
                         text='По вашему запросу ничего не найдено. Попробуйте изменить параметры запроса.')
        reset(call)
    else:
        hotels = hotels["results"]
        for i_hotel in hotels:
            distance = float(i_hotel.get('landmarks', [dict()])[0].get('distance', '0 км')[:-3])
            if distance_from <= distance <= distance_to:
                condition_matches.append(i_hotel)
        hotels = condition_matches[:5]

        for i_hotel in hotels:
            hotel_id = i_hotel.get('id', 000000)
            hotel_name = i_hotel.get('name', '')
            address = translator_two.translate(f"{i_hotel.get('address', {}).get('streetAddress', '')},"
                                               f"{i_hotel.get('address', {}).get('locality', '')},"
                                               f"{i_hotel.get('address', {}).get('countryName', '')}")
            distance = i_hotel.get('landmarks', [{}])[0].get('distance', '0 км')
            cost = str(i_hotel.get('ratePlan', {}).get('price', {}).get('exactCurrent', 0))
            hotel_url = 'https://www.hotels.com/ho' + str(i_hotel.get('id', 000000))
            hotels_info.append((user_id, time, hotel_id, hotel_name,
                                address, distance, cost, hotel_url))
        update_results(hotels_info)

        bot.send_message(chat_id=user_id,
                         text='Необходимо выдать фото ?',
                         reply_markup=photo_markup())
        set_state(user_id, States.result_issuing_state.value)
