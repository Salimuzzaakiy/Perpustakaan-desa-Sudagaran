from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)
DB_NAME = 'perpustakaan.db'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return 'Perpustakaan Digital Sudagaran'

# GET semua koleksi
@app.route('/api/koleksi', methods=['GET'])
def get_koleksi():
    conn = get_db_connection()
    koleksi = conn.execute('SELECT * FROM koleksi').fetchall()
    conn.close()
    return jsonify([dict(row) for row in koleksi])

# POST tambah koleksi baru
@app.route('/api/koleksi', methods=['POST'])
def tambah_koleksi():
    data = request.get_json()
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO koleksi (nomor_inventaris, judul, pengarang, penerbit, tahun_terbit, jumlah_eksemplar, eksemplar_tersedia, subjek, sumber, jenjang)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['nomor_inventaris'], data['judul'], data.get('pengarang'), data.get('penerbit'),
        data.get('tahun_terbit'), data.get('jumlah_eksemplar', 1), data.get('jumlah_eksemplar', 1),
        data.get('subjek'), data.get('sumber'), data.get('jenjang')
    ))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Koleksi berhasil ditambahkan'}), 201

# PUT update koleksi berdasarkan ID
@app.route('/api/koleksi/<int:id>', methods=['PUT'])
def update_koleksi(id):
    data = request.get_json()
    conn = get_db_connection()
    conn.execute('''
        UPDATE koleksi SET judul=?, pengarang=?, penerbit=?, tahun_terbit=?, subjek=?, jenjang=?
        WHERE id=?
    ''', (
        data.get('judul'), data.get('pengarang'), data.get('penerbit'),
        data.get('tahun_terbit'), data.get('subjek'), data.get('jenjang'), id
    ))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Koleksi berhasil diupdate'})

# DELETE koleksi berdasarkan ID
@app.route('/api/koleksi/<int:id>', methods=['DELETE'])
def hapus_koleksi(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM koleksi WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Koleksi berhasil dihapus'})

if __name__ == '__main__':
    app.run(debug=True)