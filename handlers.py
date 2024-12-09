from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from database import add_channel, get_user_channels

router = Router()

# Обработчик команды /start
@router.message(Command("start"))
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
@router.message(lambda message: message.text == "Add Channel")
async def select_channel(message: types.Message):
    await message.answer("Please enter the channel name or link (e.g., @example_channel).")

# Обработчик добавления канала
@router.message(lambda message: message.text.startswith('@'))
async def add_channel_handler(message: types.Message):
    user_id = message.from_user.id
    channel = message.text.strip()
    if add_channel(user_id, channel):
        await message.answer(f"Channel {channel} successfully added!")
    else:
        await message.answer(f"Channel {channel} is already added.")

# Обработчик кнопки "My Channels"
@router.message(lambda message: message.text == "My Channels")
async def show_channels(message: types.Message):
    user_id = message.from_user.id
    channels = get_user_channels(user_id)
    if channels:
        channel_list = "\n".join(channels)
        await message.answer(f"Your channels:\n{channel_list}")
    else:
        await message.answer("You have no added channels yet.")

# Обработчик кнопки "Get Digest"
@router.message(lambda message: message.text == "Get Digest")
async def get_digest(message: types.Message):
    user_id = message.from_user.id
    channels = get_user_channels(user_id)
    if not channels:
        await message.answer("You have no channels to fetch digest from.")
        return
    await message.answer("Fetching digest... (this is a placeholder response).")

def register_handlers(dp):
    dp.include_router(router)
