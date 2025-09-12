from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from config import GROUP_ID
from keyboards import get_main_keyboard, get_cancel_keyboard
from aiogram.enums import ParseMode

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Здравствуйте! Это <b>тестовый бот</b> для передачи сведений о начале/окончании рабочей смены ДЛЯ БРИГАД ПОВРЕМЕННОЙ ОПЛАТЫ, перемещении на другой объект, переходе на другую форму оплаты.\n\n<b>Вся информация отправляется в тестовую группу:</b> @brigadControl\n\nЗакажите подобного бота у меня @fgriz, я буду рад разработать бота специально под ваши потребности.",
        parse_mode=ParseMode.HTML,
        reply_markup=get_main_keyboard()
    )

@router.callback_query(F.data == "cancel_action")
async def handle_inline_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Действие отменено", reply_markup=get_main_keyboard())
    await callback.answer()

@router.message(F.text == "🔴 Кружочек")
async def handle_round(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Отправьте кружочек (видео-сообщение) через кнопку внизу справа.", reply_markup=get_cancel_keyboard())

@router.message(F.content_type.in_(["video_note"]))
async def handle_video_note(message: Message, state: FSMContext):
    await message.bot.send_video_note(chat_id=GROUP_ID, video_note=message.video_note.file_id)
    await state.clear()
    await message.answer("✅ Кружочек отправлен в группу!", reply_markup=get_main_keyboard())

@router.message(F.content_type == "location")
async def handle_location(message: Message, state: FSMContext):
    lat = message.location.latitude
    lon = message.location.longitude
    await message.bot.send_message(GROUP_ID, f"📍 Геолокация: {lat}, {lon}")
    await state.clear()
    await message.answer("✅ Геолокация отправлена в группу!", reply_markup=get_main_keyboard())
