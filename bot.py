import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import register_handlers
from scheduler import setup_scheduler
from database import init_db
from aiohttp import web
import os

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
API_TOKEN = os.getenv("bot_token")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 3000))

if not API_TOKEN or not WEBHOOK_URL:
    logger.critical("Environment variables `bot_token` or `WEBHOOK_URL` are missing. Exiting.")
    raise ValueError("Environment variables `bot_token` or `WEBHOOK_URL` are missing.")

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Webhook handler
async def handle_webhook(request):
    """
    Handles incoming updates from Telegram via the webhook.
    """
    update = await request.json()
    await dp.process_update(update)
    return web.Response()

async def main():
    logger.info("Starting bot...")
    init_db()
    logger.info("Database initialized.")

    register_handlers(dp)
    logger.info("Handlers registered.")

    setup_scheduler(bot)
    logger.info("Scheduler initialized.")

    # Setting up aiohttp application
    app = web.Application()
    app.router.add_post("/webhook", handle_webhook)
    logger.info("Webhook route added.")

    # Set webhook
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f"Webhook set to {WEBHOOK_URL}")

    # Start aiohttp server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=PORT)
    logger.info(f"Running app on http://0.0.0.0:{PORT}")
    await site.start()

    # Keep the application running
    try:
        while True:
            await asyncio.sleep(3600)  # Keep alive
    finally:
        logger.info("Shutting down...")
        await bot.session.close()  # Ensure aiohttp session is closed
        await runner.cleanup()
        logger.info("Shutdown complete.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.exception(f"Critical error: {e}")
