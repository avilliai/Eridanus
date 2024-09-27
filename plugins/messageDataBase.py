
import sqlite3
from datetime import datetime


conn = sqlite3.connect('data/user_text_database.db')
cursor = conn.cursor()


cursor.execute('''
CREATE TABLE IF NOT EXISTS user_texts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    date TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)
''')

# 定义一个函数用于添加文本
def add_text_TextDataBase(user_id, text):
    date_added = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 当前时间
    try:
        cursor.execute('''
        INSERT INTO user_texts (user_id, text, date) 
        VALUES (?, ?, ?)''', (user_id, text, date_added))
        conn.commit()
        print(f"成功添加文本: {text}，用户 ID: {user_id}")
    except sqlite3.Error as e:
        print(f"添加文本失败: {e}")
def user_exists_TextDataBase(user_id):
    cursor.execute('SELECT * FROM user_texts WHERE user_id = ?', (user_id,))
    return cursor.fetchone() is not None
