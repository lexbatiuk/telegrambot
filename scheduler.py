from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database import delete_user_data, get_channels
import logging

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()

async def clean_inactive_users():
    """
    Cleans up data for inactive users.
    """
    logger.info("Cleaning up inactive users...")
    channels = await get_channels()
    for channel in channels:
        # Add logic to determine inactive users
        user_id = channel["user_id"]
        try:
            # Here you can check user activity with bot or another service
            logger.info(f"User {user_id} is active.")
        except Exception:
            # If the user is inactive, clean up their data
            await delete_user_data(user_id)
            logger.info(f"User {user_id} data deleted.")

def setup_scheduler():
    """
    Sets up the scheduler.
    """
    scheduler.add_job(clean_inactive_users, "interval", hours=24, id="cleanup_task")
    scheduler.start()
    logger.info("Scheduler started.")

async def shutdown_scheduler():
    """
    Gracefully shuts down the scheduler.
    """
    scheduler.shutdown(wait=False)
    logger.info("Scheduler stopped.")
