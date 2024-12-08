import asyncio
from aiogram import Bot, Dispatcher
from handlers import register_handlers

# Получение данных из переменных окружения
import os
API_TOKEN = os.getenv('bot_token')

if not API_TOKEN:
    raise ValueError("Необходимые переменные окружения не заданы.")

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Словарь для хранения каналов пользователей
user_channels = {}

# Регистрация обработчиков
register_handlers(dp, user_channels)

# Главная функция запуска
async def main():
    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())
