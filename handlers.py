from aiogram import Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from database import add_channel, get_user_channels

def register_handlers(dp: Dispatcher, client):
    @dp.message(Command("start"))
    async def send_welcome(message: types.Message):
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Add Channel"), KeyboardButton(text="My Channels")],
                [KeyboardButton(text="Get Digest")],
            ],
            resize_keyboard=True
        )
        await message.answer("Welcome! Use the menu below to interact with the bot.", reply_markup=keyboard)

    @dp.message(lambda msg: msg.text == "Add Channel")
    async def add_channel_prompt(message: types.Message):
        await message.answer("Please send the channel username (e.g., @example_channel).")

    @dp.message(lambda msg: msg.text.startswith('@'))
    async def add_channel_handler(message: types.Message):
        user_id = message.from_user.id
        channel = message.text.strip()
        if add_channel(user_id, channel):
            await message.answer(f"Channel {channel} added!")
        else:
            await message.answer(f"Channel {channel} is already added.")

    @dp.message(lambda msg: msg.text == "My Channels")
    async def list_channels(message: types.Message):
        user_id = message.from_user.id
        channels = get_user_channels(user_id)
        if channels:
            await message.answer("Your channels:\n" + "\n".join(channels))
        else:
            await message.answer("You haven't added any channels yet.")

    @dp.message(lambda msg: msg.text == "Get Digest")
    async def get_digest(message: types.Message):
        user_id = message.from_user.id
        channels = get_user_channels(user_id)
        if not channels:
            await message.answer("You haven't added any channels yet.")
            return
        for channel in channels:
            try:
                async for msg in client.iter_messages(channel, limit=5):
                    await message.answer(f"{channel}:\n{msg.text[:200]}...")
            except Exception as e:
                await message.answer(f"Error accessing {channel}: {e}")
