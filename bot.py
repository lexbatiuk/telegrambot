import os

async def main():
    logger.info("Starting bot...")
    # Initialize the database
    init_db()
    logger.info("Database initialized.")

    # Start Telethon client
    try:
        await client.start()
        logger.info("Telethon client started. You are now authorized.")
    except Exception as e:
        logger.error("Authorization required. Logging in using TELEGRAM_PHONE.")
        phone = os.getenv("TELEGRAM_PHONE")
        if not phone:
            raise ValueError("Environment variable `TELEGRAM_PHONE` is missing.")
        await client.sign_in(phone=phone)
        code = input("Please enter the code you received: ")
        await client.sign_in(code=code)

    # Set webhook
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f"Webhook set at {WEBHOOK_URL}.")

    # Setup scheduler
    setup_scheduler(bot)
    logger.info("Scheduler initialized.")

    # Start aiohttp server
    app = web.Application()
    app.router.add_post('/webhook', handle_webhook)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=PORT)
    await site.start()
    logger.info(f"Webhook server started on port {PORT}.")

    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        await bot.delete_webhook()
        logger.info("Webhook removed.")
        await client.disconnect()
        await shutdown_scheduler()
        logger.info("Bot stopped.")
