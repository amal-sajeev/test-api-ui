import sqlite3
from hashlib import sha256

def create_database():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_user(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    password_hash = sha256(password.encode()).hexdigest()
    try:
        c.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))
        conn.commit()
    except sqlite3.IntegrityError:
        print("Username already exists!")
    conn.close()

if __name__ == '__main__':
    create_database()
    # Add a test user
    add_user('testuser', 'password123')