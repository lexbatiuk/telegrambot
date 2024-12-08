from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import asyncio
import os

# Получение токена из переменных окружения
API_TOKEN = os.getenv('bot_token')

# Инициализация бота
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Команда /start
@dp.message(commands=["start"])
async def send_welcome(message: types.Message):
    # Создание клавиатуры с кнопкой
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    test_button = KeyboardButton("Тест")  # Кнопка с текстом "Тест"
    keyboard.add(test_button)

    # Отправляем приветственное сообщение с клавиатурой
    await message.answer("Привет! Нажми на кнопку 'Тест'.", reply_markup=keyboard)

# Обработка кнопки "Тест"
@dp.message(lambda message: message.text == "Тест")
async def test_button_response(message: types.Message):
    await message.answer("🙂")  # Ответ смайликом

# Главная асинхронная функция
async def main():
    # Настройка диспетчера
    dp.include_router(dp)
    await bot.delete_webhook(drop_pending_updates=True)  # Удаляем вебхук, если был
    await dp.start_polling(bot)  # Запуск опроса

# Запуск бота
if __name__ == "__main__":
    asyncio.run(main())
