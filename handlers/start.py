from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from config import GROUP_ID
from states import Form
from keyboards import get_main_inline_keyboard, get_cancel_keyboard, get_confirm_keyboard, get_locations_keyboard
from aiogram.enums import ParseMode

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Здравствуйте! Это <b>тестовый бот</b> для передачи сведений о начале/окончании рабочей смены ДЛЯ БРИГАД ПОВРЕМЕННОЙ ОПЛАТЫ, перемещении на другой объект, переходе на другую форму оплаты.\n\n<b>Вся информация отправляется в тестовую группу:</b> @brigadControl\n\nЗакажите подобного бота у меня @fgriz, я буду рад разработать бота специально под ваши потребности.",
        parse_mode=ParseMode.HTML,
        reply_markup=get_main_inline_keyboard()
    )

@router.callback_query(F.data == "cancel_action")
async def handle_inline_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Действие отменено", reply_markup=get_main_inline_keyboard())
    await callback.answer()

@router.callback_query(F.data == "start_shift")
async def handle_start_shift(callback: CallbackQuery, state: FSMContext):
    await state.update_data(action_type="start")
    await state.set_state(Form.shift_action)
    await callback.message.edit_text(
        "📍 Выберите объект:",
        reply_markup=get_locations_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "end_shift")
async def handle_end_shift(callback: CallbackQuery, state: FSMContext):
    await state.update_data(action_type="end")
    await state.set_state(Form.shift_action)
    await callback.message.edit_text(
        "📍 Выберите объект:",
        reply_markup=get_locations_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "move_team")
async def handle_move_team(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Form.transfer_current_location)
    await callback.message.edit_text(
        "📍 Выберите текущий объект:",
        reply_markup=get_locations_keyboard()
    )
    await callback.answer()
    
@router.callback_query(F.data == "piecework")
async def handle_piecework(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Form.piecework)
    await callback.message.edit_text(
        "✍️ Введите данные в формате:\n"
        "<b>Объект, Наименование работы, Фамилии сотрудников</b>\n\n"
        "Пример: <code>Успенская 6, Установка плинтусов в квартире 34, Раджабов Усмонов</code>",
        parse_mode=ParseMode.HTML,
        reply_markup=get_cancel_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "send_location")
async def ask_location(callback: CallbackQuery, state: FSMContext):
    location_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Отправить геолокацию", request_location=True)],
            [KeyboardButton(text="❌ Отмена")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    # Отправляем новое сообщение с реплай-клавиатурой вместо редактирования старого
    await callback.message.answer(
        "Нажмите кнопку ниже чтобы отправить геолокацию:",
        reply_markup=location_keyboard
    )
    await state.set_state("waiting_location")
    await callback.answer()

@router.message(F.content_type == "location")
async def handle_location(message: Message, state: FSMContext):
    if await state.get_state() == "waiting_location":
        await message.bot.send_location(
            chat_id=GROUP_ID,
            latitude=message.location.latitude,
            longitude=message.location.longitude
        )
        await message.answer(
            "✅ Геолокация отправлена в группу!",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.clear()
        await message.answer(
            "Выберите действие:",
            reply_markup=get_main_inline_keyboard()
        )

@router.message(F.text == "❌ Отмена")
async def handle_cancel(message: Message, state: FSMContext):
    if await state.get_state() == "waiting_location":
        await message.answer(
            "❌ Отменено",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.clear()
        await message.answer(
            "Выберите действие:",
            reply_markup=get_main_inline_keyboard()
        )
        
@router.callback_query(F.data == "send_round")
async def ask_round(callback: CallbackQuery, state: FSMContext):
    await state.set_state("waiting_round")
    await callback.message.edit_text(
        "Отправьте кружочек (видео-сообщение) через кнопку внизу справа.",
        reply_markup=get_cancel_keyboard()
    )
    await callback.answer()

@router.message(F.content_type.in_(["video_note"]))
async def handle_video_note(message: Message, state: FSMContext):
    if await state.get_state() == "waiting_round":
        await state.update_data(video_message_id=message.message_id)
        await message.answer(
            "Отправить этот кружочек в группу?",
            reply_markup=get_confirm_keyboard("confirm_round")
        )

@router.callback_query(F.data == "confirm_round")
async def confirm_round(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    video_message_id = data.get("video_message_id")
    if video_message_id:
        await callback.bot.forward_message(chat_id=GROUP_ID, from_chat_id=callback.from_user.id, message_id=video_message_id)
        await state.clear()
        await callback.message.edit_text("✅ Кружочек отправлен в группу!", reply_markup=get_main_inline_keyboard())
    await callback.answer()