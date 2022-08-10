import datetime

from telebot.types import CallbackQuery
from telegram_bot_calendar import LSTEP

from config_data.config import MyCalendar, bot, calendar, translator_two
from database.dbworker import (States, get_parameter, set_state,
                               update_parameter)
from keyboards.distance_range_inline import distances_markup
from keyboards.photo_request_inline import photo_markup


def arrival_date_handler(call: CallbackQuery) -> None:
    """
    Функция - обработчик календаря. Также запрашивает у пользователя дату выезда из отеля.
    """

    user_id = call.from_user.id
    result, key, step = MyCalendar(locale='ru', min_date=datetime.date.today()).process(call.data)
    if not result and key:
        bot.edit_message_text(f"Выберите {translator_two.translate(LSTEP[step])}",
                              user_id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        update_parameter(user_id, 'date_from', "'" + str(result) + "'")
        bot.edit_message_reply_markup(chat_id=user_id, message_id=call.message.message_id, reply_markup=None)
        bot.send_message(chat_id=user_id,
                         text=f'Выберите дату выезда',
                         reply_markup=calendar)
        set_state(user_id, States.enter_departure_date_state.value)


def departure_date_handler(call: CallbackQuery) -> None:
    """
    Функция - обработчик календаря. Также запрашивает у пользователя диапазон расстояний
    или уточняет необходимость выдать фото в зависимости от выбранной команды.
    """

    user_id = call.from_user.id
    result, key, step = MyCalendar(locale='ru', min_date=datetime.date.today()).process(call.data)
    if not result and key:
        bot.edit_message_text(f"Выберите {translator_two.translate(LSTEP[step])}",
                              user_id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_reply_markup(chat_id=user_id, message_id=call.message.message_id, reply_markup=None)
        day_from = (get_parameter(user_id, 'date_from').split('-'))[2]
        day_to = (str(result).split('-'))[2]
        if day_to < day_from:
            bot.send_message(chat_id=user_id,
                             text='Выбрана некорректная дата, выберите дату позже даты заезда.',
                             reply_markup=calendar)
        elif get_parameter(user_id, 'command') == 'bestdeal':
            update_parameter(user_id, 'date_to', "'" + str(result) + "'")
            bot.send_message(chat_id=user_id,
                             text='Укажите необходимый диапазон расстояний от центра.',
                             reply_markup=distances_markup())
            set_state(user_id, States.enter_distances_state.value)
        else:
            update_parameter(call.from_user.id, 'date_to', "'" + str(result) + "'")
            bot.send_message(chat_id=user_id,
                             text='Необходимо выдать фото? ',
                             reply_markup=photo_markup())
            set_state(user_id, States.result_issuing_state.value)
