import logging
from aiogram import Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from database import add_channel, get_user_channels

logger = logging.getLogger(__name__)

def register_handlers(dp: Dispatcher):
    @dp.message(Command("start"))
    async def send_welcome(message: types.Message):
        logger.info(f"Пользователь {message.from_user.id} отправил /start.")
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Добавить канал"), KeyboardButton(text="Мои каналы")]
            ],
            resize_keyboard=True
        )
        await message.answer("Привет! Используй меню для управления ботом.", reply_markup=keyboard)

    @dp.message(lambda message: message.text == "Добавить канал")
    async def select_channel(message: types.Message):
        logger.info(f"Пользователь {message.from_user.id} выбрал 'Добавить канал'.")
        await message.answer("Введите название канала или ссылку (например, @news_channel).")

    @dp.message(lambda message: message.text.startswith('@'))
    async def add_channel_handler(message: types.Message):
        user_id = message.from_user.id
        channel = message.text.strip()
        if add_channel(user_id, channel):
            logger.info(f"Канал {channel} добавлен для пользователя {user_id}.")
            await message.answer(f"Канал {channel} успешно добавлен!")
        else:
            logger.warning(f"Канал {channel} уже добавлен для пользователя {user_id}.")
            await message.answer(f"Канал {channel} уже добавлен.")

    @dp.message(lambda message: message.text == "Мои каналы")
    async def show_channels(message: types.Message):
        user_id = message.from_user.id
        channels = get_user_channels(user_id)
        if channels:
            logger.info(f"Пользователь {user_id} запросил свои каналы.")
            channel_list = "\n".join(channels)
            await message.answer(f"Ваши каналы:\n{channel_list}")
        else:
            logger.info(f"У пользователя {user_id} нет добавленных каналов.")
            await message.answer("У вас пока нет добавленных каналов.")
