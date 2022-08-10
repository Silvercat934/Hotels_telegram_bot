from telebot.types import Message

from config_data.config import NoSuitableValueError, bot
from database.dbworker import States, set_state
from keyboards.choise_cities_inline import city_markup
from utils.misc.reset import reset


def city_handler(message: Message) -> None:
    """
    Функция - обработчик сообщений от пользователя с названием города.
    """
    user_id = message.from_user.id
    try:
        bot.send_message(chat_id=user_id, text='Уточните, пожалуйста:',
                         reply_markup=city_markup(message.text))
        set_state(user_id, States.choice_city_state.value)
    except NoSuitableValueError:
        bot.send_message(chat_id=user_id, text='По вашему запросу ничего не найдено. '
                                               'Пожалуйста, измените параметры поиска')
        reset(message)
