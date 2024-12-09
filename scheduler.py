import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from database import delete_user_data
import sqlite3

logger = logging.getLogger(__name__)

# Инициализация планировщика задач
scheduler = AsyncIOScheduler()

async def clean_inactive_users(bot):
    """
    Проверяет активность пользователей и удаляет данные неактивных пользователей.
    """
    logger.info("Начата очистка неактивных пользователей...")
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    try:
        # Получение списка пользователей
        cursor.execute("SELECT DISTINCT user_id FROM user_channels")
        users = cursor.fetchall()

        for user_id, in users:
            try:
                # Попытка отправить сообщение пользователю для проверки активности
                await bot.send_message(user_id, "Activity check: verifying your account is active.")
                logger.info(f"User {user_id} is active.")
            except (TelegramForbiddenError, TelegramBadRequest):
                # Удаление данных, если пользователь недоступен
                delete_user_data(user_id)
                logger.info(f"User {user_id} is inactive. Their data has been removed.")
    except Exception as e:
        logger.error(f"Error during cleanup of inactive users: {e}")
    finally:
        conn.close()

def setup_scheduler(bot):
    """
    Настраивает планировщик задач и добавляет регулярные задачи.
    """
    scheduler.add_job(
        clean_inactive_users,
        "interval",
        hours=24,  # Выполнять задачу раз в 24 часа
        args=[bot],
        id="clean_inactive_users"
    )
    scheduler.start()
    logger.info("Планировщик задач запущен.")

async def shutdown_scheduler():
    """
    Безопасное завершение работы планировщика задач.
    """
    scheduler.shutdown(wait=False)
    logger.info("Планировщик задач успешно завершён.")

def reschedule_jobs():
    """
    Переустанавливает задачи при перезапуске планировщика.
    """
    jobs = scheduler.get_jobs()
    if jobs:
        logger.info("Rescheduling existing jobs...")
        for job in jobs:
            scheduler.add_job(job.func, job.trigger, args=job.args, id=job.id)
