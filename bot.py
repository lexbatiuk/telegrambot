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
API_TOKEN = os.getenv("bot_token")
API_ID = os.getenv("api_id")
API_HASH = os.getenv("api_hash")
WEBHOOK_URL = os.getenv("webhook_url")
PORT = int(os.getenv("port", 3000))
TELEGRAM_PHONE = os.getenv("telegram_phone")

# Log loaded variables
logger.info("Loaded environment variables:")
logger.info(f"bot_token loaded: {bool(API_TOKEN)}")
logger.info(f"api_id loaded: {bool(API_ID)}")
logger.info(f"api_hash loaded: {bool(API_HASH)}")
logger.info(f"webhook_url: {WEBHOOK_URL}")
logger.info(f"port: {PORT}")
logger.info(f"telegram_phone loaded: {bool(TELEGRAM_PHONE)}")

# Validate variables
missing_vars = [
    var
    for var, value in {
        "bot_token": API_TOKEN,
        "api_id": API_ID,
        "api_hash": API_HASH,
        "webhook_url": WEBHOOK_URL,
        "telegram_phone": TELEGRAM_PHONE,
    }.items()
    if not value
]
if missing_vars:
    logger.critical(f"Missing environment variables: {', '.join(missing_vars)}")
    raise ValueError("One or more environment variables are missing.")

# Initialize bot and client
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
client = TelegramClient("user_session", API_ID, API_HASH)

# Register handlers
dp.include_router(router)

# Webhook handler
async def handle_webhook(request):
    try:
        update = await request.json()
        await dp.feed_update(bot=bot, update=update)
        return web.Response()
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        return web.Response(status=500)

# Main function
async def main():
    logger.info("Starting bot...")
    init_db()
    logger.info("Database initialized.")

    # Start Telethon client
    await client.start(phone=lambda: TELEGRAM_PHONE)
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
            await asyncio.sleep(3600)
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
