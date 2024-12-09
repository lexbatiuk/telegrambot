import logging
import os
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher
from handlers import register_handlers
from scheduler import setup_scheduler, shutdown_scheduler
from database import init_db
from telethon import TelegramClient

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Telegram API credentials
API_TOKEN = os.getenv("bot_token")
API_ID = os.getenv("api_id")
API_HASH = os.getenv("api_hash")
WEBHOOK_URL = os.getenv("webhook_url")
WEBHOOK_PATH = "/webhook"

if not all([API_TOKEN, API_ID, API_HASH, WEBHOOK_URL]):
    logger.critical("Environment variables `bot_token`, `api_id`, `api_hash`, or `webhook_url` are missing. Exiting.")
    raise ValueError("Environment variables `bot_token`, `api_id`, `api_hash`, or `webhook_url` are missing.")

# Initialize Bot and Dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Initialize Telethon client
telethon_client = TelegramClient('user_session', API_ID, API_HASH)

# Setup web server
app = web.Application()

async def handle_webhook(request):
    try:
        update = await request.json()
        await dp.feed_update(bot, update)
        return web.Response()
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        return web.Response(status=500)

app.router.add_post(WEBHOOK_PATH, handle_webhook)

async def on_startup(app):
    logger.info("Starting bot...")
    await bot.set_webhook(WEBHOOK_URL + WEBHOOK_PATH)
    await telethon_client.connect()
    init_db()
    register_handlers(dp, telethon_client)
    setup_scheduler(bot)
    logger.info("Bot is running.")

async def on_shutdown(app):
    logger.info("Shutting down bot...")
    await bot.delete_webhook()
    await telethon_client.disconnect()
    await shutdown_scheduler()
    logger.info("Bot stopped.")

app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

if __name__ == "__main__":
    web.run_app(app, port=int(os.getenv("port", 3000)))
