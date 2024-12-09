import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from database import delete_user_data
import sqlite3

logger = logging.getLogger(__name__)

async def clean_inactive_users(bot):
    """
    Checks for inactive users and deletes their data.
    """
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT DISTINCT user_id FROM user_channels")
        users = cursor.fetchall()

        for user_id, in users:
            try:
                await bot.send_message(user_id, "Checking activity...")
            except (TelegramForbiddenError, TelegramBadRequest):
                delete_user_data(user_id)
                logger.info(f"User {user_id} is no longer active. Data removed.")
    finally:
        conn.close()

def setup_scheduler(bot):
    """
    Sets up the task scheduler.
    """
    scheduler = AsyncIOScheduler()
    scheduler.add_job(clean_inactive_users, "interval", hours=24, args=[bot])  # Runs every 24 hours
    scheduler.start()
    logger.info("Task scheduler started.")
