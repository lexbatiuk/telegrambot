from telethon import TelegramClient
import asyncio
import os

# Environment Variables for Railway or Render
api_id = int(os.getenv('api_id'))  # Telegram API ID
api_hash = os.getenv('api_hash')  # Telegram API Hash
bot_token = os.getenv('bot_token')  # Bot Token from BotFather

# Initialize Telegram Client
client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

async def main():
    # Test the bot by sending a message to yourself
    me = await client.get_me()
    await client.send_message(me.id, "Hello from your bot running!")
    print("Message sent to yourself!")

# Run the bot
with client:
    client.loop.run_until_complete(main())
