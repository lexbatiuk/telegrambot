from aiogram import Router, types
from database import add_channel, get_user_channels

router = Router()

@router.message(commands=["start"])
async def start_command(message: types.Message):
    """
    Handles the /start command.
    """
    await message.answer("Welcome to the bot! Use /add_channel to add channels.")

@router.message(commands=["add_channel"])
async def add_channel_command(message: types.Message):
    """
    Handles the /add_channel command to add a channel.
    """
    user_id = message.from_user.id
    channel_name = message.get_args()
    if not channel_name:
        await message.reply("Please provide a channel name. Usage: /add_channel <channel_name>")
        return

    await add_channel(user_id, channel_name)
    await message.reply(f"Channel '{channel_name}' added!")

@router.message(commands=["list_channels"])
async def list_channels_command(message: types.Message):
    """
    Handles the /list_channels command to list user's channels.
    """
    user_id = message.from_us
