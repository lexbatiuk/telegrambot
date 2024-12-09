import logging
from aiogram import Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from database import add_channel, get_user_channels
from telethon.errors import RPCError
from telethon.sync import TelegramClient

logger = logging.getLogger(__name__)

async def fetch_messages_from_channels(user_channels, client):
    """
    Fetches the latest messages from all user channels using a user session.
    """
    all_messages = []
    try:
        await client.start()  # Start the user session
        for channel in user_channels:
            try:
                messages = []
                async for message in client.iter_messages(channel, limit=5):  # Last 5 messages
                    if message.text:
                        messages.append(f"📨 {message.text}")
                if messages:
                    all_messages.append(f"Channel: {channel}\n" + "\n\n".join(messages))
            except RPCError as e:
                logger.error(f"Error processing channel {channel}: {e}")
                all_messages.append(f"⚠️ Failed to fetch messages from {channel}.")
    except Exception as e:
        logger.error(f"Error initializing Telethon client: {e}")
        all_messages.append("⚠️ An error occurred while fetching messages.")
    finally:
        await client.disconnect()
    return all_messages

def register_handlers(dp: Dispatcher, client):
    @dp.message(Command("start"))
    async def send_welcome(message: types.Message):
        logger.info(f"User {message.from_user.id} sent /start.")
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Add Channel"), KeyboardButton(text="My Channels")],
                [KeyboardButton(text="Get Digest")]
            ],
            resize_keyboard=True
        )
        await message.answer("Welcome! Use the menu to manage the bot.", reply_markup=keyboard)

    @dp.message(lambda message: message.text == "Add Channel")
    async def select_channel(message: types.Message):
        logger.info(f"User {message.from_user.id} selected 'Add Channel'.")
        await message.answer("Please enter the channel name or link (e.g., @news_channel).")

    @dp.message(lambda message: message.text.startswith('@'))
    async def add_channel_handler(message: types.Message):
        user_id = message.from_user.id
        channel = message.text.strip()
        try:
            await client.start()  # Start the user session
            await client.get_entity(channel)  # Validate channel
            if add_channel(user_id, channel):
                logger.info(f"Channel {channel} added for user {user_id}.")
                await message.answer(f"Channel {channel} has been successfully added!")
            else:
                logger.warning(f"Channel {channel} is already added for user {user_id}.")
                await message.answer(f"Channel {channel} is already in your list.")
        except Exception as e:
            logger.error(f"Error adding channel {channel}: {e}")
            await message.answer(f"Failed to add channel {channel}. Please check the name.")
        finally:
            await client.disconnect()

    @dp.message(lambda message: message.text == "My Channels")
    async def show_channels(message: types.Message):
        user_id = message.from_user.id
        channels = get_user_channels(user_id)
        if channels:
            logger.info(f"User {user_id} requested their channels.")
            channel_list = "\n".join(channels)
            await message.answer(f"Your channels:\n{channel_list}")
        else:
            logger.info(f"User {user_id} has no channels added.")
            await message.answer("You have no channels added yet.")

    @dp.message(lambda message: message.text == "Get Digest")
    async def get_digest(message: types.Message):
        logger.info(f"User {message.from_user.id} requested the digest.")
        user_id = message.from_user.id
        channels = get_user_channels(user_id)

        if not channels:
            logger.info(f"User {user_id} has no channels for the digest.")
            await message.answer("You have no channels added yet. Please add them using the menu.")
            return

        messages = await fetch_messages_from_channels(channels, client)
        if messages:
            for msg in messages:
                await message.answer(msg)
        else:
            await message.answer("No new messages found in your channels.")
