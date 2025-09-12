from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from config import LOCATIONS

def get_main_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="📸 Начать смену"))
    builder.add(types.KeyboardButton(text="🔚 Закончить смену"))
    # builder.add(types.KeyboardButton(text="💰 Переход на сдельную"))
    builder.add(types.KeyboardButton(text="🚚 Перемещение бригады"))
    builder.adjust(2, 1)
    return builder.as_markup(resize_keyboard=True)

def get_cancel_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Отмена", callback_data="cancel_action")
    return builder.as_markup()

def get_locations_keyboard():
    builder = InlineKeyboardBuilder()
    for location in LOCATIONS:
        builder.button(text=location, callback_data=f"loc_{location}")
    builder.button(text="Другой объект", callback_data="loc_other")
    builder.button(text="❌ Отмена", callback_data="cancel_action")
    builder.adjust(1, 1, 1)
    return builder.as_markup()
