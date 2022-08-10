from typing import Dict, List

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from config_data.config import NoSuitableValueError
from utils.misc.api_request import request_to_api


def city_markup(user_message: str) -> InlineKeyboardMarkup:
    """Клавиатура с районами города."""
    parameters = {"query": user_message, "locale": "ru_RU"}
    cities = city_founding(parameters)

    if len(cities) == 0:
        raise NoSuitableValueError
    destinations = InlineKeyboardMarkup()
    for i_city in cities:
        destinations.add(InlineKeyboardButton(text=i_city.get('city_name'),
                                              callback_data=f"{i_city.get('destination_id')}"))
    return destinations


def city_founding(querystring: Dict[str, str]) -> List[dict]:
    """Функция. Делает запрос к API в целях поиска информации и городе."""

    api_url = 'https://hotels4.p.rapidapi.com/locations/v2/search'
    pattern = r'(?<="CITY_GROUP",).+?[\]]'

    suggestions = request_to_api(api_url, querystring, pattern)
    cities = [{'city_name': destination_id['name'], 'destination_id': destination_id['destinationId']}
              for destination_id in suggestions['entities']]
    return cities
