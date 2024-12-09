from aiogram import Router
from aiogram.types import Message
from database import add_channel, get_user_channels

router = Router()

@router.message(commands=["start"])
async def send_welcome(message: Message):
    await message.answer("Welcome! Use /add_channel to add channels or /list_channels to view your channels.")

@router.message(commands=["add_channel"])
async def add_channel_handler(message: Message):
    user_id = message.from_user.id
    channel = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
    if channel:
        if add_channel(user_id, channel):
            await message.answer(f"Channel {channel} has been added!")
        else:
            await message.answer(f"Channel {channel} is already in your list.")
    else:
        await message.answer("Please provide the channel name (e.g., /add_channel @example).")

@router.message(commands=["list_channels"])
async def list_channels_handler(message: Message):
    user_id = message.from_user.id
    channels = get_user_channels(user_id)
    if channels:
        await message.answer(f"Your channels:\n" + "\n".join(channels))
    else:
        await message.answer("You have no channels added.")
