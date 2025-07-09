import sqlite3

DB_NAME = "users.db"
PROTOCOLS = ["vless", "vmess", "trojan", "shadowsocks", "hysteria", "tuic"]

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Создаём таблицу только с user_id
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY
        )
    ''')
    # Добавляем недостающие столбцы
    for proto in PROTOCOLS:
        col = f"received_{proto}"
        try:
            c.execute(f"ALTER TABLE users ADD COLUMN {col} INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass  # уже есть
    conn.commit()
    conn.close()

def add_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

def has_received_test(user_id, proto):
    field = f"received_{proto}"
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(f"SELECT {field} FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return bool(row and row[0] == 1)

def mark_test_given(user_id, proto):
    field = f"received_{proto}"
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(f"UPDATE users SET {field} = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
