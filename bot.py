from apscheduler.schedulers.asyncio import AsyncIOScheduler
from handlers import register_handlers
from database import init_db
from aiogram import Bot, Dispatcher
import logging
import asyncio
import os
from handlers import clean_inactive_users

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_TOKEN = os.getenv('bot_token')

if not API_TOKEN:
    logger.critical("Переменная окружения `bot_token` не задана.")
    raise ValueError("Переменная окружения `bot_token` не задана.")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

def setup_cleanup_task(bot):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(clean_inactive_users, "interval", hours=24, args=[bot])
    scheduler.start()
    logger.info("Планировщик очистки данных запущен.")

async def main():
    logger.info("Запуск бота...")
    init_db()
    register_handlers(dp)
    setup_cleanup_task(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
