import asyncpg
import os

# Database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

async def init_db():
    """
    Initializes the database and creates necessary tables.
    """
    create_table_query = """
    CREATE TABLE IF NOT EXISTS user_channels (
        user_id BIGINT NOT NULL,
        channel_id TEXT NOT NULL,
        PRIMARY KEY (user_id, channel_id)
    );
    """
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute(create_table_query)
    await conn.close()

async def add_channel(user_id: int, channel_id: str):
    """
    Adds a new channel for a user.
    """
    insert_query = """
    INSERT INTO user_channels (user_id, channel_id)
    VALUES ($1, $2)
    ON CONFLICT (user_id, channel_id) DO NOTHING;
    """
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute(insert_query, user_id, channel_id)
    await conn.close()

async def get_user_channels(user_id: int):
    """
    Retrieves a list of channels for a user.
    """
    select_query = "SELECT channel_id FROM user_channels WHERE user_id = $1;"
    conn = await asyncpg.connect(DATABASE_URL)
    rows = await conn.fetch(select_query, user_id)
    await conn.close()
    return [row['channel_id'] for row in rows]
