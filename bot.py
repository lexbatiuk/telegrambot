from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import register_handlers
from scheduler import setup_scheduler
from database import init_db
from aiohttp import web
import os
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
API_TOKEN = os.getenv("bot_token")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not API_TOKEN or not WEBHOOK_URL:
    logger.critical("Environment variables `bot_token` or `WEBHOOK_URL` are missing. Exiting.")
    raise ValueError("Environment variables `bot_token` or `WEBHOOK_URL` are missing.")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

async def main():
    logger.info("Starting bot...")
    init_db()
    logger.info("Database initialized.")

    register_handlers(dp)
    logger.info("Handlers registered.")

    setup_scheduler(bot)
    logger.info("Scheduler initialized.")

    # Setting webhook
    app = web.Application()
    dp.setup_routes(app)
    logger.info("Webhook routes setup completed.")

    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f"Webhook set to {WEBHOOK_URL}")

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=int(os.getenv("PORT", 3000)))
    logger.info("Running app on http://0.0.0.0:3000")
    await site.start()

if __name__ == "__main__":
    try:
        import asyncio
        asyncio.run(main())
    except Exception as e:
        logger.exception(f"Critical error: {e}")
