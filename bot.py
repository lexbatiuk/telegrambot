import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from aiogram.fsm.storage.memory import MemoryStorage
from telethon import TelegramClient
from telethon.sessions import StringSession
from handlers import router
from database import init_db
from config import Config

# Логгирование
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Валидация переменных окружения
Config.validate()

# Инициализация бота и диспетчера
bot = Bot(token=Config.BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(router)

# Инициализация Telethon клиента
client = TelegramClient(StringSession(), Config.API_ID, Config.API_HASH)

async def handle_webhook(request):
    """Обработка входящих обновлений от Telegram."""
    update = Update(**await request.json())
    await dp.feed_update(bot, update)
    return web.Response(status=200)

async def main():
    """Основная функция запуска бота."""
    logger.info("Starting bot...")

    # Инициализация базы данных
    await init_db()

    # Старт Telethon клиента
    async def code_callback():
        code = input("Enter Telegram code: ").strip()
        return code

    async def password_callback():
        return Config.TELEGRAM_PASSWORD

    await client.start(
        phone=lambda: Config.TELEGRAM_PHONE,
        code_callback=code_callback,
        password_callback=password_callback
    )
    logger.info("Telethon client started.")

    # Установка webhook
    await bot.set_webhook(Config.WEBHOOK_URL)
    logger.info(f"Webhook set at {Config.WEBHOOK_URL}.")

    # Запуск aiohttp сервера
    app = web.Application()
    app.router.add_post("/webhook", handle_webhook)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=Config.PORT)
    await site.start()
    logger.info(f"Webhook server started on port {Config.PORT}.")

    try:
        while True:
            await asyncio.sleep(3600)  # Keep the bot running
    finally:
        await bot.delete_webhook()
        await client.disconnect()
        logger.info("Bot stopped.")

if __name__ == "__main__":
    asyncio.run(main())
