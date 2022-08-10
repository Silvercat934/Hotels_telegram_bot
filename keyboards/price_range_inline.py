from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def prices_markup() -> InlineKeyboardMarkup:
    """
    Клавиатура с вариантами диапазона расстояний.
    """
    prices = InlineKeyboardMarkup()
    prices.add(InlineKeyboardButton(text='0-10000 RUB', callback_data='0-10000'))
    prices.add(InlineKeyboardButton(text='10000-25000 RUB', callback_data='10000-25000'))
    prices.add(InlineKeyboardButton(text='25000-50000 RUB', callback_data='25000-50000'))
    prices.add(InlineKeyboardButton(text='50000-100000 RUB', callback_data='50000-100000'))
    return prices
