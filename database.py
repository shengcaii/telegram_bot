import sqlite3

def init_db():
    conn = sqlite3.connect('team.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_member(name, role):
    conn = sqlite3.connect('team.db')
    c = conn.cursor()
    c.execute('INSERT INTO members (name, role) VALUES (?, ?)', (name, role))
    conn.commit()
    conn.close()

def get_members():
    conn = sqlite3.connect('team.db')
    c = conn.cursor()
    c.execute('SELECT name, role FROM members')
    members = c.fetchall()
    conn.close()
    return members