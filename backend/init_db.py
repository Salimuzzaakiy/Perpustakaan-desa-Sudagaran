import sqlite3

def init_database():
    conn = sqlite3.connect('perpustakaan.db')
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print("Database berhasil dibuat: perpustakaan.db")

if __name__ == '__main__':
    init_database()