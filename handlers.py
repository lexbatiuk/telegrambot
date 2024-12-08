from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command


# Основное меню
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Добавить канал")],
        [KeyboardButton(text="Получить саммари")],
        [KeyboardButton(text="Список каналов")]
    ],
    resize_keyboard=True
)


# Обработчик команды /start
async def send_welcome(message: types.Message):
    await message.answer(
        "Привет! Этот бот помогает собирать новости из каналов и создавать их краткое саммари. "
        "Воспользуйся меню ниже для начала работы.",
        reply_markup=keyboard
    )


# Обработчик кнопки "Список каналов"
async def list_channels(message: types.Message, user_channels):
    user_id = message.from_user.id
    if user_id in user_channels and user_channels[user_id]:
        channels = "\n".join(user_channels[user_id])
        await message.answer(f"Вот твои каналы:\n{channels}")
    else:
        await message.answer("У тебя пока нет добавленных каналов. Нажми 'Добавить канал', чтобы начать.")


# Обработчик кнопки "Добавить канал"
async def add_channel(message: types.Message, user_channels):
    user_id = message.from_user.id
    await message.answer("Введите название или ссылку на канал (например, @example_channel).")
    if user_id not in user_channels:
        user_channels[user_id] = []


# Обработка текстовых сообщений для добавления канала
async def save_channel(message: types.Message, user_channels):
    user_id = message.from_user.id
    channel = message.text.strip()
    if user_id in user_channels and channel not in user_channels[user_id]:
        user_channels[user_id].append(channel)
        await message.answer(f"Канал {channel} успешно добавлен!")
    elif channel in user_channels.get(user_id, []):
        await message.answer(f"Канал {channel} уже добавлен.")
    else:
        await message.answer("Что-то пошло не так. Попробуй еще раз.")


# Регистрация обработчиков
def register_handlers(dp, user_channels):
    dp.message.register(send_welcome, Command("start"))
    dp.message.register(lambda msg: list_channels(msg, user_channels), Command("Список каналов"))
    dp.message.register(lambda msg: add_channel(msg, user_channels), lambda msg: msg.text == "Добавить канал")
    dp.message.register(lambda msg: save_channel(msg, user_channels), lambda msg: msg.text.startswith("@"))
