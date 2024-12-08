from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from database import add_user_channel, get_user_channels
from scheduler import schedule_daily_summary

def setup_handlers(dp):
    @dp.message(Command("start"))
    async def send_welcome(message: Message):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Добавить канал", callback_data="add_channel")],
                [InlineKeyboardButton(text="Получить саммари", callback_data="get_summary")]
            ]
        )
        await message.answer("Привет! Что будем делать?", reply_markup=keyboard)

    @dp.callback_query(lambda c: c.data == "add_channel")
    async def add_channel(callback: CallbackQuery):
        await callback.message.answer("Введите название канала (@example).")
        await callback.answer()

    @dp.message(lambda msg: msg.text.startswith('@'))
    async def handle_channel_input(message: Message):
        if add_user_channel(message.from_user.id, message.text):
            await message.answer(f"Канал {message.text} добавлен!")
        else:
            await message.answer("Этот канал уже добавлен.")

    @dp.callback_query(lambda c: c.data == "get_summary")
    async def get_summary(callback: CallbackQuery):
        channels = get_user_channels(callback.from_user.id)
        if channels:
            schedule_daily_summary(callback.from_user.id, channels)
            await callback.message.answer("Саммари запланировано!")
        else:
            await callback.message.answer("Сначала добавьте каналы.")
        await callback.answer()
