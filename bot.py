import logging
import asyncio
from aiogram import Bot, Dispatcher
from handlers import router
from database import init_db
import os

# Configure logging
logging.basicConfig(level=logging.INFO)

# Environment variables
API_TOKEN = os.getenv("BOT_TOKEN")

if not API_TOKEN:
    raise ValueError("No BOT_TOKEN provided")

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
dp.include_router(router)

async def main():
    """
    Main entry point of the bot.
    """
    logging.info("Initializing database...")
    await init_db()  # Initialize the database

    logging.info("Starting bot polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
