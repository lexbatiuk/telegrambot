import logging
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher
from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError
from handlers import register_handlers
from scheduler import setup_scheduler
from database import init_db
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Environment variables
API_TOKEN = os.getenv('bot_token')
API_ID = os.getenv('api_id')
API_HASH = os.getenv('api_hash')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
PORT = int(os.getenv('PORT', 3000))

if not all([API_TOKEN, API_ID, API_HASH, WEBHOOK_URL]):
    logger.critical("Environment variables `bot_token`, `api_id`, `api_hash`, or `WEBHOOK_URL` are missing.")
    raise ValueError("Environment variables `bot_token`, `api_id`, `api_hash`, or `WEBHOOK_URL` are missing.")

# Initialize Bot and Dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Initialize Telethon client
client = TelegramClient('user_session', API_ID, API_HASH)

async def handle_webhook(request):
    """
    Handles incoming webhook requests from Telegram.
    """
    try:
        update = await request.json()
        await dp.feed_update(bot, update)
        return web.Response()
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        return web.Response(status=500)

async def main():
    # Start Telethon client
    await client.start()
    logger.info("Telethon client connected.")

    # Initialize database
    init_db()
    logger.info("Database initialized.")

    # Register handlers
    register_handlers(dp, client)
    logger.info("Handlers registered.")

    # Set webhook
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f"Webhook set to {WEBHOOK_URL}")

    # Start scheduler
    setup_scheduler(bot)
    logger.info("Scheduler started.")

    # Start web server
    app = web.Application()
    app.router.add_post('/webhook', handle_webhook)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=PORT)
    await site.start()
    logger.info(f"Webhook server started on port {PORT}")

    # Keep the program running
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down bot...")
        await client.disconnect()
        logger.info("Telethon client disconnected.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.exception(f"Critical error: {e}")
