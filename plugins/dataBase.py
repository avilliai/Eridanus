import sqlite3
from datetime import datetime

conn = sqlite3.connect('data/user_database.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    nickname TEXT NOT NULL,
    sex TEXT,
    sign_in_days INTEGER DEFAULT 0,
    added_date TEXT NOT NULL,
    city TEXT NOT NULL
)
''')

def add_user(user_id, nickname, sex,city):
    added_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
    INSERT INTO users (user_id, nickname, sex, added_date,city) 
    VALUES (?, ?, ?, ?)''', (user_id, nickname, sex, added_date,city))
    conn.commit()
def user_exists(user_id):
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    return cursor.fetchone() is not None


#cursor.execute('SELECT * FROM users')
#print(cursor.fetchall())

#conn.close()