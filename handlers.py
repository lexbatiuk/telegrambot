from aiogram import Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from database import add_channel, get_user_channels

def register_handlers(dp: Dispatcher):
    # Обработчик команды /start
    @dp.message(Command("start"))
    async def send_welcome(message: types.Message):
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton("Добавить канал"), KeyboardButton("Мои каналы"))
        await message.answer("Привет! Используй меню для управления ботом.", reply_markup=keyboard)

    # Обработчик нажатия кнопки "Добавить канал"
    @dp.message(lambda message: message.text == "Добавить канал")
    async def select_channel(message: types.Message):
        await message.answer("Введите название канала или ссылку (например, @news_channel).")

    # Обработчик добавления канала
    @dp.message(lambda message: message.text.startswith('@'))
    async def add_channel_handler(message: types.Message):
        user_id = message.from_user.id
        channel = message.text.strip()
        if add_channel(user_id, channel):
            await message.answer(f"Канал {channel} успешно добавлен!")
        else:
            await message.answer(f"Канал {channel} уже добавлен.")

    # Обработчик нажатия кнопки "Мои каналы"
    @dp.message(lambda message: message.text == "Мои каналы")
    async def show_channels(message: types.Message):
        user_id = message.from_user.id
        channels = get_user_channels(user_id)
        if channels:
            channel_list = "\n".join(channels)
            await message.answer(f"Ваши каналы:\n{channel_list}")
        else:
            await message.answer("У вас пока нет добавленных каналов.")
