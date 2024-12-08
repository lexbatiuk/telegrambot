from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from telethon import TelegramClient
from database import get_user_channels
import os

API_ID = os.getenv('api_id')
API_HASH = os.getenv('api_hash')

client = TelegramClient('bot_session', API_ID, API_HASH)

async def fetch_messages(bot):
    async with client:
        for user_id, channels in get_all_user_channels():
            for channel in channels:
                try:
                    async for message in client.iter_messages(channel, limit=5):
                        await bot.send_message(user_id, f"Новое сообщение из {channel}: {message.text[:200]}")
                except Exception as e:
                    print(f"Ошибка с каналом {channel}: {e}")

def setup_scheduler(bot):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(fetch_messages, IntervalTrigger(hours=24), args=[bot])
    scheduler.start()

def get_all_user_channels():
    """Возвращает словарь {user_id: [каналы]}"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, channel FROM user_channels")
    data = {}
    for user_id, channel in cursor.fetchall():
        if user_id not in data:
            data[user_id] = []
        data[user_id].append(channel)
    conn.close()
    return data.items()
