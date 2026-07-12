import sqlite3
from werkzeug.security import generate_password_hash

username = input("Masukkan username admin: ")
password = input("Masukkan password admin: ")

conn = sqlite3.connect('perpustakaan.db')
conn.execute(
    'INSERT INTO admin (username, password_hash) VALUES (?, ?)',
    (username, generate_password_hash(password))
)
conn.commit()
conn.close()
print(f"Admin '{username}' berhasil dibuat.")