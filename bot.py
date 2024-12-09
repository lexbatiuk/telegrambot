import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
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

# Telegram API credentials
API_TOKEN = os.getenv('bot_token')
API_ID = os.getenv('api_id')
API_HASH = os.getenv('api_hash')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')  # Webhook URL
WEBHOOK_PATH = os.getenv('WEBHOOK_PATH', '/webhook')  # Optional, default is '/webhook'
PORT = int(os.getenv('PORT', 3000))  # Default to 3000 if not set

if not API_TOKEN or not API_ID or not API_HASH or not WEBHOOK_URL:
    logger.critical("Environment variables `bot_token`, `api_id`, `api_hash`, or `WEBHOOK_URL` are missing. Exiting.")
    raise ValueError("Environment variables `bot_token`, `api_id`, `api_hash`, or `WEBHOOK_URL` are missing.")

# Initialize Bot and Dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Initialize Telethon client
client = TelegramClient('user_session', API_ID, API_HASH)

async def on_startup(app):
    """
    Actions to perform when the app starts.
    """
    logger.info("Setting webhook...")
    await bot.set_webhook(WEBHOOK_URL)
    logger.info("Webhook set successfully.")

async def on_shutdown(app):
    """
    Actions to perform when the app shuts down.
    """
    logger.info("Removing webhook...")
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.session.close()
    logger.info("Webhook removed successfully.")

def main():
    """
    Main entry point for the application.
    """
    app = web.Application()

    # Setup webhook handlers
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    # Register callbacks for startup and shutdown
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    # Initialize the database
    init_db()
    logger.info("Database initialized.")

    # Register handlers
    register_handlers(dp, client)
    logger.info("Handlers registered.")

    # Setup task scheduler
    setup_scheduler(bot)
    logger.info("Scheduler initialized.")

    # Start the application
    web.run_app(app, host='0.0.0.0', port=PORT)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception(f"Critical error: {e}")
