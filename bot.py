import logging
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from handlers import router
from scheduler import setup_scheduler, shutdown_scheduler
from database import init_db
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
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
ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID"))

if not API_TOKEN or not API_ID or not API_HASH or not WEBHOOK_URL:
    raise ValueError("Missing required environment variables!")

# Path to the session file
SESSION_FILE_PATH = "/data/telegram_session"

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Telethon client with file-based session
client = TelegramClient(
    StringSession(),
    API_ID,
    API_HASH,
    system_version="TelethonSession",
    session=SESSION_FILE_PATH
)

telethon_code = None


async def handle_code_request(message: types.Message):
    """
    Handle incoming messages to request a Telegram code.
    """
    global telethon_code
    if message.from_user.id != ALLOWED_USER_ID:
        await message.answer("Access denied.")
        return

    telethon_code = message.text.strip()
    await message.answer("Code received. Restarting login process...")
    # Stop event loop to restart client
    asyncio.get_event_loop().stop()


async def request_code():
    """
    Request the Telegram code from the user via the bot chat.
    """
    await bot.send_message(ALLOWED_USER_ID, "Please enter the Telegram code you received:")


async def main():
    logger.info("Starting bot...")
    await init_db()

    logger.info("Database initialized.")
    dp.include_router(router)

    # Set webhook
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f"Webhook set at {WEBHOOK_URL}.")

    # Initialize Telethon client
    await client.connect()
    if not await client.is_user_authorized():
        try:
            await client.send_code_request(TELEGRAM_PHONE)
            await request_code()

            # Wait until the code is received via bot
            global telethon_code
            while telethon_code is None:
                await asyncio.sleep(1)

            await client.sign_in(TELEGRAM_PHONE, telethon_code)
        except SessionPasswordNeededError:
            await bot.send_message(ALLOWED_USER_ID, "Please provide your Telegram password:")
            while telethon_code is None:
                await asyncio.sleep(1)
            await client.sign_in(password=telethon_code)

    logger.info("Telethon client started.")

    # Start aiohttp server
    app = web.Application()
    app.router.add_post('/webhook', dp.start_polling)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=PORT)
    await site.start()

    logger.info(f"Webhook server started on port {PORT}.")
    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.exception(f"Critical error: {e}")
