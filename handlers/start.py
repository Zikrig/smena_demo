from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from keyboards import get_main_keyboard
from aiogram.enums import ParseMode

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Здравствуйте! Это <b>тестовый бот</b> для передачи сведений о начале/окончании рабочей смены ДЛЯ БРИГАД ПОВРЕМЕННОЙ ОПЛАТЫ, перемещении на другой объект, переходе на другую форму оплаты.\n\n<b>Вся информация отправляется в тестовую группу:</b> @brigadeControlTestBot\n\nЗакажите подобного бота у меня @fgriz, я буду рад разработать бота специально под ваши потребности.",
        parse_mode=ParseMode.HTML,
        reply_markup=get_main_keyboard()
    )

@router.callback_query(F.data == "cancel_action")
async def handle_inline_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Действие отменено", reply_markup=get_main_keyboard())
    await callback.answer()
