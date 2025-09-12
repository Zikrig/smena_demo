from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from config import LOCATIONS

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

def get_main_inline_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="📸 Начать смену", callback_data="start_shift")
    builder.button(text="🔚 Закончить смену", callback_data="end_shift")
    builder.button(text="🚚 Перемещение бригады", callback_data="move_team")
    builder.button(text="📍 Геолокация", callback_data="send_location")
    builder.button(text="🔴 Кружочек", callback_data="send_round")
    builder.adjust(2, 1, 2)
    return builder.as_markup()

def get_cancel_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Отмена", callback_data="cancel_action")
    return builder.as_markup()

def get_confirm_keyboard(action):
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Отправить", callback_data=action)
    builder.button(text="❌ Отмена", callback_data="cancel_action")
    builder.adjust(2)
    return builder.as_markup()