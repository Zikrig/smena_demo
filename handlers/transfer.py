from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from config import GROUP_ID
from states import Form
from keyboards import get_locations_keyboard, get_cancel_keyboard, get_main_inline_keyboard
from datetime import datetime

router = Router()

@router.callback_query(F.data == "move_team")
async def handle_transfer_prompt(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Form.transfer_current_location)
    await callback.message.edit_text(
        "📍 Выберите текущий объект:",
        reply_markup=get_locations_keyboard()
    )
    await callback.answer()

@router.callback_query(Form.transfer_current_location, F.data.startswith("loc_"))
async def handle_transfer_current_location(callback: CallbackQuery, state: FSMContext):
    data = callback.data.split("_", 1)[1]
    if data == "other":
        await state.set_state(Form.transfer_current)
        await callback.message.edit_text(
            "Введите название текущего объекта:",
            reply_markup=get_cancel_keyboard()
        )
    else:
        await state.update_data(current_location=data)
        await state.set_state(Form.transfer_new_location)
        await callback.message.edit_text(
            "📍 Выберите новый объект:",
            reply_markup=get_locations_keyboard()
        )
    await callback.answer()

@router.message(Form.transfer_current, F.text)
async def handle_transfer_current_custom(message: Message, state: FSMContext):
    if len(message.text) > 100:
        return await message.answer("❌ Название объекта слишком длинное. Максимум 100 символов.")
    
    await state.update_data(current_location=message.text)
    await state.set_state(Form.transfer_new_location)
    await message.answer(
        "📍 Выберите новый объект:",
        reply_markup=get_locations_keyboard()
    )

@router.callback_query(Form.transfer_new_location, F.data.startswith("loc_"))
async def handle_transfer_new_location(callback: CallbackQuery, state: FSMContext):
    data = callback.data.split("_", 1)[1]
    if data == "other":
        await state.set_state(Form.transfer_new)
        await callback.message.edit_text(
            "Введите название нового объекта:",
            reply_markup=get_cancel_keyboard()
        )
    else:
        await state.update_data(new_location=data)
        await state.set_state(Form.transfer_names)
        await callback.message.edit_text(
            "Введите фамилии сотрудников:",
            reply_markup=get_cancel_keyboard()
        )
    await callback.answer()

@router.message(Form.transfer_new, F.text)
async def handle_transfer_new_custom(message: Message, state: FSMContext):
    if len(message.text) > 100:
        return await message.answer("❌ Название объекта слишком длинное. Максимум 100 символов.")
    
    await state.update_data(new_location=message.text)
    await state.set_state(Form.transfer_names)
    await message.answer(
        "Введите фамилии сотрудников:",
        reply_markup=get_cancel_keyboard()
    )

@router.message(Form.transfer_names, F.text)
async def handle_transfer_names(message: Message, state: FSMContext):
    names = message.text
    data = await state.get_data()
    current_location = data['current_location']
    new_location = data['new_location']
    
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
        reply_markup=get_main_inline_keyboard()
    )