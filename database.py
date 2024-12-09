import asyncpg
import os

# Получение строки подключения из переменных окружения
DB_DSN = os.getenv("DATABASE_URL")  # Railway предоставляет эту переменную

if not DB_DSN:
    raise ValueError("DATABASE_URL is not set in the environment variables.")

async def init_db():
    """
    Инициализирует соединение с базой данных и создает таблицы, если их нет.
    """
    conn = await asyncpg.connect(dsn=DB_DSN)
    try:
        # Создаем таблицу user_channels
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS user_channels (
                user_id BIGINT NOT NULL,
                channel_name TEXT NOT NULL,
                UNIQUE(user_id, channel_name)
            )
        """)
        print("Database initialized successfully.")
    finally:
        await conn.close()

async def add_channel(user_id: int, channel_name: str):
    """
    Добавляет канал в базу данных для указанного пользователя.
    """
    conn = await asyncpg.connect(dsn=DB_DSN)
    try:
        await conn.execute(
            "INSERT INTO user_channels (user_id, channel_name) VALUES ($1, $2) ON CONFLICT DO NOTHING",
            user_id, channel_name
        )
        print(f"Channel '{channel_name}' added for user {user_id}.")
    finally:
        await conn.close()

async def get_user_channels(user_id: int):
    """
    Возвращает все каналы для указанного пользователя.
    """
    conn = await asyncpg.connect(dsn=DB_DSN)
    try:
        rows = await conn.fetch(
            "SELECT channel_name FROM user_channels WHERE user_id = $1",
            user_id
        )
        return [row['channel_name'] for row in rows]
    finally:
        await conn.close()

async def delete_user_data(user_id: int):
    """
    Удаляет все данные пользователя из базы данных.
    """
    conn = await asyncpg.connect(dsn=DB_DSN)
    try:
        await conn.execute(
            "DELETE FROM user_channels WHERE user_id = $1",
            user_id
        )
        print(f"All data for user {user_id} has been deleted.")
    finally:
        await conn.close()
