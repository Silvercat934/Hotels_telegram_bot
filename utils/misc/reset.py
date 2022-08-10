import time
from typing import Union

from telebot.types import CallbackQuery, Message

from config_data.config import States, bot
from database.dbworker import set_state
from keyboards.commands_inline import menu_markup


def reset(message: Union[Message, CallbackQuery]) -> None:
    """
    Функция. Возвращает бота к исходному состоянию с выбором команды.
    """
    user_id = message.from_user.id
    time.sleep(3)
    set_state(user_id, States.enter_command_state.value)
    bot.send_message(chat_id=user_id,
                     text=f'Добро пожаловать, выберите команду: ', reply_markup=menu_markup())
