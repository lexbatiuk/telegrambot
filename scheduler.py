import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from database import delete_user_data
import sqlite3

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

async def clean_inactive_users(bot):
    """
    Checks for inactive users and deletes their data.
    """
    logger.info("Starting cleanup of inactive users...")
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT DISTINCT user_id FROM user_channels")
        users = cursor.fetchall()

        for user_id, in users:
            try:
                # Attempt to send a message to check if the user is active
                await bot.send_message(user_id, "Checking activity...")
                logger.info(f"User {user_id} is active.")
            except (TelegramForbiddenError, TelegramBadRequest):
                # Remove data if the user is inactive
                delete_user_data(user_id)
                logger.info(f"User {user_id} is no longer active. Data removed.")
    except Exception as e:
        logger.error(f"Error during cleanup of inactive users: {e}")
    finally:
        conn.close()

def setup_scheduler(bot):
    """
    Sets up the task scheduler.
    """
    scheduler.add_job(
        clean_inactive_users, 
        "interval", 
        hours=24, 
        args=[bot], 
        id="clean_inactive_users"
    )
    scheduler.start()
    logger.info("Task scheduler started.")

async def shutdown_scheduler():
    """
    Gracefully shuts down the scheduler.
    """
    scheduler.shutdown(wait=False)
    logger.info("Scheduler shutdown completed.")
