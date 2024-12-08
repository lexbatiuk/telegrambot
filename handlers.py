from aiogram import Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import hashlib

# Локальные данные
user_channels = {}
processed_texts = {}

# Хеширование текста
def get_text_hash(text: str):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

# Постоянная клавиатура
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(
    KeyboardButton("Добавить канал"),
    KeyboardButton("Получить саммари"),
    KeyboardButton("Список каналов")  # Новая кнопка для отображения списка каналов
)

# Команда /start
async def send_welcome(message: types.Message):
    await message.answer("Привет! Вот что я могу сделать:", reply_markup=keyboard)

# Обработка кнопки "Добавить канал"
async def select_channel(message: types.Message):
    await message.answer("Введите название канала или ссылку на канал (например, @news_channel).")
    if message.from_user.id not in user_channels:
        user_channels[message.from_user.id] = []

# Обработка добавления канала
async def add_channel(message: types.Message):
    user_id = message.from_user.id
    channel = message.text.strip()

    # Проверка, что канал уже не добавлен
    if channel not in user_channels.get(user_id, []):
        user_channels[user_id].append(channel)
        await message.answer(f"Канал {channel} добавлен в список для мониторинга!")
    else:
        await message.answer(f"Канал {channel} уже добавлен.")

# Обработка кнопки "Список каналов"
async def list_channels(message: types.Message):
    user_id = message.from_user.id
    channels = user_channels.get(user_id, [])
    if channels:
        await message.answer("Ваши каналы:\n" + "\n".join(channels))
    else:
        await message.answer("У вас пока нет добавленных каналов.")

# Обработка кнопки "Получить саммари"
async def get_summary(message: types.Message, client):
    user_id = message.from_user.id
    if user_id in user_channels and user_channels[user_id]:
        for channel in user_channels[user_id]:
            async for msg in client.iter_messages(channel, limit=5):
                text = msg.text
                if text:
                    message_hash = get_text_hash(text)
                    if message_hash not in processed_texts:
                        processed_texts[message_hash] = text
                        summary = text[:200]
                        await message.answer(f"Саммари для {channel}: {summary}")
    else:
        await message.answer("Добавьте хотя бы один канал, чтобы получить саммари.")

# Регистрация обработчиков
def register_handlers(dp: Dispatcher, client):
    dp.message.register(send_welcome, Command("start"))
    dp.message.register(select_channel, lambda message: message.text == "Добавить канал")
    dp.message.register(add_channel, lambda message: message.text.startswith('@'))
    dp.message.register(list_channels, lambda message: message.text == "Список каналов")
    dp.message.register(lambda message: get_summary(message, client), lambda message: message.text == "Получить саммари")
