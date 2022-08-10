from telebot.types import Message
from telegram_bot_calendar import LSTEP

from config_data.config import States, bot, calendar, step
from database.dbworker import get_current_state, set_state
from keyboards.commands_inline import menu_markup
from keyboards.distance_range_inline import distances_markup
from keyboards.photo_request_inline import photo_markup
from keyboards.price_range_inline import prices_markup
from utils.misc.reset import reset


def echo(message: Message) -> None:
    """
    Функция - обработчик сообщений пользователя.
    """

    user_id = message.from_user.id
    state = get_current_state(user_id)
    if message.text.lower() == "привет" or "/hello-world" or "/start":
        bot.send_message(chat_id=user_id,
                         text=f'Добро пожаловать, вас приветствует бот '
                              f'туристического агентства TooEasyTravel!'
                              f'Я занимаюсь поиском отелей по заданным параметрам. '
                              f'Чем я могу вам помочь ?', reply_markup=menu_markup())
        set_state(user_id, States.enter_command_state.value)
    elif message.text == '/reset':
        reset(message)
    elif state == States.enter_command_state.value:
        bot.send_message(chat_id=user_id,
                         text=f'Вы еще не выбрали команду, выберите команду: ',
                         reply_markup=menu_markup())
    elif state == States.enter_city_state.value or States.choice_city_state.value:
        set_state(user_id, States.enter_city_state.value)
        bot.send_message(chat_id=user_id,
                         text='Вы еще не выбрали город. Введите название города')
    elif state == States.enter_arrival_date_state.value:
        bot.send_message(
            chat_id=user_id,
            text=f'Вы не выбрали дату заезда. Выберите дату.{LSTEP[step]}',
            reply_markup=calendar
        )
    elif state == States.enter_departure_date_state.value:
        bot.send_message(
            chat_id=user_id,
            text=f'Вы не выбрали дату выезда. Выберите дату.{LSTEP[step]}',
            reply_markup=calendar
        )
    elif state == States.enter_distances_state.value:
        bot.send_message(chat_id=user_id,
                         text='Вы еще не ввели диапазон расстояний, пожалуйста выберите.',
                         reply_markup=distances_markup())
    elif state == States.enter_prices_state.value:
        bot.send_message(chat_id=user_id,
                         text='Вы еще не ввели диапазон цен, пожалуйста выберите.',
                         reply_markup=prices_markup())
    elif state == States.photo_issuing_state.value:
        bot.send_message(chat_id=user_id,
                         text='Вы еще не указали необходимость выдачи фото, выдать фото ?',
                         reply_markup=photo_markup())
    else:
        bot.send_message(user_id, 'Я вас не понимаю. Для начала работы введите /start')
