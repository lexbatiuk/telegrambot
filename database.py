import asyncpg
import os
import logging

logger = logging.getLogger(__name__)

async def init_db():
    """
    Initialize the PostgreSQL database and create tables if they don't exist.
    """
    conn = await asyncpg.connect(
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
        database=os.getenv("PGDATABASE"),
        host=os.getenv("PGHOST"),
        port=os.getenv("PGPORT"),
    )
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS user_channels (
            user_id BIGINT PRIMARY KEY,
            channels TEXT[]
        )
    ''')
    await conn.close()
    logger.info("Database initialized.")

async def add_channel(user_id, channel):
    """
    Add a channel to the user's list of channels.
    """
    conn = await asyncpg.connect(
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
        database=os.getenv("PGDATABASE"),
        host=os.getenv("PGHOST"),
        port=os.getenv("PGPORT"),
    )
    await conn.execute('''
        INSERT INTO user_channels (user_id, channels)
        VALUES ($1, ARRAY[$2])
        ON CONFLICT (user_id) DO UPDATE
        SET channels = array_append(user_channels.channels, $2)
    ''', user_id, channel)
    await conn.close()

async def get_channels(user_id):
    """
    Get the list of channels for a user.
    """
    conn = await asyncpg.connect(
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
        database=os.getenv("PGDATABASE"),
        host=os.getenv("PGHOST"),
        port=os.getenv("PGPORT"),
    )
    result = await conn.fetchval('''
        SELECT channels FROM user_channels WHERE user_id = $1
    ''', user_id)
    await conn.close()
    return result or []

async def delete_user_data(user_id):
    """
    Delete all data for a user.
    """
    conn = await asyncpg.connect(
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
        database=os.getenv("PGDATABASE"),
        host=os.getenv("PGHOST"),
        port=os.getenv("PGPORT"),
    )
    await conn.execute('''
        DELETE FROM user_channels WHERE user_id = $1
    ''', user_id)
    await conn.close()
