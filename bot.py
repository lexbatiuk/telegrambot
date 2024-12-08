import logging
import asyncio
from aiogram import Bot, Dispatcher
from handlers import register_handlers
from scheduler import setup_scheduler
from database import init_db
import os

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Получение данных из переменных окружения
API_TOKEN = os.getenv('bot_token')

if not API_TOKEN:
    logger.critical("Переменная окружения `bot_token` не задана. Завершаем выполнение.")
    raise ValueError("Переменная окружения `bot_token` не задана.")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

async def main():
    logger.info("Запуск бота...")
    # Инициализация базы данных
    init_db()
    logger.info("База данных инициализирована.")

    # Регистрация обработчиков
    register_handlers(dp)
    logger.info("Обработчики зарегистрированы.")

    # Запуск планировщика
    setup_scheduler(bot)
    logger.info("Планировщик запущен.")

    # Запуск бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.exception(f"Критическая ошибка: {e}")
