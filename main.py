import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers import start, shift, piecework, transfer

# Инициализация
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Подключение роутеров
for router in (start.router, shift.router, piecework.router, transfer.router):
    dp.include_router(router)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    dp.run_polling(bot)