from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from config import GROUP_ID
from states import Form
from keyboards import get_cancel_keyboard, get_main_keyboard
from datetime import datetime

router = Router()

@router.message(F.text == "💰 Переход на сдельную")
async def handle_piecework_prompt(message: Message, state: FSMContext):
    await state.set_state(Form.piecework)
    await message.answer(
        "✍️ Введите данные в формате:\n"
        "<b>Объект, Наименование работы, Фамилии сотрудников</b>\n\n"
        "Пример: <code>Успенская 6, Установка плинтусов в квартире 34, Раджабов Усмонов</code>",
        parse_mode=ParseMode.HTML,
        reply_markup=get_cancel_keyboard()
    )

@router.message(Form.piecework, F.text)
async def handle_piecework_data(message: Message, state: FSMContext):
    parts = [part.strip() for part in message.text.split(',')]
    if len(parts) < 3:
        await message.answer(
            "❌ Неверный формат данных. Пожалуйста, введите данные в формате:\n"
            "<b>Объект, Наименование работы, Фамилии сотрудников</b>\n\n"
            "Пример: <code>Успенская 6, Установка плинтусов в квартире 34, Раджабов Усмонов</code>",
            parse_mode=ParseMode.HTML
        )
        return
    location = parts[0]
    work = parts[1]
    names = ', '.join(parts[2:])
    if len(location) > 100:
        return await message.answer("❌ Название объекта слишком длинное. Максимум 100 символов.")
    if len(work) > 200:
        return await message.answer("❌ Наименование работы слишком длинное. Максимум 200 символов.")
    current_time = datetime.now().strftime("%H:%M")
    group_msg = (
        f"🔀 <b>Переход на сдельную:</b>\n"
        f"⏰ Время: {current_time}\n"
        f"📍 Объект: {location}\n"
        f"📝 Работа: {work}\n"
        f"🧍 Сотрудники: {names}"
    )
    await message.bot.send_message(GROUP_ID, group_msg, parse_mode=ParseMode.HTML)
    await state.clear()
    await message.answer(
        "✅ Данные отправлены в группу!",
        reply_markup=get_main_keyboard()
    )
