from aiogram import Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from database import add_channel, get_user_channels
from telethon import TelegramClient
import logging
import os

logger = logging.getLogger(__name__)

# Подключение к Telegram API через переменные окружения
API_ID = os.getenv("api_id")
API_HASH = os.getenv("api_hash")
BOT_TOKEN = os.getenv("bot_token")
client = TelegramClient('bot_session', API_ID, API_HASH)

async def fetch_messages_from_channels(user_channels):
    """
    Получает последние сообщения из всех каналов пользователя.
    """
    try:
        # Инициализация Telethon как бота
        await client.start(bot_token=BOT_TOKEN)
        all_messages = []
        for channel in user_channels:
            messages = []
            async for message in client.iter_messages(channel, limit=5):  # 5 последних сообщений
                if message.text:
                    messages.append(f"📨 {message.text}")
            if messages:
                all_messages.append(f"Канал: {channel}\n" + "\n\n".join(messages))
        return all_messages
    except Exception as e:
        logger.error(f"Ошибка при получении сообщений из каналов: {e}")
        return ["Не удалось получить сообщения."]
    finally:
        await client.disconnect()

def register_handlers(dp: Dispatcher):
    @dp.message(Command("start"))
    async def send_welcome(message: types.Message):
        logger.info(f"Пользователь {message.from_user.id} отправил /start.")
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Добавить канал"), KeyboardButton(text="Мои каналы")],
                [KeyboardButton(text="Получить дайджест")],
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

    @dp.message(lambda message: message.text == "Получить дайджест")
    async def get_digest(message: types.Message):
        logger.info(f"Пользователь {message.from_user.id} запросил дайджест.")
        user_id = message.from_user.id
        channels = get_user_channels(user_id)

        if not channels:
            logger.info(f"У пользователя {user_id} нет каналов для получения дайджеста.")
            await message.answer("У вас пока нет добавленных каналов. Добавьте их через меню.")
            return

        messages = await fetch_messages_from_channels(channels)
        if messages:
            for msg in messages:
                await message.answer(msg)
        else:
            await message.answer("Не удалось получить сообщения из ваших каналов.")
