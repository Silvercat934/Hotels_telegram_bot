from typing import Dict

from requests.exceptions import ReadTimeout, RequestException
from telebot.types import CallbackQuery

from config_data.config import bot, calendar, translator_two
from database.dbworker import States, get_parameter, set_state, update_results
from utils.misc.api_request import request_to_api
from utils.misc.reset import reset


def destination_id_handler(call: CallbackQuery, search_term: str) -> None:
    """
    Функция - обработчик Inline кнопок с районами города. Записывает в БД результат запроса к API.
    Также запрашивает у пользователя дату заезда в отель.
    """
    parameters = {"destinationId": str(call.data), "sortOrder": search_term, "currency": 'RUB', "locale": "ru_RU"}
    user_id = call.from_user.id
    hotels = dict()
    bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id, text='Ожидайте, идет обработка запроса.',
                          reply_markup=None)
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
        hotels = hotels["results"][:5]
        hotels_info = list()
        time = get_parameter(user_id, 'time')
        for i_hotel in hotels:
            hotel_id = i_hotel.get('id', 000000)
            hotel_name = i_hotel.get('name', '')
            address = translator_two.translate(f"{i_hotel.get('address', {}).get('streetAddress', '')},"
                                               f"{i_hotel.get('address', {}).get('locality', '')}, "
                                               f"{i_hotel.get('address', {}).get('countryName', '')}")
            distance = i_hotel.get('landmarks', [{}])[0].get('distance', '0 км')
            cost = str(i_hotel.get('ratePlan', {}).get('price', {}).get('exactCurrent', 0))
            hotel_url = 'https://www.hotels.com/ho' + str(i_hotel.get('id', 000000))

            hotels_info.append((user_id, time, hotel_id, hotel_name,
                                address, distance, cost, hotel_url))
        update_results(hotels_info)
        
            bot.send_message(chat_id=user_id,
                     text=f"Спасибо за ожидание. Выберите дату заезда.",
                     reply_markup=calendar)
            set_state(user_id, States.enter_arrival_date_state.value)

            
def hotels_founding(querystring: Dict[str, str]) -> dict:
    """Функция. Делает запрос к API в целях поиска отелей."""

    pattern = r'(?<=,)"results":.+?(?=,"pagination)'
    api_url = 'https://hotels4.p.rapidapi.com/properties/list'
    query_result = request_to_api(api_url, querystring, pattern)
    return query_result
