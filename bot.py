import logging
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from handlers import router
from scheduler import setup_scheduler, shutdown_scheduler
from database import init_db
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
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
WEBHOOK_URL = os.getenv("webhook_url")
PORT = int(os.getenv("PORT", 3000))
TELEGRAM_PHONE = os.getenv("TELEGRAM_PHONE")
TELEGRAM_PASSWORD = os.getenv("TELEGRAM_PASSWORD")
ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID", 0))
DB_DSN = os.getenv("DATABASE_URL")

# Check environment variables
missing_vars = [
    ("API_TOKEN", API_TOKEN),
    ("API_ID", API_ID),
    ("API_HASH", API_HASH),
    ("WEBHOOK_URL", WEBHOOK_URL),
    ("TELEGRAM_PHONE", TELEGRAM_PHONE),
    ("DATABASE_URL", DB_DSN),
]
missing = [var for var, value in missing_vars if not value]
if missing:
    logger.critical(f"Missing environment variables: {', '.join(missing)}")
    raise ValueError("Missing required environment variables!")

# Initialize bot, dispatcher, and Telethon client
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
client = TelegramClient("user_session", API_ID, API_HASH)

# Store the event loop for external callbacks
event_loop = asyncio.get_event_loop()

# Global flag for awaiting code
awaiting_code = False


async def request_code(message: types.Message):
    """
    Request the confirmation code from the user via bot message.
    """
    global awaiting_code
    if message.from_user.id != ALLOWED_USER_ID:
        await message.answer("You are not authorized to send the code.")
        return

    if not awaiting_code:
        await message.answer("Not waiting for a confirmation code right now.")
        return

    code = message.text.strip()
    try:
        await client.sign_in(phone=TELEGRAM_PHONE, code=code)
        awaiting_code = False
        await message.answer("Authorization completed successfully!")
    except Exception as e:
        logger.error(f"Failed to sign in: {e}")
        await message.answer(f"Failed to authorize with this code: {e}")


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


@dp.message(Command(commands=["start"]))
async def start_handler(message: types.Message):
    """
    Start command handler for testing bot response.
    """
    await message.answer("Bot is running! 🚀")


async def main():
    logger.info("Starting bot...")
    # Initialize database
    await init_db()
    logger.info("Database initialized successfully.")

    # Start Telethon client
    try:
        await client.start(phone=lambda: TELEGRAM_PHONE)
        logger.info("Telethon client connected.")
    except SessionPasswordNeededError:
        if TELEGRAM_PASSWORD:
            await client.sign_in(password=TELEGRAM_PASSWORD)
        else:
            logger.error("Two-factor authentication password is required but not provided.")
            raise

    # Handle cases when user is not authorized
    global awaiting_code
    if not client.is_user_authorized():
        awaiting_code = True
        logger.info("Waiting for the confirmation code via bot message.")

    # Set webhook
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f"Webhook set at {WEBHOOK_URL}.")

    # Start aiohttp server
    app = web.Application()
    app.router.add_post('/webhook', handle_webhook)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=PORT)
    await site.start()
    logger.info(f"Webhook server started on port {PORT}.")

    # Run the bot
    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        await bot.delete_webhook()
        logger.info("Webhook removed.")
        await client.disconnect()
        logger.info("Telethon client disconnected.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.exception(f"Critical error: {e}")
