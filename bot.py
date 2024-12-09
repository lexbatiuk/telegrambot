import logging
import asyncio
from aiogram import Bot, Dispatcher
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
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
WEBHOOK_PATH = "/webhook"  # Path for webhook

if not API_TOKEN or not API_ID or not API_HASH or not WEBHOOK_URL:
    logger.critical("Environment variables `bot_token`, `api_id`, `api_hash`, or `WEBHOOK_URL` are missing. Exiting.")
    raise ValueError("Environment variables `bot_token`, `api_id`, `api_hash`, or `WEBHOOK_URL` are missing.")

# Initialize Bot and Dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Initialize Telethon client
client = TelegramClient('user_session', API_ID, API_HASH)


async def on_startup(app: web.Application):
    """Callback to handle app startup."""
    await bot.set_webhook(f"{WEBHOOK_URL}{WEBHOOK_PATH}")
    logger.info(f"Webhook set to {WEBHOOK_URL}{WEBHOOK_PATH}")


async def on_shutdown(app: web.Application):
    """Callback to handle app shutdown."""
    await bot.session.close()
    await client.disconnect()
    logger.info("Bot session and Telethon client closed.")
    logger.info("Shutdown completed.")


async def main():
    logger.info("Starting bot...")
    init_db()
    logger.info("Database initialized.")

    register_handlers(dp, client)
    logger.info("Handlers registered.")

    setup_scheduler(bot)
    logger.info("Scheduler initialized.")

    # Create webhook server
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, dp.as_handler())
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=8443)  # Use port 8443 for Telegram webhook
    logger.info("Starting webhook server...")
    await site.start()

    logger.info("Bot is running. Waiting for updates...")
    await asyncio.Event().wait()  # Keep running until interrupted


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.exception(f"Critical error: {e}")
