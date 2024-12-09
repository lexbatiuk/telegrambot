import asyncpg
import os
import logging

DATABASE_URL = os.getenv("DATABASE_URL")

async def init_db():
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("""
    CREATE TABLE IF NOT EXISTS user_channels (
        user_id BIGINT PRIMARY KEY,
        channels TEXT[]
    )
    """)
    await conn.close()

async def add_channel(user_id, channel):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("""
    INSERT INTO user_channels (user_id, channels)
    VALUES ($1, $2)
    ON CONFLICT (user_id)
    DO UPDATE SET channels = array_append(user_channels.channels, $2)
    """, user_id, channel)
    await conn.close()

async def get_user_channels(user_id):
    conn = await asyncpg.connect(DATABASE_URL)
    channels = await conn.fetchval("""
    SELECT channels FROM user_channels WHERE user_id = $1
    """, user_id)
    await conn.close()
    return channels or []
