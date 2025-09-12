from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from config import GROUP_ID
from states import Form
from keyboards import get_locations_keyboard, get_cancel_keyboard, get_main_inline_keyboard
from datetime import datetime

from aiogram import Router
router = Router()

@router.message(F.text.in_(["📸 Начать смену", "🔚 Закончить смену"]))
async def handle_shift(message: Message, state: FSMContext):
    action_type = "start" if "Начать" in message.text else "end"
    await state.update_data(action_type=action_type)
    await state.set_state(Form.shift_action)
    await message.answer(
        "📍 Выберите объект:",
        reply_markup=get_locations_keyboard()
    )

@router.callback_query(Form.shift_action, F.data.startswith("loc_"))
async def handle_location_selection(callback: CallbackQuery, state: FSMContext):
    data = callback.data.split("_", 1)[1]
    if data == "other":
        await state.update_data(expecting_custom_location=True)
        await state.set_state(Form.photo)
        await callback.message.answer(
            "📸 Чтобы указать объект:\n"
            "1. Нажмите «📎»\n"
            "2. Выберите «Сделать фото»\n"
            "3. Добавьте подпись с названием объекта\n"
            "4. Отправьте фото",
            reply_markup=get_cancel_keyboard()
        )
    else:
        await state.update_data(location=data)
        await state.set_state(Form.photo)
        await callback.message.answer(
            "📸 Для подтверждения:\n"
            "1. Нажмите «📎»\n"
            "2. Выберите «Сделать фото»\n"
            "3. Добавьте подпись с названием объекта\n"
            "4. Отправьте фото",
            reply_markup=get_cancel_keyboard()
        )
    await callback.answer()

@router.message(Form.photo, F.photo)
async def handle_shift_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    action_type = data["action_type"]
    if data.get("expecting_custom_location"):
        if not message.caption:
            await message.answer(
                "❌ Вы не указали объект в подписи к фото!\n\n"
                "📸 Повторите отправку:\n"
                "1. Нажмите «📎»\n"
                "2. Выберите «Сделать фото»\n"
                "3. Добавьте подпись с названием объекта\n"
                "4. Отправьте фото"
            )
            return
        location = message.caption.strip()
        if len(location) > 100:
            await message.answer(
                "❌ Название объекта слишком длинное. Максимум 100 символов.\n\n"
                "📸 Повторите отправку:\n"
                "1. Нажмите «📎»\n"
                "2. Выберите «Сделать фото»\n"
                "3. Добавьте подпись с названием объекта\n"
                "4. Отправьте фото"
            )
            return
        await state.update_data(location=location, expecting_custom_location=False)
    if "location" not in await state.get_data():
        await message.answer("❌ Ошибка: объект не определен. Попробуйте снова.")
        await state.clear()
        return
    location = (await state.get_data())["location"]
    current_time = datetime.now().strftime("%H:%M")
    action_text = "Начало смены" if action_type == "start" else "Окончание смены"
    emoji = "📸" if action_type == "start" else "🔚"
    caption = (
        f"{emoji} <b>{action_text}</b>\n"
        f"📍 Объект: {location}\n"
        f"⏰ Время: {current_time}\n"
        f"🧍 Фото бригады: [прикреплено]"
    )
    await message.bot.send_photo(
        chat_id=GROUP_ID,
        photo=message.photo[-1].file_id,
        caption=caption,
        parse_mode=ParseMode.HTML
    )
    await state.clear()
    await message.answer("✅ Данные отправлены в группу!", reply_markup=get_main_inline_keyboard())
