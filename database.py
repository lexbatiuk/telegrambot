import asyncpg
import os

async def add_channel(user_id, channel_name):
    """
    Adds a channel to the database for a specific user.
    """
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"))
    try:
        await conn.execute(
            "INSERT INTO user_channels (user_id, channel_name) VALUES ($1, $2)",
            user_id, channel_name
        )
    finally:
        await conn.close()

async def get_user_channels(user_id):
    """
    Retrieves all channels for a specific user.
    """
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"))
    try:
        rows = await conn.fetch(
            "SELECT channel_name FROM user_channels WHERE user_id = $1", user_id
        )
        return [row["channel_name"] for row in rows]
    finally:
        await conn.close()

async def delete_user_data(user_id):
    """
    Deletes all data associated with a specific user.
    """
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"))
    try:
        await conn.execute("DELETE FROM user_channels WHERE user_id = $1", user_id)
    finally:
        await conn.close()

async def get_channels():
    """
    Retrieves all channels from the database.
    """
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"))
    try:
        rows = await conn.fetch("SELECT * FROM user_channels")
        return rows
    finally:
        await conn.close()
