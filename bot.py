import asyncio
from aiogram import Bot, Dispatcher
from telethon import TelegramClient
from dotenv import load_dotenv
import os

# Импортируем функции из других файлов
from handlers import register_handlers
from scheduler import start_scheduler

# Загружаем переменные окружения
load_dotenv()

# Получение данных из переменных окружения
API_TOKEN = os.getenv('bot_token')
API_ID = os.getenv('api_id')
API_HASH = os.getenv('api_hash')

if not API_TOKEN or not API_ID or not API_HASH:
    raise ValueError("Необходимые переменные окружения не заданы.")

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Инициализация клиента Telethon
client = TelegramClient('bot_session', API_ID, API_HASH)

# Регистрация обработчиков
register_handlers(dp, client)

# Главная асинхронная функция
async def main():
    try:
        await client.start()  # Подключаем Telethon
        await start_scheduler(client, bot)  # Запускаем планировщик задач
        await dp.start_polling(bot)  # Запускаем aiogram
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        await client.disconnect()

# Запуск
if __name__ == "__main__":
    asyncio.run(main())
