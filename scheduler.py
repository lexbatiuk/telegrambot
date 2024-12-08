import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from database import delete_user_data
import sqlite3

logger = logging.getLogger(__name__)

async def clean_inactive_users(bot):
    """
    Проверяет пользователей на активность и удаляет данные неактивных пользователей.
    """
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT DISTINCT user_id FROM user_channels")
        users = cursor.fetchall()

        for user_id, in users:
            try:
                await bot.send_message(user_id, "Проверка активности...")
            except (TelegramForbiddenError, TelegramBadRequest):
                delete_user_data(user_id)
                logger.info(f"Пользователь {user_id} больше не активен. Данные удалены.")
    finally:
        conn.close()

def setup_scheduler(bot):
    """
    Настройка планировщика задач.
    """
    scheduler = AsyncIOScheduler()
    scheduler.add_job(clean_inactive_users, "interval", hours=24, args=[bot])  # Запускать раз в 24 часа
    scheduler.start()
    logger.info("Планировщик задач запущен.")
