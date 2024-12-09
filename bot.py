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

# Telegram API credentials
API_TOKEN = os.getenv('bot_token')
API_ID = os.getenv('api_id')
API_HASH = os.getenv('api_hash')
TELEGRAM_PHONE = os.getenv('TELEGRAM_PHONE')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
PORT = int(os.getenv('PORT', 3000))

# Validate environment variables
missing_vars = []
if not API_TOKEN:
    missing_vars.append('bot_token')
if not API_ID:
    missing_vars.append('api_id')
if not API_HASH:
    missing_vars.append('api_hash')
if not TELEGRAM_PHONE:
    missing_vars.append('TELEGRAM_PHONE')
if not WEBHOOK_URL:
    missing_vars.append('WEBHOOK_URL')

if missing_vars:
    logger.critical(f"Missing environment variables: {', '.join(missing_vars)}")
    raise ValueError("One or more environment variables are missing.")

# Initialize Bot, Dispatcher, and Telethon client
bot = Bot(token=API_TOKEN)
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
    logger.info("Starting Telethon client...")
    await client.start(phone=lambda: TELEGRAM_PHONE)
    logger.info("Telethon client started.")

    # Set webhook
    logger.info(f"Setting webhook to {WEBHOOK_URL}...")
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
        logger.info("Shutting down bot...")
        await bot.delete_webhook()
        logger.info("Webhook removed.")
        await client.disconnect()
        logger.info("Telethon client disconnected.")
        await shutdown_scheduler()
        logger.info("Scheduler shutdown completed.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.exception(f"Critical error: {e}")
