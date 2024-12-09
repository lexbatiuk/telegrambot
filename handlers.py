from aiogram import Router, types
from aiogram.filters import Command
from database import add_channel, get_user_channels

def register_handlers(dp, client):
    router = Router()

    @router.message(Command("start"))
    async def send_welcome(message: types.Message):
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="Add channel"), types.KeyboardButton(text="My channels")],
                [types.KeyboardButton(text="Get digest")],
            ],
            resize_keyboard=True
        )
        await message.answer("Welcome! Use the menu to manage the bot.", reply_markup=keyboard)

    @router.message(lambda message: message.text == "Add channel")
    async def add_channel_prompt(message: types.Message):
        await message.answer("Enter the channel username (e.g., @example_channel):")

    @router.message(lambda message: message.text.startswith('@'))
    async def add_channel_handler(message: types.Message):
        user_id = message.from_user.id
        channel = message.text.strip()
        if add_channel(user_id, channel):
            await message.answer(f"Channel {channel} successfully added!")
        else:
            await message.answer(f"Channel {channel} is already added.")

    @router.message(lambda message: message.text == "My channels")
    async def show_channels(message: types.Message):
        user_id = message.from_user.id
        channels = get_user_channels(user_id)
        if channels:
            await message.answer(f"Your channels:\n" + "\n".join(channels))
        else:
            await message.answer("You haven't added any channels yet.")

    @router.message(lambda message: message.text == "Get digest")
    async def get_digest(message: types.Message):
        user_id = message.from_user.id
        channels = get_user_channels(user_id)
        if not channels:
            await message.answer("You have no channels added.")
            return

        for channel in channels:
            try:
                async for msg in client.iter_messages(channel, limit=5):
                    await message.answer(f"{channel}:\n{msg.text[:200]}...")
            except Exception as e:
                await message.answer(f"Error accessing {channel}: {e}")

    dp.include_router(router)
