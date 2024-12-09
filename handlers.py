from aiogram import Router, types
from aiogram.filters import Command
from database import add_channel, get_user_channels

# Инициализация роутера
router = Router()

# Хендлер для команды /start
@router.message(Command(commands=["start"]))
async def start_command_handler(message: types.Message):
    """
    Обработчик команды /start. Приветствие пользователя.
    """
    await message.reply("Welcome! Bot is ready to serve.")

# Хендлер для команды /channels
@router.message(Command(commands=["channels"]))
async def list_channels_handler(message: types.Message):
    """
    Обработчик команды /channels. Вывод списка каналов пользователя.
    """
    user_channels = await get_user_channels(message.from_user.id)
    if user_channels:
        channels_list = "\n".join(user_channels)
        await message.reply(f"Here are your channels:\n{channels_list}")
    else:
        await message.reply("You don't have any channels saved.")

# Хендлер для добавления канала через команду /add_channel <channel_name>
@router.message(Command(commands=["add_channel"]))
async def add_channel_handler(message: types.Message):
    """
    Обработчик команды /add_channel. Добавление канала в базу данных.
    """
    if len(message.text.split()) < 2:
        await message.reply("Please provide the channel name. Usage: /add_channel <channel_name>")
        return

    channel_name = message.text.split(maxsplit=1)[1]
    success = await add_channel(message.from_user.id, channel_name)
    if success:
        await message.reply(f"Channel {channel_name} added successfully!")
    else:
        await message.reply(f"Failed to add channel {channel_name}. It might already exist.")

# Хендлер для помощи /help
@router.message(Command(commands=["help"]))
async def help_command_handler(message: types.Message):
    """
    Обработчик команды /help. Отправляет список доступных команд.
    """
    help_text = (
        "Available commands:\n"
        "/start - Start the bot\n"
        "/channels - List your saved channels\n"
        "/add_channel <channel_name> - Add a channel to your list\n"
        "/help - Show this help message"
    )
    await message.reply(help_text)
