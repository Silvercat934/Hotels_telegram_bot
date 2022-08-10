from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def distances_markup() -> InlineKeyboardMarkup:
    """
    Клавиатура с вариантами диапазона расстояний.
    """
    distances = InlineKeyboardMarkup()
    distances.add(InlineKeyboardButton(text='0-15 километров', callback_data='0-15'))
    distances.add(InlineKeyboardButton(text='15-30 километров', callback_data='15-30'))
    distances.add(InlineKeyboardButton(text='30-45 километров', callback_data='30-45'))
    return distances
