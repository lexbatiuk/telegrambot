import os


class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    API_ID = os.getenv("API_ID")
    API_HASH = os.getenv("API_HASH")
    DATABASE_URL = os.getenv("DATABASE_URL")
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")
    TELEGRAM_PHONE = os.getenv("TELEGRAM_PHONE")
    TELEGRAM_PASSWORD = os.getenv("TELEGRAM_PASSWORD")
    PORT = int(os.getenv("PORT", 3000))

    @classmethod
    def validate(cls):
        """Проверка всех обязательных переменных окружения."""
        required_vars = [
            cls.BOT_TOKEN,
            cls.API_ID,
            cls.API_HASH,
            cls.DATABASE_URL,
            cls.WEBHOOK_URL,
            cls.TELEGRAM_PHONE,
        ]
        missing_vars = [
            var_name for var_name, value in vars(cls).items() if var_name.isupper() and not value
        ]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
