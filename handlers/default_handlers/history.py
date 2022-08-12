from sqlite3 import OperationalError

from telebot.types import CallbackQuery

from config_data.config import bot
from database.dbworker import get_history
from utils.misc.reset import reset


def history_issuing(call: CallbackQuery) -> None:
    """
    Функция. Формирует историю поиска отелей.
    """
    user_id = call.from_user.id
    bot.send_message(chat_id=user_id,
                     text='Ожидайте, идет обработка запроса.')
    try:
        history = get_history(call.from_user.id)
        hotel_num = 0
        time, hotels, command, command_result = ['' for _ in range(4)]

        for i_hotel in history:
            if i_hotel['time'] == time:
                hotels += f"\n{hotel_num}. {i_hotel['hotel_name']}" \
                          f"\n{i_hotel['address']}" \
                          f"\n{i_hotel['hotel_url']}"
            elif hotel_num == 0:
                hotel_num = 1
                command, time = i_hotel['command'], i_hotel['time']
                hotels = f"\n{hotel_num}. {i_hotel['hotel_name']}" \
                         f"\n{i_hotel['address']}" \
                         f"\n{i_hotel['hotel_url']}"
            else:
                command_result = f"\n\nКоманда: {command}" \
                                 f"\nВремя вызова: {time}" \
                                 f"\nРезультат выполнения: \n{hotels}"
                bot.send_message(user_id, command_result, disable_web_page_preview=True)

                hotel_num = 1
                command, time = i_hotel['command'], i_hotel['time']
                hotels = f"\n{hotel_num}. {i_hotel['hotel_name']}" \
                         f"\n{i_hotel['address']}" \
                         f"\n{i_hotel['hotel_url']}"
            hotel_num += 1
        command_result = f"\n\nКоманда: {command}" \
                         f"\nВремя вызова: {time}" \
                         f"\nРезультат выполнения: \n{hotels}"

        bot.send_message(chat_id=user_id,
                         text=command_result,
                         disable_web_page_preview=True)

        bot.send_message(chat_id=user_id,
                         text='Спасибо за использование нашего бота. Всего доброго.')
        reset(call)
    except OperationalError:
        bot.send_message(chat_id=user_id,
                         text='История пуста. Для отображения истории вам необходимо произвести поиск отелей.')
        reset(call)
