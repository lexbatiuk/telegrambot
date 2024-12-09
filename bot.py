import asyncio
import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import router
from database import init_db

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Environment variables
BOT_TOKEN = os.getenv("bot_token")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 3000))

# Verify environment variables
required_vars = [BOT_TOKEN, WEBHOOK_URL]
missing_vars = [var for var, value in zip(["BOT_TOKEN", "WEBHOOK_URL"], [BOT_TOKEN, WEBHOOK_URL]) if not value]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Bot, Dispatcher, and Storage
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(router)

async def handle_webhook(request):
    """
    Handle incoming updates from Telegram via Webhook.
    """
    try:
        update = Update(**await request.json())
        await dp.feed_update(bot, update)
        return web.Response(status=200)
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        return web.Response(status=500)

async def main():
    """
    Main function to initialize and run the bot with Webhook.
    """
    logger.info("Starting bot...")

    # Delete old Webhook to avoid conflicts
    await bot.delete_webhook(drop_pending_updates=True)

    # Initialize the database
    await init_db()
    logger.info("Database initialized successfully.")

    # Set Webhook
    await bot.set_webhook(url=WEBHOOK_URL)
    logger.info(f"Webhook set at {WEBHOOK_URL}")

    # Start aiohttp server to handle Webhook
    app = web.Application()
    app.router.add_post("/webhook", handle_webhook)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=PORT)
    await site.start()
    logger.info(f"Webhook server started on port {PORT}")

    try:
        while True:
            await asyncio.sleep(3600)  # Keep the bot running
    finally:
        await bot.delete_webhook()
        logger.info("Bot stopped.")

if __name__ == "__main__":
    asyncio.run(main())
