import sqlite3
from datetime import datetime

with sqlite3.connect('data/user_database.db') as conn:
    cursor = conn.cursor()

# 创建用户表
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    nickname TEXT NOT NULL,
    sex TEXT,
    sign_in_days INTEGER DEFAULT 0,
    added_date TEXT NOT NULL,
    city TEXT NOT NULL,
    operate_level TEXT NOT NULL,
    last_sign_in TEXT NOT NULL
)
''')

# 修改 add_user 函数，确保提供所有字段
def add_user(user_id, nickname, sex, city, operate_level=0):
    added_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    last_sign_in=added_date
    cursor.execute('''
    INSERT INTO users (user_id, nickname, sex, added_date, city, operate_level,last_sign_in) 
    VALUES (?, ?, ?, ?, ?, ?,?)''', (user_id, nickname, sex, added_date, city, operate_level,last_sign_in))
    conn.commit()

def user_exists(user_id):
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    return cursor.fetchone() is not None

def get_user_info(user_id):
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    return cursor.fetchone()

def update_last_sign_in(user_id):
    last_sign_in_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
    UPDATE users
    SET last_sign_in = ?, sign_in_days = sign_in_days + 1
    WHERE user_id = ?
    ''', (last_sign_in_date, user_id))
    conn.commit()

#cursor.execute('SELECT * FROM users')
#print(cursor.fetchall())

#conn.close()