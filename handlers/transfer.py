from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from config import GROUP_ID
from states import Form
from keyboards import get_cancel_keyboard, get_main_keyboard
from datetime import datetime

router = Router()

@router.message(F.text == "🚚 Перемещение бригады")
async def handle_transfer_prompt(message: Message, state: FSMContext):
    await state.set_state(Form.transfer)
    await message.answer(
        "✍️ Введите данные в формате:\n"
        "<b>Текущий объект, Фамилии сотрудников, Новый объект</b>\n\n"
        "Пример: <code>Поклонногорская 13, Усмонов Раджабов, Успенская 6</code>",
        parse_mode=ParseMode.HTML,
        reply_markup=get_cancel_keyboard()
    )

@router.message(Form.transfer, F.text)
async def handle_transfer_data(message: Message, state: FSMContext):
    parts = [part.strip() for part in message.text.split(',')]
    if len(parts) < 3:
        await message.answer(
            "❌ Неверный формат данных. Пожалуйста, введите данные в формате:\n"
            "<b>Текущий объект, Фамилии сотрудников, Новый объект</b>\n\n"
            "Пример: <code>Поклонногорская 13, Усмонов Раджабов, Успенская 6</code>",
            parse_mode=ParseMode.HTML
        )
        return
    current_location = parts[0]
    names = parts[1]
    new_location = ', '.join(parts[2:])
    if len(current_location) > 100:
        return await message.answer("❌ Название текущего объекта слишком длинное. Максимум 100 символов.")
    if len(new_location) > 100:
        return await message.answer("❌ Название нового объекта слишком длинное. Максимум 100 символов.")
    current_time = datetime.now().strftime("%H:%M")
    group_msg = (
        f"🔄 <b>Перевод между объектами:</b>\n"
        f"⏰ Время: {current_time}\n"
        f"📍 Текущий объект: {current_location}\n"
        f"🧍 Сотрудники: {names}\n"
        f"🚐 Перемещение на объект: {new_location}"
    )
    await message.bot.send_message(GROUP_ID, group_msg, parse_mode=ParseMode.HTML)
    await state.clear()
    await message.answer(
        "✅ Данные отправлены в группу!",
        reply_markup=get_main_keyboard()
    )
