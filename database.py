import sqlite3

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_channels (
            user_id INTEGER,
            channel TEXT
        )
    """)
    conn.commit()
    conn.close()

# Добавление канала для пользователя
def add_channel(user_id, channel):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT channel FROM user_channels WHERE user_id = ? AND channel = ?", (user_id, channel))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO user_channels (user_id, channel) VALUES (?, ?)", (user_id, channel))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

# Получение списка каналов пользователя
def get_user_channels(user_id):
    conn = sqlite3.connect("bot_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT channel FROM user_channels WHERE user_id = ?", (user_id,))
    channels = [row[0] for row in cursor.fetchall()]
    conn.close()
    return channels

# Инициализация базы данных при запуске
init_db()
