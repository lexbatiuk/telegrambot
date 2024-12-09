import logging
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher
from handlers import router
from scheduler import setup_scheduler, shutdown_scheduler
from database import init_db
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
BOT_TOKEN = os.getenv("bot_token")
API_ID = os.getenv("api_id")
API_HASH = os.getenv("api_hash")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 3000))

if not all([BOT_TOKEN, API_ID, API_HASH, WEBHOOK_URL]):
    raise ValueError("Required environment variables are missing.")

# Initialize bot, dispatcher, and Telegram client
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
dp.include_router(router)

# Webhook handling
async def handle_webhook(request):
    update = await request.json()
    await dp.feed_update(bot=bot, update=update)
    return web.Response()

async def main():
    logger.info("Starting bot...")
    await bot.set_webhook(WEBHOOK_URL)
    setup_scheduler()
    app = web.Application()
    app.router.add_post("/webhook", handle_webhook)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, port=PORT)
    await site.start()
    logger.info(f"Bot is listening on port {PORT}.")

    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        await bot.delete_webhook()
        await shutdown_scheduler()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.exception(f"Bot crashed with error: {e}")
