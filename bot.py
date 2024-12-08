import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Получение токена из переменных окружения
API_TOKEN = os.getenv('bot_token')

# Проверка наличия токена
if not API_TOKEN:
    raise ValueError("Токен бота не найден. Убедитесь, что переменная окружения 'bot_token' задана.")

# Инициализация бота
bot = Bot(token=API_TOKEN)
dp = Dispatcher()  # Диспетчер является корневым роутером

# Команда /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    # Создание клавиатуры с кнопкой
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    test_button = KeyboardButton("Тест")  # Кнопка "Тест"
    keyboard.add(test_button)

    # Отправляем приветственное сообщение с клавиатурой
    await message.answer("Привет! Нажми на кнопку 'Тест'.", reply_markup=keyboard)

# Обработка нажатия кнопки "Тест"
@dp.message(lambda message: message.text == "Тест")
async def test_button_response(message: types.Message):
    await message.answer("🙂")  # Ответ смайликом

# Главная асинхронная функция запуска бота
async def main():
    try:
        # Удаляем старые вебхуки, если они были
        await bot.delete_webhook(drop_pending_updates=True)

        print("Бот запущен!")
        # Запускаем поллинг
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        await bot.session.close()  # Закрытие сессии бота при завершении

# Запуск бота
if __name__ == "__main__":
    asyncio.run(main())
