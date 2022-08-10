from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup


def photo_markup() -> InlineKeyboardMarkup:
    """Клавиатура с вариантами ответа на вопрос о выдаче фото."""
    choice = InlineKeyboardMarkup()
    choice.add(InlineKeyboardButton(text='Да', callback_data='yes'))
    choice.add(InlineKeyboardButton(text='Нет', callback_data='no'))
    return choice
