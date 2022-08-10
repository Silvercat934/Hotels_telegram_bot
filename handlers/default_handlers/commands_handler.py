from telebot.types import CallbackQuery

from config_data.config import bot
from handlers.default_handlers.history import history_issuing
from handlers.default_handlers.start import start
from keyboards.commands_inline import menu_markup
from utils.misc.reset import reset


def commands_handler(call: CallbackQuery) -> None:
    """
    Функция - обработчик Inline кнопок с выбором команды
    """
    user_id = call.from_user.id
    bot.edit_message_reply_markup(chat_id=user_id, message_id=call.message.message_id, reply_markup=None)

    if call.data == '/history':
        history_issuing(call)
    elif call.data == '/help':
        commands = "\n1. /lowprice - Узнать топ самых дешёвых отелей в городе " \
                   "\n2. /higprice - Узнать топ самых дорогих отелей в городе" \
                   "\n3. /bestdeal - Узнать топ отелей, наиболее подходящих по цене и расположению от центра" \
                   "(самые дешёвые и находятся ближе всего к центру)" \
                   "\n4. /history - Узнать историю поиска отелей" \
                   "\n5. /help - Информация по командам " \
                   "\n6. /help - Сброс"
        bot.send_message(chat_id=user_id, text=commands, reply_markup=menu_markup())
    elif call.data == '/lowprice' or '/highprice' or '/bestdeal':
        start(call)
    elif call.data == '/reset':
        reset(call)
