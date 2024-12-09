from aiogram import Router, types, F
from database import add_channel, get_user_channels

router = Router()

@router.message(F.text.startswith("/start"))
async def start_command(message: types.Message):
    """
    Handles the /start command.
    """
    await message.answer(
        "Welcome! Use the following commands:\n"
        "/add_channel <channel_name> - Add a new channel.\n"
        "/list_channels - List your channels."
    )

@router.message(F.text.startswith("/add_channel"))
async def add_channel_command(message: types.Message):
    """
    Handles the /add_channel command.
    """
    user_id = message.from_user.id
    channel_name = message.text.removeprefix("/add_channel").strip()
    
    if not channel_name:
        await message.reply("Please provide a channel name: /add_channel <channel_name>")
        return

    try:
        await add_channel(user_id, channel_name)
        await message.reply(f"Channel '{channel_name}' has been added successfully!")
    except Exception as e:
        await message.reply(f"Failed to add channel '{channel_name}': {e}")

@router.message(F.text.startswith("/list_channels"))
async def list_channels_command(message: types.Message):
    """
    Handles the /list_channels command.
    """
    user_id = message.from_user.id
    try:
        channels = await get_user_channels(user_id)
        if channels:
            await message.reply("Your channels:\n" + "\n".join(channels))
        else:
            await message.reply("You don't have any channels added yet.")
    except Exception as e:
        await message.reply(f"Failed to retrieve channels: {e}")
