import asyncio
from aiogram import Bot, Dispatcher
from handlers import register_handlers
from scheduler import setup_scheduler
from database import init_db
import os

# Получение данных из переменных окружения
API_TOKEN = os.getenv('bot_token')

if not API_TOKEN:
    raise ValueError("Переменная окружения `bot_token` не задана.")

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

async def main():
    print("Бот запускается...")
    # Инициализация базы данных
    init_db()

    # Регистрация обработчиков
    register_handlers(dp)

    # Запуск планировщика
    setup_scheduler(bot)

    # Запуск бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
