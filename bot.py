import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.webhook.aiohttp_server import setup_application
from aiohttp import web
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

# Load environment variables
API_TOKEN = os.getenv('bot_token')
API_ID = os.getenv('api_id')
API_HASH = os.getenv('api_hash')
WEBHOOK_URL = os.getenv('webhook_url')
WEBHOOK_PATH = "/webhook"

if not API_TOKEN or not API_ID or not API_HASH or not WEBHOOK_URL:
    logger.critical("Environment variables `bot_token`, `api_id`, `api_hash`, or `webhook_url` are missing. Exiting.")
    raise ValueError("Environment variables are missing.")

# Initialize Bot and Dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Initialize Telethon client
client = TelegramClient('user_session', API_ID, API_HASH)

async def handle_webhook(request):
    """
    Handles incoming Telegram updates via webhook.
    """
    try:
        update = await request.json()
        await dp.feed_update(bot=bot, update=types.Update(**update))
        return web.Response(status=200)
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        return web.Response(status=500)

async def main():
    logger.info("Starting bot...")

    # Initialize database
    init_db()
    logger.info("Database initialized.")

    # Register handlers
    register_handlers(dp, client)
    logger.info("Handlers registered.")

    # Setup scheduler
    setup_scheduler(bot)
    logger.info("Scheduler initialized.")

    # Start Telethon client
    await client.start()
    logger.info("Telethon client started.")

    # Create webhook server
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, handle_webhook)

    # Configure webhook
    await bot.set_webhook(url=f"{WEBHOOK_URL}{WEBHOOK_PATH}")
    logger.info(f"Webhook set to {WEBHOOK_URL}{WEBHOOK_PATH}")

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, port=3000)
    await site.start()

    logger.info("Webhook server started. Listening on port 3000.")
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.exception(f"Critical error: {e}")
