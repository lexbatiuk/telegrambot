from aiogram import Router, types, F
from database import add_channel, get_user_channels, delete_user_data

# Create a router instance
router = Router()

@router.message(F.text.startswith("/start"))
async def start_command(message: types.Message):
    """
    Handles the /start command.
    """
    await message.answer(
        "Welcome to the bot!\n"
        "Use the following commands:\n"
        "/add_channel <channel_name> - Add a channel\n"
        "/list_channels - List your channels\n"
        "/delete_all - Delete all your data"
    )

@router.message(F.text.startswith("/add_channel"))
async def add_channel_command(message: types.Message):
    """
    Handles the /add_channel command to add a channel.
    """
    user_id = message.from_user.id
    channel_name = message.text.removeprefix("/add_channel").strip()
    if not channel_name:
        await message.reply("Please provide a channel name: /add_channel <channel_name>")
        return

    await add_channel(user_id, channel_name)
    await message.reply(f"Channel '{channel_name}' added successfully!")

@router.message(F.text.startswith("/list_channels"))
async def list_channels_command(message: types.Message):
    """
    Handles the /list_channels command to list all channels of a user.
    """
    user_id = message.from_user.id
    channels = await get_user_channels(user_id)
    if channels:
        await message.reply("Here are your channels:\n" + "\n".join(channels))
    else:
        await message.reply("No channels found. Use /add_channel to add one.")

@router.message(F.text.startswith("/delete_all"))
async def delete_all_command(message: types.Message):
    """
    Handles the /delete_all command to delete all user data.
    """
    user_id = message.from_user.id
    await delete_user_data(user_id)
    await message.reply("All your data has been deleted.")
