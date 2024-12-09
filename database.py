import asyncpg
import os

# Получаем строку подключения к базе данных из переменной окружения
DB_DSN = os.getenv("DATABASE_URL")  # Railway автоматически предоставляет эту переменную

async def init_db():
    """
    Initializes the database connection and creates necessary tables if they don't exist.
    """
    conn = await asyncpg.connect(dsn=DB_DSN)
    try:
        # Создание таблицы для хранения данных о каналах
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS user_channels (
                user_id BIGINT NOT NULL,
                channel_id BIGINT NOT NULL,
                UNIQUE(user_id, channel_id)
            )
        """)
        print("Database initialized successfully.")
    finally:
        await conn.close()

async def add_channel(user_id: int, channel_id: int):
    """
    Adds a channel to the database for a given user.
    """
    conn = await asyncpg.connect(dsn=DB_DSN)
    try:
        await conn.execute(
            "INSERT INTO user_channels (user_id, channel_id) VALUES ($1, $2) ON CONFLICT DO NOTHING",
            user_id, channel_id
        )
        print(f"Channel {channel_id} added for user {user_id}.")
    finally:
        await conn.close()

async def get_user_channels(user_id: int):
    """
    Retrieves all channels for a given user from the database.
    """
    conn = await asyncpg.connect(dsn=DB_DSN)
    try:
        rows = await conn.fetch(
            "SELECT channel_id FROM user_channels WHERE user_id = $1",
            user_id
        )
        return [row['channel_id'] for row in rows]
    finally:
        await conn.close()

async def delete_user_data(user_id: int):
    """
    Deletes all data related to a specific user from the database.
    """
    conn = await asyncpg.connect(dsn=DB_DSN)
    try:
        await conn.execute(
            "DELETE FROM user_channels WHERE user_id = $1",
            user_id
        )
        print(f"Data for user {user_id} has been deleted.")
    finally:
        await conn.close()

async def get_channels():
    """
    Retrieves all unique channels from the database.
    """
    conn = await asyncpg.connect(dsn=DB_DSN)
    try:
        rows = await conn.fetch("SELECT DISTINCT channel_id FROM user_channels")
        return [row['channel_id'] for row in rows]
    finally:
        await conn.close()
