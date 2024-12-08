import os
import hashlib
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telethon import TelegramClient
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Получение данных из переменных окружения
API_TOKEN = os.getenv('bot_token')  # Токен бота
API_ID = os.getenv('api_id')  # ID из Telegram
API_HASH = os.getenv('api_hash')  # Hash из Telegram

if not API_TOKEN or not API_ID or not API_HASH:
    raise ValueError("Необходимые переменные окружения не заданы.")

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Инициализация клиента Telethon для работы с Telegram API
client = TelegramClient('bot_session', API_ID, API_HASH)

# Словарь для хранения каналов пользователя
user_channels = {}

# Словарь для хранения хешей обработанных сообщений
processed_texts = {}

# Хеширование текста для избежания повторной обработки
def get_text_hash(text: str):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

# Команда /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    keyboard = InlineKeyboardMarkup()
    start_button = InlineKeyboardButton("Выбрать канал", callback_data="select_channel")
    get_summary_button = InlineKeyboardButton("Получить саммари", callback_data="get_summary")
    keyboard.add(start_button, get_summary_button)
    await message.answer("Привет! Выберите действие:", reply_markup=keyboard)

# Обработка кнопки "Выбрать канал"
@dp.callback_query(lambda c: c.data == "select_channel")
async def process_select_channel(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "Введите название канала или ссылку на канал (например, @news_channel).")
    user_channels[callback_query.from_user.id] = []  # Инициализация списка каналов для пользователя

# Обработка введенного канала
@dp.message(lambda message: message.text.startswith('@'))
async def add_channel(message: types.Message):
    user_id = message.from_user.id
    channel = message.text.strip()

    # Проверка, что канал уже не добавлен
    if channel not in user_channels.get(user_id, []):
        user_channels[user_id].append(channel)
        await message.answer(f"Канал {channel} добавлен в список для мониторинга!")
    else:
        await message.answer(f"Канал {channel} уже добавлен.")

# Сбор сообщений с каналов
async def fetch_messages(user_id):
    if user_id in user_channels:
        for channel in user_channels[user_id]:
            try:
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
            except Exception as e:
                await bot.send_message(user_id, f"Ошибка при обработке канала {channel}: {e}")

# Команда для получения саммари
@dp.callback_query(lambda c: c.data == "get_summary")
async def get_summary(callback_query: types.CallbackQuery):
    await fetch_messages(callback_query.from_user.id)

# Планировщик задач для автоматического сбора новостей
async def scheduled_task():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(fetch_messages, 'interval', hours=24, args=[message.from_user.id])  # Запускать раз в 24 часа
    scheduler.start()

# Главная асинхронная функция
async def main():
    try:
        # Подключение к Telethon (передаем bot_token вместо номера телефона)
        await client.start(bot_token=API_TOKEN)  # Передаем именно bot_token
        # Запуск бота через aiogram
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        await client.disconnect()

# Запуск бота
if __name__ == "__main__":
    asyncio.run(main())
