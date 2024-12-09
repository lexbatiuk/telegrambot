import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from handlers import register_handlers
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_TOKEN = os.getenv("bot_token")

if not API_TOKEN:
    raise ValueError("The bot token is missing.")

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

async def handle_webhook(request):
    update = await request.json()
    await dp.feed_update(bot, update)
    return web.Response()

async def main():
    register_handlers(dp)

    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")
    await bot.set_webhook(url=os.getenv("WEBHOOK_URL"))
    setup_application(app, dp)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.getenv("PORT", 3000)))
    await site.start()
    logger.info("Webhook server started")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Critical error: {e}")
