import asyncpg
import os

DATABASE_URL = os.getenv("DATABASE_URL")


async def init_db():
    """
    Initializes the database and creates required tables if they do not exist.
    """
    create_table_query = """
    CREATE TABLE IF NOT EXISTS user_channels (
        user_id BIGINT NOT NULL,
        channel_id TEXT NOT NULL,
        PRIMARY KEY (user_id, channel_id)
    );
    """
    async with asyncpg.create_pool(DATABASE_URL) as pool:
        async with pool.acquire() as connection:
            await connection.execute(create_table_query)


async def add_channel(user_id: int, channel_id: str):
    """
    Adds a channel to the database for a specific user.
    """
    query = """
    INSERT INTO user_channels (user_id, channel_id)
    VALUES ($1, $2)
    ON CONFLICT (user_id, channel_id) DO NOTHING;
    """
    async with asyncpg.create_pool(DATABASE_URL) as pool:
        async with pool.acquire() as connection:
            await connection.execute(query, user_id, channel_id)


async def get_user_channels(user_id: int):
    """
    Retrieves the list of channels for a specific user.
    """
    query = "SELECT channel_id FROM user_channels WHERE user_id = $1;"
    async with asyncpg.create_pool(DATABASE_URL) as pool:
        async with pool.acquire() as connection:
            return await connection.fetch(query, user_id)
