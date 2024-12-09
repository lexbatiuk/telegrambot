from aiogram import Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from database import add_channel, get_user_channels
import os

# Получаем список разрешенных пользователей из переменной окружения
ALLOWED_USERS = [int(os.getenv('ALLOWED_USER_ID'))]

def register_handlers(dp: Dispatcher, client):
    # Проверка доступа
    @dp.message()
    async def check_access(message: types.Message):
        if message.from_user.id not in ALLOWED_USERS:
            await message.answer("Sorry, you are not authorized to use this bot.")
            return  # Останавливаем обработку для неавторизованных пользователей

    # Обработчик команды /start
    @dp.message(Command("start"))
    async def send_welcome(message: types.Message):
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Add Channel"), KeyboardButton(text="My Channels")],
                [KeyboardButton(text="Get Digest")]
            ],
            resize_keyboard=True
        )
        await message.answer("Welcome! Use the menu to interact with the bot.", reply_markup=keyboard)

    # Добавление канала
    @dp.message(lambda message: message.text == "Add Channel")
    async def select_channel(message: types.Message):
        await message.answer("Please enter the channel name or link (e.g., @channel_name).")

    @dp.message(lambda message: message.text.startswith('@'))
    async def add_channel_handler(message: types.Message):
        user_id = message.from_user.id
        channel = message.text.strip()
        if add_channel(user_id, channel):
            await message.answer(f"Channel {channel} successfully added!")
        else:
            await message.answer(f"Channel {channel} is already added.")

    # Получение списка каналов
    @dp.message(lambda message: message.text == "My Channels")
    async def show_channels(message: types.Message):
        user_id = message.from_user.id
        channels = get_user_channels(user_id)
        if channels:
            channel_list = "\n".join(channels)
            await message.answer(f"Your channels:\n{channel_list}")
        else:
            await message.answer("You have no added channels.")

    # Получение дайджеста
    @dp.message(lambda message: message.text == "Get Digest")
    async def get_digest(message: types.Message):
        user_id = message.from_user.id
        # Логика получения дайджеста
        await message.answer("Here is your digest (mock data for now).")
