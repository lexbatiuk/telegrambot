import asyncpg
import os
import logging

# Настройка логирования
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Получаем строку подключения к базе данных из переменной окружения
DB_DSN = os.getenv("DATABASE_URL")  # Railway автоматически предоставляет эту переменную

if not DB_DSN:
    raise ValueError("DATABASE_URL is not set in the environment variables.")

# Глобальный пул соединений
pool = None

async def init_db():
    """
    Initializes the database connection pool and creates necessary tables if they don't exist.
    """
    global pool
    try:
        pool = await asyncpg.create_pool(dsn=DB_DSN)
        logger.info("Database connection pool created successfully.")

        # Создаем таблицу, если она не существует
        async with pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS user_channels (
                    user_id BIGINT NOT NULL,
                    channel_id BIGINT NOT NULL,
                    UNIQUE(user_id, channel_id)
                )
            """)
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing the database: {e}")
        raise

async def add_channel(user_id: int, channel_id: int):
    """
    Adds a channel to the database for a given user.
    """
    global pool
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO user_channels (user_id, channel_id) VALUES ($1, $2) ON CONFLICT DO NOTHING",
                user_id, channel_id
            )
        logger.info(f"Channel {channel_id} added for user {user_id}.")
    except Exception as e:
        logger.error(f"Error adding channel {channel_id} for user {user_id}: {e}")
        raise

async def get_user_channels(user_id: int):
    """
    Retrieves all channels for a given user from the database.
    """
    global pool
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT channel_id FROM user_channels WHERE user_id = $1",
                user_id
            )
        return [row['channel_id'] for row in rows]
    except Exception as e:
        logger.error(f"Error retrieving channels for user {user_id}: {e}")
        raise

async def delete_user_data(user_id: int):
    """
    Deletes all data related to a specific user from the database.
    """
    global pool
    try:
        async with pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM user_channels WHERE user_id = $1",
                user_id
            )
        logger.info(f"Data for user {user_id} has been deleted.")
    except Exception as e:
        logger.error(f"Error deleting data for user {user_id}: {e}")
        raise

async def get_channels():
    """
    Retrieves all unique channels from the database.
    """
    global pool
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT DISTINCT channel_id FROM user_channels")
        return [row['channel_id'] for row in rows]
    except Exception as e:
        logger.error(f"Error retrieving all channels: {e}")
        raise
