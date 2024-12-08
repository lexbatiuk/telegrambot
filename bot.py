import asyncio
from aiogram import Bot, Dispatcher
from database import init_db
from handlers import setup_handlers
from scheduler import init_scheduler
import os

API_TOKEN = os.getenv('bot_token')

if not API_TOKEN:
    raise ValueError("Токен бота не задан.")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

async def main():
    init_db()  # Инициализация базы данных
    setup_handlers(dp)  # Регистрация обработчиков
    scheduler = init_scheduler()  # Настройка планировщика задач

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
