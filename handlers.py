from aiogram import Router, types, F
from database import add_channel, get_user_channels

router = Router()

@router.message(F.text.startswith("/start"))
async def start_command(message: types.Message):
    """
    Handles the /start command.
    """
    await message.answer("Welcome! Use /add_channel or /list_channels commands.")

@router.message(F.text.startswith("/add_channel"))
async def add_channel_command(message: types.Message):
    """
    Handles the /add_channel command.
    """
    user_id = message.from_user.id
    channel_name = message.text.removeprefix("/add_channel").strip()
    if not channel_name:
        await message.reply("Provide channel name: /add_channel <channel_name>")
        return

    await add_channel(user_id, channel_name)
    await message.reply(f"Channel '{channel_name}' added!")

@router.message(F.text.startswith("/list_channels"))
async def list_channels_command(message: types.Message):
    """
    Handles the /list_channels command.
    """
    user_id = message.from_user.id
    channels = await get_user_channels(user_id)
    if channels:
        await message.reply("Your channels:\n" + "\n".join(channels))
    else:
        await message.reply("No channels found.")
