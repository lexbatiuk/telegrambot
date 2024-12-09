import asyncpg
import logging
from config import Config

logger = logging.getLogger(__name__)

# Создание пула соединений с базой данных
pool = None

async def init_db():
    """Инициализация пула соединений и создание таблиц."""
    global pool
    pool = await asyncpg.create_pool(dsn=Config.DATABASE_URL)
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS user_channels (
                user_id BIGINT NOT NULL,
                channel_id BIGINT NOT NULL,
                UNIQUE(user_id, channel_id)
            );
            CREATE TABLE IF NOT EXISTS temp_data (
                user_id BIGINT PRIMARY KEY,
                temp_code TEXT
            );
        """)
    logger.info("Database initialized successfully.")

async def add_channel(user_id: int, channel_id: int):
    """Добавление канала в базу данных."""
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO user_channels (user_id, channel_id)
            VALUES ($1, $2)
            ON CONFLICT DO NOTHING;
        """, user_id, channel_id)

async def get_user_channels(user_id: int):
    """Получение списка каналов пользователя."""
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT channel_id FROM user_channels WHERE user_id = $1;
        """, user_id)
        return [row["channel_id"] for row in rows]

async def save_temp_code(user_id: int, code: str):
    """Сохранение временного кода в базу данных."""
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO temp_data (user_id, temp_code)
            VALUES ($1, $2)
            ON CONFLICT (user_id) DO UPDATE SET temp_code = $2;
        """, user_id, code)

async def get_temp_code(user_id: int):
    """Получение временного кода из базы данных."""
    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            SELECT temp_code FROM temp_data WHERE user_id = $1;
        """, user_id)
        return row["temp_code"] if row else None
