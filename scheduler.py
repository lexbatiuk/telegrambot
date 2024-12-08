from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

def init_scheduler():
    scheduler.start()
    return scheduler

def schedule_daily_summary(user_id, channels):
    scheduler.add_job(
        fetch_and_send_summary,
        "interval",
        hours=24,
        args=[user_id, channels],
        id=f"summary_{user_id}",
        replace_existing=True
    )
