from aiogram import Router, types
from aiogram.types import Message
from database import add_channel, get_user_channels

router = Router()

@router.message(commands=["start"])
async def send_welcome(message: Message):
    await message.answer("Welcome! Use /add_channel to add a channel or /my_channels to view your channels.")

@router.message(commands=["add_channel"])
async def add_channel_handler(message: Message):
    user_id = message.from_user.id
    if message.text.startswith('@'):
        channel = message.text.split()[1]
        if add_channel(user_id, channel):
            await message.answer(f"Channel {channel} added!")
        else:
            await message.answer(f"Channel {channel} already added.")

@router.message(commands=["my_channels"])
async def my_channels_handler(message: Message):
    user_id = message.from_user.id
    channels = get_user_channels(user_id)
    if channels:
        await message.answer("Your channels:\n" + "\n".join(channels))
    else:
        await message.answer("You have no added channels.")
