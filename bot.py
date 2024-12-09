import logging
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher
from handlers import router
from scheduler import setup_scheduler, shutdown_scheduler
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
BOT_TOKEN = os.getenv('bot_token')
API_ID = os.getenv('api_id')
API_HASH = os.getenv('api_hash')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')  # Match variable name from hosting
PORT = int(os.getenv('PORT', 3000))  # Default to port 3000

# Validate environment variables
if not BOT_TOKEN or not API_ID or not API_HASH or not WEBHOOK_URL:
    logger.critical("Environment variables `bot_token`, `api_id`, `api_hash`, or `WEBHOOK_URL` are missing. Exiting.")
    raise ValueError("Environment variables `bot_token`, `api_id`, `api_hash`, or `WEBHOOK_URL` are missing.")

# Initialize Bot, Dispatcher, and Telethon client
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
client = TelegramClient("user_session", API_ID, API_HASH)

# Register routes for the bot
dp.include_router(router)

async def handle_webhook(request):
    """
    Handles webhook requests from Telegram.
    """
    try:
        update = await request.json()
        await dp.feed_update(bot=bot, update=update)
        return web.Response()
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        return web.Response(status=500)

async def main():
    logger.info("Starting bot...")

    # Initialize the database
    init_db()
    logger.info("Database initialized.")

    # Start Telethon client
    await client.start()
    logger.info("Telethon client started.")

    # Set webhook
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f"Webhook set at {WEBHOOK_URL}.")

    # Setup scheduler
    setup_scheduler(bot)
    logger.info("Scheduler initialized.")

    # Start aiohttp server
    app = web.Application()
    app.router.add_post('/webhook', handle_webhook)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=PORT)
    await site.start()
    logger.info(f"Webhook server started on port {PORT}.")

    try:
        while True:
            await asyncio.sleep(3600)  # Keep the bot running
    finally:
        await bot.delete_webhook()
        logger.info("Webhook removed.")
        await client.disconnect()
        await shutdown_scheduler()
        logger.info("Bot stopped.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.exception(f"Critical error: {e}")
