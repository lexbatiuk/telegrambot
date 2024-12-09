import logging
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from handlers import router  # Импортируем объект router
from database import init_db
from scheduler import setup_scheduler, shutdown_scheduler
from telethon.sync import TelegramClient
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Telegram API credentials
API_TOKEN = os.getenv("bot_token")
API_ID = os.getenv("api_id")
API_HASH = os.getenv("api_hash")
WEBHOOK_URL = os.getenv("webhook_url")
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.getenv("PORT", 3000))

if not API_TOKEN or not API_ID or not API_HASH or not WEBHOOK_URL:
    logger.critical(
        "Environment variables `bot_token`, `api_id`, `api_hash`, or `webhook_url` are missing. Exiting."
    )
    raise ValueError(
        "Environment variables `bot_token`, `api_id`, `api_hash`, or `webhook_url` are missing."
    )

# Initialize bot, dispatcher, and Telethon client
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
dp.include_router(router)  # Подключаем router
client = TelegramClient("user_session", API_ID, API_HASH)


async def handle_webhook(request: web.Request) -> web.Response:
    """
    Handle incoming updates from Telegram via webhook.
    """
    try:
        update = await request.json()
        await dp.feed_update(bot, update)
        return web.Response(status=200)
    except Exception as e:
        logger.exception(f"Error handling webhook: {e}")
        return web.Response(status=500)


async def main():
    """
    Main function to start the bot.
    """
    logger.info("Starting bot...")
    init_db()
    logger.info("Database initialized.")

    setup_scheduler(bot)
    logger.info("Scheduler started.")

    # Configure webhook
    await bot.set_webhook(WEBHOOK_URL)
    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, WEBAPP_HOST, WEBAPP_PORT)
    await site.start()

    logger.info("Bot is up and running!")
    try:
        await client.start()
        logger.info("Telethon client started.")
        await asyncio.Event().wait()  # Keep running until interrupted
    finally:
        await client.disconnect()
        await bot.delete_webhook()
        await shutdown_scheduler()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.exception(f"Critical error: {e}")
