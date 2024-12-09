import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from database import init_db

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Environment variables
BOT_TOKEN = os.getenv("bot_token")
API_ID = os.getenv("api_id")
API_HASH = os.getenv("api_hash")
TELEGRAM_PHONE = os.getenv("TELEGRAM_PHONE")
SESSION_STRING = os.getenv("TELEGRAM_SESSION", None)

# Verify environment variables
required_vars = [BOT_TOKEN, API_ID, API_HASH, TELEGRAM_PHONE]
missing_vars = [var for var in required_vars if not var]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Bot and Dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Telethon client
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
auth_state = {"waiting_for_code": False}


# Command: Start
@dp.message(commands=["start"])
async def start_command(message: types.Message):
    """
    Sends a welcome message with a button to request the code.
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Запросить код", callback_data="request_code")]]
    )
    await message.answer("Добро пожаловать! Нажмите кнопку ниже, чтобы запросить код авторизации.", reply_markup=keyboard)


# Callback: Request Code
@dp.callback_query(lambda c: c.data == "request_code")
async def request_code(callback_query: types.CallbackQuery):
    """
    Handles the 'Request Code' button press.
    """
    if auth_state["waiting_for_code"]:
        await callback_query.message.edit_text("Уже был отправлен запрос на код. Пожалуйста, введите код.")
        return

    try:
        await client.connect()
        if not await client.is_user_authorized():
            await client.send_code_request(TELEGRAM_PHONE)
            auth_state["waiting_for_code"] = True
            await callback_query.message.edit_text(
                "Код отправлен на ваш Telegram-аккаунт. Введите его с помощью команды `/auth_code <код>`."
            )
        else:
            await callback_query.message.edit_text("Вы уже авторизованы.")
    except Exception as e:
        logger.error(f"Ошибка при запросе кода: {e}")
        await callback_query.message.edit_text(f"Ошибка при запросе кода: {e}")


# Command: Enter Authorization Code
@dp.message(commands=["auth_code"])
async def auth_code_command(message: types.Message):
    """
    Handles the /auth_code command to complete the login process.
    """
    code = message.text.removeprefix("/auth_code").strip()
    if not code:
        await message.reply("Введите корректный код в формате: `/auth_code <код>`")
        return

    if not auth_state["waiting_for_code"]:
        await message.reply("Запрос на авторизацию не был отправлен. Нажмите кнопку 'Запросить код'.")
        return

    try:
        await client.sign_in(TELEGRAM_PHONE, code)
        session_string = client.session.save()
        os.environ["TELEGRAM_SESSION"] = session_string
        auth_state["waiting_for_code"] = False
        logger.info("Авторизация прошла успешно, сессия сохранена.")
        await message.reply("Авторизация прошла успешно!")
    except Exception as e:
        logger.error(f"Ошибка при авторизации: {e}")
        await message.reply(f"Ошибка при авторизации: {e}")


async def main():
    """
    Main function to initialize and run the bot.
    """
    logger.info("Starting bot...")

    # Initialize the database
    await init_db()
    logger.info("Database initialized successfully.")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
