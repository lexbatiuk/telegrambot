import logging
import asyncio
import os
from aiohttp import web
from aiogram import Bot, Dispatcher
from handlers import register_handlers
from scheduler import setup_scheduler
from database import init_db
from telethon.sync import TelegramClient

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
WEBHOOK_URL = os.getenv('WEBHOOK_URL')  # Full URL for webhook (e.g., "https://your-domain.com/webhook")
PORT = int(os.getenv('PORT', 3000))  # Default port is 3000

if not API_TOKEN or not API_ID or not API_HASH or not WEBHOOK_URL:
    logger.critical("Environment variables `bot_token`, `api_id`, `api_hash`, or `WEBHOOK_URL` are missing. Exiting.")
    raise ValueError("Environment variables `bot_token`, `api_id`, `api_hash`, or `WEBHOOK_URL` are missing.")

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Initialize Telethon client
client = TelegramClient('user_session', API_ID, API_HASH)

# Create aiohttp app
app = web.Application()

async def handle_webhook(request):
    """Handles incoming updates from Telegram via webhook."""
    try:
        update = await request.json()
        await dp.feed_raw_update(bot=bot, update=update)
        return web.Response(text="OK")
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        return web.Response(text="Error", status=500)

async def main():
    logger.info("Starting bot...")
    init_db()
    logger.info("Database initialized.")

    # Register handlers
    register_handlers(dp, client)
    logger.info("Handlers registered.")

    # Setup scheduler
    setup_scheduler(bot)
    logger.info("Scheduler initialized.")

    # Set webhook
    await bot.set_webhook(url=WEBHOOK_URL)
    logger.info(f"Webhook set to {WEBHOOK_URL}")

    # Configure aiohttp routes
    app.router.add_post("/webhook", handle_webhook)

    # Start aiohttp server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=PORT)
    logger.info(f"Webhook server started on port {PORT}")
    await site.start()

    try:
        while True:
            await asyncio.sleep(3600)  # Keep the server running
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down...")
        await runner.cleanup()
        await bot.delete_webhook()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.exception(f"Critical error: {e}")
