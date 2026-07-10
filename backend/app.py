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

# GET koleksi
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

# GET semua anggota
@app.route('/api/anggota', methods=['GET'])
def get_anggota():
    conn = get_db_connection()
    anggota = conn.execute('SELECT * FROM anggota').fetchall()
    conn.close()
    return jsonify([dict(row) for row in anggota])

# POST tambah anggota baru
@app.route('/api/anggota', methods=['POST'])
def tambah_anggota():
    data = request.get_json()
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO anggota (nomor_anggota, nama, jenis_kelamin, no_kontak, asal, keterangan)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        data['nomor_anggota'], data['nama'], data.get('jenis_kelamin'),
        data.get('no_kontak'), data.get('asal'), data.get('keterangan')
    ))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Anggota berhasil ditambahkan'}), 201

# PUT update anggota
@app.route('/api/anggota/<int:id>', methods=['PUT'])
def update_anggota(id):
    data = request.get_json()
    conn = get_db_connection()
    conn.execute('''
        UPDATE anggota SET nama=?, jenis_kelamin=?, no_kontak=?, asal=?, keterangan=?
        WHERE id=?
    ''', (
        data.get('nama'), data.get('jenis_kelamin'), data.get('no_kontak'),
        data.get('asal'), data.get('keterangan'), id
    ))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Anggota berhasil diupdate'})

# DELETE anggota
@app.route('/api/anggota/<int:id>', methods=['DELETE'])
def hapus_anggota(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM anggota WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Anggota berhasil dihapus'})

from datetime import date, timedelta

# GET semua sirkulasi (riwayat pinjam-kembali)
@app.route('/api/sirkulasi', methods=['GET'])
def get_sirkulasi():
    conn = get_db_connection()
    sirkulasi = conn.execute('''
        SELECT sirkulasi.*, koleksi.judul, anggota.nama
        FROM sirkulasi
        JOIN koleksi ON sirkulasi.koleksi_id = koleksi.id
        JOIN anggota ON sirkulasi.anggota_id = anggota.id
    ''').fetchall()
    conn.close()
    return jsonify([dict(row) for row in sirkulasi])

# POST pinjam buku
@app.route('/api/sirkulasi/pinjam', methods=['POST'])
def pinjam_buku():
    data = request.get_json()
    koleksi_id = data['koleksi_id']
    anggota_id = data['anggota_id']

    conn = get_db_connection()

    # Cek stok tersedia
    buku = conn.execute('SELECT eksemplar_tersedia FROM koleksi WHERE id=?', (koleksi_id,)).fetchone()
    if buku is None:
        conn.close()
        return jsonify({'error': 'Buku tidak ditemukan'}), 404
    if buku['eksemplar_tersedia'] <= 0:
        conn.close()
        return jsonify({'error': 'Buku sedang tidak tersedia'}), 400

    # Ambil durasi pinjam default dari pengaturan
    durasi = conn.execute("SELECT value FROM pengaturan WHERE key='durasi_pinjam_default'").fetchone()
    durasi_hari = int(durasi['value']) if durasi else 7
    jatuh_tempo = date.today() + timedelta(days=durasi_hari)

    # Insert record sirkulasi
    conn.execute('''
        INSERT INTO sirkulasi (koleksi_id, anggota_id, tanggal_jatuh_tempo, status)
        VALUES (?, ?, ?, 'dipinjam')
    ''', (koleksi_id, anggota_id, jatuh_tempo.isoformat()))

    # Kurangi stok tersedia
    conn.execute('UPDATE koleksi SET eksemplar_tersedia = eksemplar_tersedia - 1 WHERE id=?', (koleksi_id,))

    conn.commit()
    conn.close()
    return jsonify({'message': 'Buku berhasil dipinjam', 'tanggal_jatuh_tempo': jatuh_tempo.isoformat()}), 201

# PUT kembalikan buku
@app.route('/api/sirkulasi/<int:id>/kembali', methods=['PUT'])
def kembalikan_buku(id):
    conn = get_db_connection()

    record = conn.execute('SELECT koleksi_id, status FROM sirkulasi WHERE id=?', (id,)).fetchone()
    if record is None:
        conn.close()
        return jsonify({'error': 'Data peminjaman tidak ditemukan'}), 404
    if record['status'] == 'dikembalikan':
        conn.close()
        return jsonify({'error': 'Buku ini sudah dikembalikan sebelumnya'}), 400

    # Update status sirkulasi
    conn.execute('''
        UPDATE sirkulasi SET tanggal_kembali=?, status='dikembalikan' WHERE id=?
    ''', (date.today().isoformat(), id))

    # Tambah lagi stok tersedia
    conn.execute('UPDATE koleksi SET eksemplar_tersedia = eksemplar_tersedia + 1 WHERE id=?', (record['koleksi_id'],))

    conn.commit()
    conn.close()
    return jsonify({'message': 'Buku berhasil dikembalikan'})

if __name__ == '__main__':
    app.run(debug=True)