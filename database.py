import sqlite3
import logging

logger = logging.getLogger(__name__)
DB_FILE = "bot_database.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_channels (
            user_id INTEGER,
            channel TEXT
        )
    """)
    conn.commit()
    conn.close()
    logger.info("Таблица user_channels проверена или создана.")

def add_channel(user_id, channel):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT channel FROM user_channels WHERE user_id = ? AND channel = ?", (user_id, channel))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO user_channels (user_id, channel) VALUES (?, ?)", (user_id, channel))
            conn.commit()
            logger.info(f"Канал {channel} добавлен для пользователя {user_id}.")
            return True
        else:
            logger.warning(f"Канал {channel} уже существует для пользователя {user_id}.")
            return False
    finally:
        conn.close()

def get_user_channels(user_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT channel FROM user_channels WHERE user_id = ?", (user_id,))
        channels = [row[0] for row in cursor.fetchall()]
        logger.info(f"Получен список каналов для пользователя {user_id}: {channels}")
        return channels
    finally:
        conn.close()

def delete_user_data(user_id):
    """
    Удаляет все данные пользователя из базы данных.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM user_channels WHERE user_id = ?", (user_id,))
        conn.commit()
        logger.info(f"Данные пользователя {user_id} удалены.")
    finally:
        conn.close()
