import asyncpg

DB_DSN = os.getenv("DATABASE_URL")

async def init_db():
    conn = await asyncpg.connect(DB_DSN)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS user_channels (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            channel_name TEXT NOT NULL
        )
    """)
    await conn.close()

async def add_channel(user_id: int, channel_name: str):
    conn = await asyncpg.connect(DB_DSN)
    await conn.execute("""
        INSERT INTO user_channels (user_id, channel_name) VALUES ($1, $2)
    """, user_id, channel_name)
    await conn.close()

async def get_user_channels(user_id: int):
    conn = await asyncpg.connect(DB_DSN)
    rows = await conn.fetch("""
        SELECT channel_name FROM user_channels WHERE user_id = $1
    """, user_id)
    await conn.close()
    return [row['channel_name'] for row in rows]
