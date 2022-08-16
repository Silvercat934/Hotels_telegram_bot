from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def menu_markup() -> InlineKeyboardMarkup:
    """
    Клавиатура с пользовательскими командами.
    """
    menu = InlineKeyboardMarkup()
    menu.add(InlineKeyboardButton(text='Топ-5 дешевых отелей в городе', callback_data='/lowprice'))
    menu.add(InlineKeyboardButton(text='Топ-5 дорогих отелей в городе', callback_data='/highprice'))
    menu.add(InlineKeyboardButton(text='Топ-5 наиболее подходящих по цене, расстоянию', callback_data='/bestdeal'))
    menu.add(InlineKeyboardButton(text='История поиска', callback_data='/history'))
    menu.add(InlineKeyboardButton(text='Помощь', callback_data='/help'))
    return menu
