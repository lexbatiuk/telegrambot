from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
import os

# Получение токена бота из переменных окружения
API_TOKEN = os.getenv('bot_token')

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Команда /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    # Создание клавиатуры с кнопкой
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    test_button = KeyboardButton("Тест")  # Кнопка с названием "Тест"
    keyboard.add(test_button)
    
    # Отправляем сообщение с клавиатурой
    await message.answer("Привет! Нажми на кнопку 'Тест'.", reply_markup=keyboard)

# Обработка нажатия кнопки "Тест"
@dp.message_handler(lambda message: message.text == "Тест")
async def test_button_response(message: types.Message):
    await message.answer("🙂")  # Отправляем смайлик в ответ на кнопку

# Запуск бота
if __name__ == '__main__':
    print("Бот запущен...")
    executor.start_polling(dp, skip_updates=True)
