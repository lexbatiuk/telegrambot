import sqlite3

DB_FILE = "bot.db"

def init_db():
    """Инициализация базы данных."""
    conn = sqlite3.connect(DB_FILE)
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

def add_channel(user_id: int, channel: str) -> bool:
    """Добавляет канал для пользователя. Возвращает True, если добавление успешно."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO user_channels (user_id, channel) VALUES (?, ?)", (user_id, channel))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user_channels(user_id: int) -> list[str]:
    """Возвращает список каналов пользователя."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT channel FROM user_channels WHERE user_id
