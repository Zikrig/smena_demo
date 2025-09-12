from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from config import GROUP_ID
from keyboards import get_main_inline_keyboard, get_cancel_keyboard, get_confirm_keyboard, get_geo_confirm_keyboard, get_locations_keyboard
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
    await callback.message.edit_text("Вы выбрали: Начать смену", reply_markup=get_main_inline_keyboard())
    await callback.answer()

@router.callback_query(F.data == "end_shift")
async def handle_end_shift(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Вы выбрали: Закончить смену", reply_markup=get_main_inline_keyboard())
    await callback.answer()

@router.callback_query(F.data == "move_team")
async def handle_move_team(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Вы выбрали: Перемещение бригады", reply_markup=get_main_inline_keyboard())
    await callback.answer()

@router.callback_query(F.data == "send_location")
async def ask_location(callback: CallbackQuery, state: FSMContext):
    await state.set_state("waiting_location")
    await callback.message.edit_text(
        "Пожалуйста, отправьте свою геолокацию через вложение (скрепка) или кнопку ниже.",
        reply_markup=get_geo_confirm_keyboard()
    )
    await callback.answer()

@router.message(F.content_type == "location")
async def handle_location(message: Message, state: FSMContext):
    if await state.get_state() == "waiting_location":
        await state.update_data(location_message_id=message.message_id)
        await message.answer(
            "Готово к отправке. Нажмите 'Отправить геолокацию' ниже.",
            reply_markup=get_geo_confirm_keyboard()
        )

@router.callback_query(F.data == "confirm_location")
async def confirm_location(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    location_message_id = data.get("location_message_id")
    if location_message_id:
        await callback.bot.forward_message(chat_id=GROUP_ID, from_chat_id=callback.from_user.id, message_id=location_message_id)
        await state.clear()
        await callback.message.edit_text("✅ Геолокация отправлена в группу!", reply_markup=get_main_inline_keyboard())
    await callback.answer()

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