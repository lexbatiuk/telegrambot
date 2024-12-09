from telethon.sync import TelegramClient
from config import Config
import logging

logger = logging.getLogger(__name__)
client = TelegramClient("user_session", Config.API_ID, Config.API_HASH)

async def start_telethon_client():
    async def code_callback():
        logger.info("Waiting for the confirmation code...")
        return Config.TELEGRAM_PHONE

    async def password_callback():
        logger.info("No password required.")
        return None

    await client.start(
        phone=lambda: Config.TELEGRAM_PHONE,
        code_callback=code_callback,
        password_callback=password_callback,
    )
    logger.info("Telethon client started.")
