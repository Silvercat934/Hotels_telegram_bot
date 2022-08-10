import datetime
import os
from enum import Enum

import telebot
from dotenv import load_dotenv
from telegram_bot_calendar import DetailedTelegramCalendar
from translate import Translator


class States(Enum):
    """
    Дочерний класс класса Enum. Состояния бота.
    """

    enter_command_state = 0
    enter_city_state = 1
    choice_city_state = 2
    enter_arrival_date_state = 3
    enter_departure_date_state = 4
    photo_issuing_state = 5
    result_issuing_state = 6
    enter_prices_state = 7
    enter_distances_state = 8


class NoSuitableValueError(Exception):
    """
    Дочерний класс класса Exception. Класс исключений.
    """
    def __init__(self, *args) -> None:
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self) -> str:
        if self.message:
            return f'NoSuitableValueError {self.message}'
        else:
            return 'NoSuitableValueError'


class MyCalendar(DetailedTelegramCalendar):
    """
    Дочерний класс класса DetailedTelegramCalendar. Кастомизированный календарь.
    """
    prev_button = "⬅️"
    next_button = "➡️"

    empty_month_button = ""
    empty_year_button = ""
    empty_day_button = ""


load_dotenv(os.path.abspath(os.path.join('.env')))
token = os.getenv('TOKEN')
api_key = os.getenv('API_KEY')
bot = telebot.TeleBot(token)

translator_one = Translator(from_lang="ru", to_lang="en")
translator_two = Translator(from_lang="en", to_lang="ru")

now = datetime.datetime.now()
db_file = 'database/users.db'

calendar, step = MyCalendar(locale='ru', min_date=datetime.date.today()).build()
