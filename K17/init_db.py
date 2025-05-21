import sqlite3

def init_db():
    conn = sqlite3.connect('vulnerable.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
        )
    ''')
    
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', 'supersecret'))
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('user', 'qwerty'))
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin1', 'secret'))
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin2', 'password_secret'))
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()