from aiogram import Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from database import add_channel, get_user_channels

def register_handlers(dp: Dispatcher, client):
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
        await message.answer("Welcome! Use the menu to manage the bot.", reply_markup=keyboard)

    # Обработчик кнопки "Add Channel"
    @dp.message(lambda message: message.text == "Add Channel")
    async def select_channel(message: types.Message):
        await message.answer("Please enter the name or link of the channel (e.g., @example_channel).")

    # Обработчик добавления канала
    @dp.message(lambda message: message.text.startswith('@'))
    async def add_channel_handler(message: types.Message):
        user_id = message.from_user.id
        channel = message.text.strip()
        if add_channel(user_id, channel):
            await message.answer(f"Channel {channel} has been added successfully!")
        else:
            await message.answer(f"Channel {channel} is already added.")

    # Обработчик кнопки "My Channels"
    @dp.message(lambda message: message.text == "My Channels")
    async def show_channels(message: types.Message):
        user_id = message.from_user.id
        channels = get_user_channels(user_id)
        if channels:
            channel_list = "\n".join(channels)
            await message.answer(f"Your channels:\n{channel_list}")
        else:
            await message.answer("You have no channels added yet.")

    # Обработчик кнопки "Get Digest"
    @dp.message(lambda message: message.text == "Get Digest")
    async def get_digest(message: types.Message):
        user_id = message.from_user.id
        channels = get_user_channels(user_id)
        if not channels:
            await message.answer("You have no channels added yet.")
            return

        await message.answer("Fetching digest. Please wait...")
        for channel in channels:
            try:
                async for msg in client.iter_messages(channel, limit=5):  # Последние 5 сообщений
                    if msg.text:
                        await message.answer(f"Message from {channel}:\n{msg.text}")
            except Exception as e:
                await message.answer(f"Failed to fetch messages from {channel}: {e}")

    # Регистрация обработчиков
    dp.include_router(send_welcome)
    dp.include_router(select_channel)
    dp.include_router(add_channel_handler)
    dp.include_router(show_channels)
    dp.include_router(get_digest)
