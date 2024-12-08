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
    KeyboardButton("Список каналов")
)

# Команда /start
async def send_welcome(message: types.Message):
    await message.answer("Привет! Вот что я могу сделать:", reply_markup=keyboard)

# Обработка кнопки "Добавить канал"
async def select_channel(message: types.Message):
    await message.answer("Введите название канала или ссылку на канал (например, @news_channel).")
    user_channels[message.from_user.id] = []

# Обработка добавления канала
async def add_channel(message: types.Message):
    user_id = message.from_user.id
    channel = message.text.strip()

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
    if user_id in user_channels
