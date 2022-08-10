from datetime import datetime

from telebot.types import CallbackQuery

from config_data.config import bot
from database.dbworker import States, add_note, set_state


def start(call: CallbackQuery) -> None:
    """
    Функция. Запрашивает у пользователя название города и делает новую запись в БД
    """
    user_id = call.from_user.id
    bot.send_message(chat_id=user_id, text='В каком городе ищем ?(Ввод осуществляется на русском языке)')
    add_note(user_id, call.data[1:], "'" + str(datetime.now()) + "'")
    set_state(user_id, States.enter_city_state.value)
