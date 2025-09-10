import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.enums import ParseMode
from dotenv import load_dotenv
from os import getenv

load_dotenv()

BOT_TOKEN = getenv("BOT_TOKEN")
GROUP_ID = getenv("GROUP_ID")

# Инициализация
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# Фиксированный список объектов
LOCATIONS = [
    "Поклонногорская 13",
    "Успенская 6",
    "Первомайская 3",
    "Совхозная 15",
    "Центральная 7"
]

# Состояния FSM
class Form(StatesGroup):
    shift_action = State()
    photo = State()
    transfer = State()
    piecework = State()

# Главная клавиатура
def get_main_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="📸 Начать смену"))
    builder.add(types.KeyboardButton(text="🔚 Закончить смену"))
    builder.add(types.KeyboardButton(text="💰 Переход на сдельную"))
    builder.add(types.KeyboardButton(text="🚚 Перемещение бригады"))
    builder.adjust(2, 2)
    return builder.as_markup(resize_keyboard=True)

# Клавиатура с кнопкой Отмена
def get_cancel_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Отмена", callback_data="cancel_action")
    return builder.as_markup()

# Клавиатура выбора объекта
def get_locations_keyboard():
    builder = InlineKeyboardBuilder()
    for location in LOCATIONS:
        builder.button(text=location, callback_data=f"loc_{location}")
    builder.button(text="Другой объект", callback_data="loc_other")
    builder.button(text="❌ Отмена", callback_data="cancel_action")
    builder.adjust(1, 1, 1)
    return builder.as_markup()

# Обработка команды /start
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Здравствуйте! Это <b>тестовый бот</b> для передачи сведений о начале/окончании рабочей смены ДЛЯ БРИГАД ПОВРЕМЕННОЙ ОПЛАТЫ, перемещении на другой объект, переходе на другую форму оплаты.\n\n<b>Вся информация отправляется в тестовую группу: @brigadeControlTestBot",
        parse_mode=ParseMode.HTML,
        reply_markup=get_main_keyboard()
    )

# Глобальный обработчик отмены
@router.callback_query(F.data == "cancel_action")
async def handle_inline_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Действие отменено", reply_markup=get_main_keyboard())
    await callback.answer()

# Обработка начала/окончания смены
@router.message(F.text.in_(["📸 Начать смену", "🔚 Закончить смену"]))
async def handle_shift(message: Message, state: FSMContext):
    action_type = "start" if "Начать" in message.text else "end"
    await state.update_data(action_type=action_type)
    await state.set_state(Form.shift_action)
    await message.answer(
        "📍 Выберите объект:",
        reply_markup=get_locations_keyboard()
    )

# Обработчик выбора объекта
@router.callback_query(Form.shift_action, F.data.startswith("loc_"))
async def handle_location_selection(callback: CallbackQuery, state: FSMContext):
    data = callback.data.split("_", 1)[1]
    
    if data == "other":
        # Для "Другого объекта" сразу запрашиваем фото с подписью
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
        # Для выбранного объекта сохраняем и запрашиваем фото
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

# Обработчик фото
@router.message(Form.photo, F.photo)
async def handle_shift_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    action_type = data["action_type"]
    
    # Обработка кастомного объекта (название берем из подписи)
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
        
        # Сохраняем кастомный объект
        await state.update_data(location=location, expecting_custom_location=False)
    
    # Проверяем наличие объекта
    if "location" not in await state.get_data():
        await message.answer("❌ Ошибка: объект не определен. Попробуйте снова.")
        await state.clear()
        return
        
    # Формируем сообщение
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

    # Отправляем в группу
    await bot.send_photo(
        chat_id=GROUP_ID,
        photo=message.photo[-1].file_id,
        caption=caption,
        parse_mode=ParseMode.HTML
    )
    
    await state.clear()
    await message.answer("✅ Данные отправлены в группу!", reply_markup=get_main_keyboard())

# Обработка сдельной оплаты - ОДИН ШАГ
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

# Обработка данных для сдельной оплаты
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
    names = ', '.join(parts[2:])  # Объединяем все оставшиеся части как фамилии
    
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
    
    await bot.send_message(GROUP_ID, group_msg, parse_mode=ParseMode.HTML)
    await state.clear()
    await message.answer(
        "✅ Данные отправлены в группу!",
        reply_markup=get_main_keyboard()
    )

# Обработка перемещения бригады - ОДИН ШАГ
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

# Обработка данных для перемещения бригады
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
    new_location = ', '.join(parts[2:])  # Объединяем все оставшиеся части как новый объект
    
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
    
    await bot.send_message(GROUP_ID, group_msg, parse_mode=ParseMode.HTML)
    await state.clear()
    await message.answer(
        "✅ Данные отправлены в группу!",
        reply_markup=get_main_keyboard()
    )

# Запуск бота
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    dp.run_polling(bot)