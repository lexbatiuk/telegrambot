from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Планировщик задач
async def scheduled_task(client, bot, user_id, channels):
    for channel in channels:
        async for message in client.iter_messages(channel, limit=5):
            text = message.text
            if text:
                await bot.send_message(user_id, f"Новое сообщение из {channel}: {text[:200]}")

# Функция для запуска планировщика
async def start_scheduler(client, bot):
    scheduler = AsyncIOScheduler()
    # Пример задачи для пользователя
    scheduler.add_job(scheduled_task, 'interval', hours=24, args=(client, bot, 12345678, ["@example_channel"]))
    scheduler.start()
