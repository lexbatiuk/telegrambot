import logging
from aiogram import Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from database import add_channel, get_user_channels

logger = logging.getLogger(__name__)

def register_handlers(dp: Dispatcher, client):
    @dp.message(commands=["start"])
    async def send_welcome(message: types.Message):
        """
        Sends a welcome message and displays menu buttons.
        """
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Add Channel"), KeyboardButton(text="My Channels")],
                [KeyboardButton(text="Get Digest")]
            ],
            resize_keyboard=True
        )
        await message.answer("Welcome! Use the menu to manage the bot.", reply_markup=keyboard)

    @dp.message(lambda message: message.text == "Add Channel")
    async def add_channel_prompt(message: types.Message):
        """
        Prompts the user to add a channel.
        """
        await message.answer("Please enter the channel username (e.g., @example_channel).")

    @dp.message(lambda message: message.text.startswith("@"))
    async def handle_channel_addition(message: types.Message):
        """
        Adds the channel to the database.
        """
        user_id = message.from_user.id
        channel = message.text.strip()
        if add_channel(user_id, channel):
            await message.answer(f"Channel {channel} added successfully!")
        else:
            await message.answer(f"Channel {channel} is already added.")

    @dp.message(lambda message: message.text == "My Channels")
    async def show_channels(message: types.Message):
        """
        Displays the user's subscribed channels.
        """
        user_id = message.from_user.id
        channels = get_user_channels(user_id)
        if channels:
            await message.answer("Your channels:\n" + "\n".join(channels))
        else:
            await message.answer("You have no subscribed channels.")

    @dp.message(lambda message: message.text == "Get Digest")
    async def get_digest(message: types.Message):
        """
        Sends the latest messages from the user's channels.
        """
        user_id = message.from_user.id
        channels = get_user_channels(user_id)
        if not channels:
            await message.answer("You have no subscribed channels.")
            return
        
        for channel in channels:
            try:
                async for msg in client.iter_messages(channel, limit=5):
                    if msg.text:
                        await message.answer(f"{channel}: {msg.text}")
            except Exception as e:
                logger.error(f"Error fetching messages from {channel}: {e}")
                await message.answer(f"Could not fetch messages from {channel}.")
