import asyncio
import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import router
from database import init_db
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Environment variables
BOT_TOKEN = os.getenv("bot_token")
API_ID = os.getenv("api_id")
API_HASH = os.getenv("api_hash")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 3000))
TELEGRAM_PHONE = os.getenv("TELEGRAM_PHONE")
TELEGRAM_PASSWORD = os.getenv("TELEGRAM_PASSWORD")

# Verify environment variables
required_vars = [BOT_TOKEN, API_ID, API_HASH, WEBHOOK_URL, TELEGRAM_PHONE]
if not all(required_vars):
    raise ValueError("Missing required environment variables!")

# Bot, Dispatcher, and Storage
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Telethon client
client = TelegramClient(StringSession(), API_ID, API_HASH)

# Include router from handlers
dp.include_router(router)

async def handle_webhook(request):
    """Handle incoming updates from Telegram."""
    try:
        update = Update(**await request.json())
        await dp.feed_update(bot, update)
        return web.Response(status=200)
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        return web.Response(status=500)

async def main():
    """Main function to initialize and run the bot."""
    logger.info("Starting bot...")

    # Initialize the database
    await init_db()
    logger.info("Database initialized.")

    # Start Telethon client
    async def code_callback():
        logger.info("Waiting for the confirmation code...")
        return input("Enter Telegram code: ").strip()

    async def password_callback():
        return TELEGRAM_PASSWORD

    await client.start(
        phone=lambda: TELEGRAM_PHONE,
        code_callback=code_callback,
        password_callback=password_callback
    )
    logger.info("Telethon client started.")

    # Set webhook
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f"Webhook set at {WEBHOOK_URL}.")

    # Start aiohttp server
    app = web.Application()
    app.router.add_post("/webhook", handle_webhook)
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
        await client.disconnect()
        logger.info("Bot stopped.")

if __name__ == "__main__":
    asyncio.run(main())
