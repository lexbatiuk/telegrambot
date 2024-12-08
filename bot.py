from telethon import TelegramClient
import asyncio

# Environment Variables for Render
import os
api_id = int(os.getenv('25028817'))  # Telegram API ID
api_hash = os.getenv('5a53c8a24269d4d6bed55de5a431811c')  # Telegram API Hash
bot_token = os.getenv('7708475257:AAHaMc2mE24P9mHvOKl59bHYaAMr9q2eGYQ')  # Bot Token from BotFather

# Initialize Telegram Client
client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

async def main():
    # Test the bot by sending a message to yourself
    me = await client.get_me()
    await client.send_message(me.id, "Hello from your bot running on Render!")
    print("Message sent to yourself!")

# Run the bot
with client:
    client.loop.run_until_complete(main())
