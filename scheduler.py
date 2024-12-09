from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database import delete_user_data

scheduler = AsyncIOScheduler()

async def clean_inactive_users():
    # Your logic to clean inactive users
    pass

def setup_scheduler(bot):
    scheduler.add_job(clean_inactive_users, "interval", hours=24)
    scheduler.start()

async def shutdown_scheduler():
    scheduler.shutdown(wait=False)
