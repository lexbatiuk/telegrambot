import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from database import delete_user_data, get_channels
import asyncpg
import os

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()

async def clean_inactive_users(bot):
    """
    Check for inactive users and delete their data.
    """
    try:
        conn = await asyncpg.connect(
            user=os.getenv("PGUSER"),
            password=os.getenv("PGPASSWORD"),
            database=os.getenv("PGDATABASE"),
            host=os.getenv("PGHOST"),
            port=os.getenv("PGPORT"),
        )
        users = await conn.fetch('SELECT user_id FROM user_channels')
        for user in users:
            user_id = user['user_id']
            try:
                await bot.send_message(user_id, "Checking activity...")
            except (TelegramForbiddenError, TelegramBadRequest):
                await delete_user_data(user_id)
                logger.info(f"Deleted data for inactive user {user_id}.")
        await conn.close()
    except Exception as e:
        logger.error(f"Error cleaning inactive users: {e}")

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
    logger.info("Scheduler started.")

async def shutdown_scheduler():
    """
    Gracefully shuts down the scheduler.
    """
    scheduler.shutdown(wait=False)
    logger.info("Scheduler stopped.")
