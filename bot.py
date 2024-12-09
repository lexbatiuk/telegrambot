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

# Environment variables
API_TOKEN = os.getenv("bot_token")
API_ID = os.getenv("api_id")
API_HASH = os.getenv("api_hash")
TELEGRAM_PHONE = os.getenv("TELEGRAM_PHONE")
TELEGRAM_PASSWORD = os.getenv("TELEGRAM_PASSWORD")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 3000))

# Validate environment variables
missing_vars = [
    var
    for var, value in {
        "bot_token": API_TOKEN,
        "api_id": API_ID,
        "api_hash": API_HASH,
        "TELEGRAM_PHONE": TELEGRAM_PHONE,
        "TELEGRAM_PASSWORD": TELEGRAM_PASSWORD,
        "WEBHOOK_URL": WEBHOOK_URL,
    }.items()
    if not value
]

if missing_vars:
    logger.critical(f"Missing environment variables: {', '.join(missing_vars)}")
    raise ValueError("One or more environment variables are missing.")

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Register routes for the bot
dp.include_router(router)

# Initialize Telethon client
client = TelegramClient("user_session", API_ID, API_HASH)


async def handle_webhook(request):
    """Handles webhook requests from Telegram."""
    try:
        update = await request.json()
        await dp.feed_update(bot=bot, update=update)
        return web.Response()
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        return web.Response(status=500)


async def main():
    """Main function to start the bot."""
    logger.info("Starting bot...")
    init_db()
    logger.info("Database initialized.")

    # Start Telethon client
    async def code_callback():
        logger.info("Waiting for the confirmation code...")
        return os.getenv("TELEGRAM_CODE", "")

    async def password_callback():
        return TELEGRAM_PASSWORD

    await client.start(
        phone=lambda: TELEGRAM_PHONE,
        code_callback=code_callback,
        password_callback=password_callback,
    )
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
