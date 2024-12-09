import logging
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from handlers import register_handlers
from scheduler import setup_scheduler, shutdown_scheduler
from database import init_db
from telethon.sync import TelegramClient
import os

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Чтение переменных окружения
API_TOKEN = os.getenv('bot_token')
API_ID = os.getenv('api_id')
API_HASH = os.getenv('api_hash')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
WEBHOOK_PATH = os.getenv('WEBHOOK_PATH', '/webhook')  # Путь вебхука по умолчанию

if not API_TOKEN or not API_ID or not API_HASH or not WEBHOOK_URL:
    logger.critical("Отсутствуют необходимые переменные окружения.")
    raise ValueError("Переменные окружения `bot_token`, `api_id`, `api_hash`, или `WEBHOOK_URL` отсутствуют.")

# Инициализация бота, диспетчера и Telethon клиента
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
client = TelegramClient('user_session', API_ID, API_HASH)

async def on_startup(app: web.Application):
    """
    Callback на старте приложения.
    """
    logger.info("Запуск бота...")
    init_db()
    logger.info("База данных инициализирована.")

    # Регистрация обработчиков
    register_handlers(dp, client)
    logger.info("Обработчики зарегистрированы.")

    # Настройка планировщика задач
    setup_scheduler(bot)
    logger.info("Планировщик задач запущен.")

    # Установка вебхука
    await bot.set_webhook(WEBHOOK_URL + WEBHOOK_PATH)
    logger.info(f"Webhook установлен на {WEBHOOK_URL + WEBHOOK_PATH}")

async def on_shutdown(app: web.Application):
    """
    Callback при завершении работы приложения.
    """
    logger.info("Завершаем работу...")
    await shutdown_scheduler()  # Завершение планировщика
    await bot.session.close()  # Завершение сессии бота
    await client.disconnect()  # Отключение Telethon клиента
    logger.info("Все подключения завершены.")

def main():
    """
    Основная точка входа.
    """
    app = web.Application()

    # Установка обработчиков для вебхука
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    # Регистрация callbacks
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    # Запуск приложения
    web.run_app(app, host='0.0.0.0', port=int(os.getenv('PORT', 3000)))

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception(f"Критическая ошибка: {e}")
