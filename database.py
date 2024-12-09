import asyncpg
import os

DB_DSN = os.getenv("DATABASE_URL")  # Получаем URL базы данных из переменных окружения

async def init_db():
    """
    Initializes the database connection.
    """
    conn = await asyncpg.connect(DB_DSN)
    await conn.execute("""
    CREATE TABLE IF NOT EXISTS user_channels (
        id SERIAL PRIMARY KEY,
        user_id BIGINT NOT NULL,
        channel_name TEXT NOT NULL
    )
    """)
    await conn.close()

async def add_channel(user_id, channel_name):
    """
    Adds a new channel for the user.
    """
    conn = await asyncpg.connect(DB_DSN)
    await conn.execute(
        "INSERT INTO user_channels (user_id, channel_name) VALUES ($1, $2)",
        user_id, channel_name
    )
    await conn.close()

async def get_user_channels(user_id):
    """
    Retrieves all channels associated with a user.
    """
    conn = await asyncpg.connect(DB_DSN)
    rows = await conn.fetch(
        "SELECT channel_name FROM user_channels WHERE user_id = $1",
        user_id
    )
    await conn.close()
    return [row['channel_name'] for row in rows]

async def delete_user_data(user_id):
    """
    Deletes all data associated with a user.
    """
    conn = await asyncpg.connect(DB_DSN)
    await conn.execute(
        "DELETE FROM user_channels WHERE user_id = $1",
        user_id
    )
    await conn.close()
