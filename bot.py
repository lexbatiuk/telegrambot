import os
import asyncio
import hashlib
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from telethon import TelegramClient

# Получение токена из переменных окружения
API_TOKEN = os.getenv('bot_token')
API_ID = os.getenv('api_id')
API_HASH = os.getenv('api_hash')

if not API_TOKEN or not API_ID or not API_HASH:
    raise ValueError("Токен бота, api_id или api_hash не заданы.")

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Инициализация клиента Telethon для работы с Telegram API
client = TelegramClient('bot_session', API_ID, API_HASH)

# Словарь для хранения каналов пользователя
user_channels = {}

# Хеширование текста для избежания повторной обработки
def get_text_hash(text: str):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

# Команда /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    start_button = KeyboardButton("Выбрать канал")
    keyboard.add(start_button)
    await message.answer("Привет! Нажми 'Выбрать канал', чтобы начать.", reply_markup=keyboard)

# Команда для выбора канала
@dp.message(Command("select_channel"))
async def select_channel(message: types.Message):
    await message.answer("Введите название канала или ссылку на канал (например, @news_channel).")
    user_channels[message.from_user.id] = []  # Инициализация списка каналов для пользователя

# Обработка введенного канала
@dp.message(lambda message: message.text.startswith('@'))
async def add_channel(message: types.Message):
    user_id = message.from_user.id
    channel = message.text.strip()
    
    # Сохраняем канал для пользователя
    if user_id not in user_channels:
        user_channels[user_id] = []
    
    user_channels[user_id].append(channel)
    
    await message.answer(f"Канал {channel} добавлен в список для мониторинга!")

# Сбор сообщений с каналов
async def fetch_messages(user_id):
    if user_id in user_channels:
        for channel in user_channels[user_id]:
            async for message in client.iter_messages(channel, limit=5):  # Ограничиваем 5 последними сообщениями
                text = message.text
                if text:
                    # Хешируем текст и проверяем, был ли он уже обработан
                    message_hash = get_text_hash(text)
                    if message_hash not in processed_texts:
                        processed_texts[message_hash] = text
                        summary = text[:200]  # Возьмем первые 200 символов как пример саммари
                        await bot.send_message(user_id, f"Саммари для {channel}: {summary}")
                    else:
                        await bot.send_message(user_id, f"Сообщение из {channel} уже было обработано.")

# Команда для получения саммари
@dp.message(Command("get_summary"))
async def get_summary(message: types.Message):
    await fetch_messages(message.from_user.id)

# Главная асинхронная функция
async def main():
    try:
        # Подключение к Telethon
        await client.start()
        # Запуск бота
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        await client.disconnect()

# Запуск бота
if __name__ == "__main__":
    asyncio.run(main())
