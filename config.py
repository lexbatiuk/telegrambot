import os

class Config:
    BOT_TOKEN = os.getenv("bot_token")
    API_ID = os.getenv("api_id")
    API_HASH = os.getenv("api_hash")
    DATABASE_URL = os.getenv("DATABASE_URL")
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")
    TELEGRAM_PHONE = os.getenv("TELEGRAM_PHONE")
    TELEGRAM_PASSWORD = os.getenv("TELEGRAM_PASSWORD")
    PORT = int(os.getenv("PORT", 3000))
    ALLOWED_USER_ID = os.getenv("ALLOWED_USER_ID")

    @classmethod
    def validate(cls):
        missing_vars = [
            var_name for var_name, var_value in cls.__dict__.items()
            if not var_name.startswith("__") and var_value is None
        ]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
