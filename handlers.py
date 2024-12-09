from aiogram import Router, types
from aiogram.filters import Command
from database import add_channel, get_user_channels

router = Router()  # Создаем объект Router

@router.message(Command("start"))
async def send_welcome(message: types.Message):
    """
    Обработчик команды /start.
    """
    await message.answer("Welcome! Use the menu to interact with the bot.")

@router.message(lambda message: message.text == "Add Channel")
async def select_channel(message: types.Message):
    """
    Обработчик для кнопки 'Add Channel'.
    """
    await message.answer("Please enter the channel username (e.g., @example_channel).")

@router.message(lambda message: message.text.startswith('@'))
async def add_channel_handler(message: types.Message):
    """
    Обработчик для добавления канала.
    """
    user_id = message.from_user.id
    channel = message.text.strip()
    if add_channel(user_id, channel):
        await message.answer(f"Channel {channel} has been successfully added!")
    else:
        await message.answer(f"Channel {channel} is already added.")

@router.message(lambda message: message.text == "My Channels")
async def show_channels(message: types.Message):
    """
    Обработчик для показа списка каналов.
    """
    user_id = message.from_user.id
    channels = get_user_channels(user_id)
    if channels:
        channel_list = "\n".join(channels)
        await message.answer(f"Your channels:\n{channel_list}")
    else:
        await message.answer("You don't have any channels added yet.")
