from aiogram import Router, types
from aiogram.filters import Command
from database import add_channel, get_user_channels

router = Router()

@router.message(Command("start"))
async def start_command_handler(message: types.Message):
    """
    Handles the /start command.
    """
    await message.answer("Welcome! Bot is ready to serve.")

@router.message(Command("channels"))
async def list_channels_handler(message: types.Message):
    """
    Handles the /channels command to list user's channels.
    """
    user_channels = await get_user_channels(message.from_user.id)
    if user_channels:
        channels_list = "\n".join(user_channels)
        await message.answer(f"Here are your channels:\n{channels_list}")
    else:
        await message.answer("You don't have any channels saved.")
