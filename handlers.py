from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command


# Создаем клавиатуру с кнопками
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
        "Привет! Используй кнопки ниже для взаимодействия с ботом:",
        reply_markup=keyboard
    )


# Обработчик команды "Список каналов"
async def list_channels(message: types.Message, user_channels):
    user_id = message.from_user.id
    if user_id in user_channels and user_channels[user_id]:
        channels = "\n".join(user_channels[user_id])
        await message.answer(f"Вот твои каналы:\n{channels}")
    else:
        await message.answer("У тебя пока нет добавленных каналов.")


# Регистрация обработчиков
def register_handlers(dp, user_channels):
    dp.message.register(send_welcome, Command("start"))
    dp.message.register(lambda message: list_channels(message, user_channels), Command("Список каналов"))
