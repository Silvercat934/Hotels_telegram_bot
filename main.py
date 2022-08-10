from loguru import logger
from telebot.types import CallbackQuery, Message

from config_data.config import States, bot
from database.dbworker import get_current_state, get_parameter
from handlers.api_handlers.bestdeal_handlers import (
    bestdeal_destination_id_handler, distances_handler, prices_handler)
from handlers.api_handlers.city_handler import city_handler
from handlers.api_handlers.high_or_low_price import destination_id_handler
from handlers.api_handlers.photo_handler import photo_issuing_handler
from handlers.default_handlers.commands_handler import commands_handler
from handlers.default_handlers.dates_handlers import (arrival_date_handler,
                                                      departure_date_handler)
from handlers.default_handlers.echo import echo
from utils.misc.reset import reset

logger.add('logs/logs_{time}.log', level='DEBUG', format="{time} {level} {message}", rotation="06:00",
           compression="zip")
logger.debug('Error')
logger.info('Information message')
logger.warning('Warning')


@logger.catch()
@bot.callback_query_handler(func=lambda call: get_current_state(call.from_user.id) == States.enter_command_state.value)
def entering_command(call: CallbackQuery) -> None:
    commands_handler(call)


@logger.catch()
@bot.message_handler(func=lambda call: get_current_state(call.from_user.id) == States.enter_city_state.value)
def entering_city(message: Message) -> None:
    if message.text == '/reset':
        reset(message)
    else:
        bot.send_message(chat_id=message.from_user.id, text='Ожидайте...')
        city_handler(message)


@logger.catch()
@bot.callback_query_handler(func=lambda call: get_current_state(call.from_user.id) == States.choice_city_state.value)
def city_choice(call: CallbackQuery) -> None:
    command = get_parameter(call.from_user.id, 'command')
    if command == 'lowprice':
        search_term = 'PRICE_LOWEST_FIRST'
        destination_id_handler(call, search_term)
    elif command == 'highprice':
        search_term = 'PRICE_HIGHEST_FIRST'
        destination_id_handler(call, search_term)
    elif command == 'bestdeal':
        bestdeal_destination_id_handler(call)


@logger.catch()
@bot.callback_query_handler(func=lambda call: get_current_state(call.from_user.id) ==
                            States.enter_arrival_date_state.value)
def arrival_date_enter(call: CallbackQuery) -> None:
    arrival_date_handler(call)


@logger.catch()
@bot.callback_query_handler(func=lambda call: get_current_state(call.from_user.id) ==
                            States.enter_departure_date_state.value)
def departure_date_enter(call: CallbackQuery) -> None:
    departure_date_handler(call)


@logger.catch()
@bot.callback_query_handler(func=lambda call: get_current_state(call.from_user.id) ==
                            States.enter_distances_state.value)
def distances_choice(call: CallbackQuery) -> None:
    distances_handler(call)


@logger.catch()
@bot.callback_query_handler(func=lambda call: get_current_state(call.from_user.id) ==
                            States.enter_prices_state.value)
def prices_choice(call: CallbackQuery) -> None:
    prices_handler(call)


@logger.catch()
@bot.callback_query_handler(func=lambda call: get_current_state(call.from_user.id) ==
                            States.result_issuing_state.value)
def need_photo(call: CallbackQuery) -> None:
    photo_issuing_handler(call)


@logger.catch()
@bot.message_handler(content_types=['text'])
def start_message(message: Message) -> None:
    echo(message)


bot.polling(none_stop=True, interval=0)
