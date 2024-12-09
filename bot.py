import logging
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher
from handlers import register_handlers
from scheduler import setup_scheduler
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
WEBHOOK_URL = os.getenv('webhook_url')
PORT = int(os.getenv('port', 3000))

if not API_TOKEN or not API_ID or not API_HASH or not WEBHOOK_URL:
    logger.critical("Environment variables `bot_token`, `api_id`, `api_hash`, or `webhook_url` are missing. Exiting.")
    raise ValueError("Environment variables `bot_token`, `api_id`, `api_hash`, or `webhook_url` are missing.")

# Initialize Bot and Dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Initialize Telethon client
client = TelegramClient('user_session', API_ID, API_HASH)

# Ensure the webhook is correctly set up
async def ensure_webhook():
    """
    Checks and sets the webhook if needed.
    """
    try:
        webhook_info = await bot.get_webhook_info()
        if webhook_info.url != WEBHOOK_URL:
            await bot.set_webhook(WEBHOOK_URL)
            logger.info("Webhook re-registered successfully.")
        else:
            logger.info("Webhook is already set correctly.")
    except Exception as e:
        logger.exception(f"Error ensuring webhook: {e}")

# Webhook handler
async def handle_webhook(request):
    """
    Handles incoming updates from Telegram via the webhook.
    """
    try:
        update = await request.json()
        await dp.feed_raw_update(bot=bot, update=update)
        return web.Response(text="OK")
    except ConnectionResetError as e:
        logger.warning(f"Connection lost: {e}")
        return web.Response(text="Connection lost", status=500)
    except Exception as e:
        logger.exception(f"Error handling webhook: {e}")
        return web.Response(text="Error", status=500)

# Main function
async def main():
    logger.info("Starting bot...")
    # Initialize database
    init_db()
    logger.info("Database initialized.")

    # Register handlers
    register_handlers(dp, client)
    logger.info("Handlers registered.")

    # Setup scheduler
    setup_scheduler(bot)
    logger.info("Scheduler initialized.")

    # Ensure webhook is set
    await ensure_webhook()

    # Create aiohttp web app
    app = web.Application()
    app.router.add_post("/webhook", handle_webhook)

    # Run web app
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=PORT)
    await site.start()
    logger.info(f"Bot is running on port {PORT} with webhook URL: {WEBHOOK_URL}")

    # Keep the application running
    try:
        while True:
            await asyncio.sleep(3600)  # Sleep to keep the loop alive
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down bot...")
        await bot.session.close()
        await client.disconnect()
        await runner.cleanup()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.exception(f"Critical error: {e}")
