import logging
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import router
from database import init_db

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Получение переменных окружения
import os
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 3000))
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
TELEGRAM_PHONE = os.getenv("TELEGRAM_PHONE")
TELEGRAM_PASSWORD = os.getenv("TELEGRAM_PASSWORD")
DATABASE_URL = os.getenv("DATABASE_URL")

# Проверка переменных окружения
required_vars = {
    "BOT_TOKEN": BOT_TOKEN,
    "WEBHOOK_URL": WEBHOOK_URL,
    "API_ID": API_ID,
    "API_HASH": API_HASH,
    "TELEGRAM_PHONE": TELEGRAM_PHONE,
    "DATABASE_URL": DATABASE_URL,
}
missing_vars = [key for key, value in required_vars.items() if not value]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)  # parse_mode будет задан в отдельных функциях
dp = Dispatcher(storage=MemoryStorage())

# Подключение обработчиков
dp.include_router(router)

# Обработчик вебхука
async def handle_webhook(request):
    try:
        update = Update(**await request.json())
        await dp.feed_update(bot, update)
        return web.Response(status=200)
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        return web.Response(status=500)

# Главная функция
async def main():
    logger.info("Starting bot...")

    # Инициализация базы данных
    await init_db()
    logger.info("Database initialized successfully.")

    # Установка вебхука
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f"Webhook set at {WEBHOOK_URL}")

    # Запуск aiohttp-сервера
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
        logger.info("Webhook removed.")

if __name__ == "__main__":
    asyncio.run(main())
