import logging
import asyncio
from aiogram import Bot, Dispatcher
from handlers import register_handlers
from scheduler import setup_scheduler
from database import init_db
from telethon.sync import TelegramClient
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Telegram API credentials
API_TOKEN = os.getenv('bot_token')
API_ID = os.getenv('api_id')
API_HASH = os.getenv('api_hash')

if not API_TOKEN or not API_ID or not API_HASH:
    logger.critical("Environment variables `bot_token`, `api_id`, or `api_hash` are missing. Exiting.")
    raise ValueError("Environment variables `bot_token`, `api_id`, or `api_hash` are missing.")

# Initialize Bot and Dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Initialize Telethon client
client = TelegramClient('user_session', API_ID, API_HASH)

async def main():
    logger.info("Starting bot...")
    init_db()
    logger.info("Database initialized.")

    register_handlers(dp, client)
    logger.info("Handlers registered.")

    setup_scheduler(bot)
    logger.info("Scheduler initialized.")

    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.exception(f"Critical error: {e}")
