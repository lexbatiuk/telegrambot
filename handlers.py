from aiogram import Router
from aiogram.types import Message
from database import add_channel, get_user_channels

router = Router()


@router.message(commands=["start"])
async def start_command(message: Message):
    await message.answer("Welcome to the bot!")


@router.message(commands=["add_channel"])
async def add_channel_command(message: Message):
    args = message.get_args()
    if not args:
        await message.answer("Please provide a channel ID.")
        return

    await add_channel(message.from_user.id, args)
    await message.answer(f"Channel {args} added successfully.")


@router.message(commands=["list_channels"])
async def list_channels_command(message: Message):
    channels = await get_user_channels(message.from_user.id)
    if not channels:
        await message.answer("You have no channels added.")
        return

    channel_list = "\n".join([record["channel_id"] for record in channels])
    await message.answer(f"Your channels:\n{channel_list}")
