import os

class Config:
    BOT_TOKEN = os.getenv("bot_token")
    API_ID = os.getenv("api_id")
    API_HASH = os.getenv("api_hash")
    WEBHOOK_URL = os.getenv("webhook_url")
    TELEGRAM_PHONE = os.getenv("TELEGRAM_PHONE")
    PORT = int(os.getenv("port", 3000))

    @classmethod
    def validate(cls):
        missing_vars = [var for var in cls.__dict__ if var.isupper() and not getattr(cls, var)]
        if missing_vars:
            raise ValueError(f"Missing environment variables: {', '.join(missing_vars)}")

Config.validate()
