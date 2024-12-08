import sqlite3

def init_db():
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_channels (
            user_id INTEGER,
            channel TEXT,
            UNIQUE(user_id, channel)
        )
    """)
    conn.commit()
    conn.close()

def add_user_channel(user_id, channel):
    try:
        conn = sqlite3.connect("bot.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO user_channels (user_id, channel) VALUES (?, ?)", (user_id, channel))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user_channels(user_id):
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT channel FROM user_channels WHERE user_id = ?", (user_id,))
    channels = [row[0] for row in cursor.fetchall()]
    conn.close()
    return channels
