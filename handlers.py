from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from database import add_channel, get_user_channels
import logging

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("start"))
async def send_welcome(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Add Channel"), KeyboardButton(text="My Channels")],
            [KeyboardButton(text="Get Digest")]
        ],
        resize_keyboard=True
    )
    await message.answer("Welcome! Use the menu below to navigate.", reply_markup=keyboard)

@router.message(lambda message: message.text == "Add Channel")
async def select_channel(message: types.Message):
    await message.answer("Please enter the channel name or link (e.g., @channelname).")

@router.message(lambda message: message.text.startswith("@"))
async def add_channel_handler(message: types.Message):
    user_id = message.from_user.id
    channel = message.text.strip()
    if add_channel(user_id, channel):
        await message.answer(f"The channel {channel} has been added!")
        logger.info(f"Channel {channel} added for user {user_id}.")
    else:
        await message.answer(f"The channel {channel} is already added.")

@router.message(lambda message: message.text == "My Channels")
async def show_channels(message: types.Message):
    user_id = message.from_user.id
    channels = get_user_channels(user_id)
    if channels:
        await message.answer("Your channels:\n" + "\n".join(channels))
    else:
        await message.answer("You have no added channels.")

@router.message(lambda message: message.text == "Get Digest")
async def get_digest(message: types.Message):
    user_id = message.from_user.id
    channels = get_user_channels(user_id)
    if not channels:
        await message.answer("You don't have any channels to fetch a digest from.")
        return
    await message.answer("Fetching digest...\n(Placeholder for digest content)")
    logger.info(f"User {user_id} requested a digest from channels: {channels}")
