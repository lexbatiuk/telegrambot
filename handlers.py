from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from database import add_channel, get_user_channels

router = Router()

@router.message(commands=["start"])
async def send_welcome(message: Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Add Channel"), KeyboardButton(text="My Channels")],
            [KeyboardButton(text="Get Digest")]
        ],
        resize_keyboard=True
    )
    await message.answer("Welcome! Use the menu to manage the bot.", reply_markup=keyboard)

@router.message(lambda message: message.text == "Add Channel")
async def select_channel(message: Message):
    await message.answer("Enter the channel name or link (e.g., @example_channel).")

@router.message(lambda message: message.text.startswith('@'))
async def add_channel_handler(message: Message):
    user_id = message.from_user.id
    channel = message.text.strip()
    if add_channel(user_id, channel):
        await message.answer(f"Channel {channel} successfully added!")
    else:
        await message.answer(f"Channel {channel} is already added.")

@router.message(lambda message: message.text == "My Channels")
async def show_channels(message: Message):
    user_id = message.from_user.id
    channels = get_user_channels(user_id)
    if channels:
        await message.answer("Your channels:\n" + "\n".join(channels))
    else:
        await message.answer("You have no channels added yet.")

@router.message(lambda message: message.text == "Get Digest")
async def get_digest(message: Message):
    await message.answer("This feature is under construction!")
