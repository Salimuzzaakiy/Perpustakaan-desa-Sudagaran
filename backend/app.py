from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import sqlite3
from datetime import date, timedelta
from werkzeug.security import check_password_hash
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)
DB_NAME = 'perpustakaan.db'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Endpoint untuk mengunggah file
@app.route('/api/koleksi/<int:id>/upload', methods=['POST'])
def upload_soft_file(id):
    if 'file' not in request.files:
        return jsonify({'error': 'Tidak ada file yang dikirim'}), 400

    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'File harus berformat PDF'}), 400

    filename = secure_filename(f"koleksi_{id}_{file.filename}")
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    conn = get_db_connection()
    conn.execute('UPDATE koleksi SET file_digital=? WHERE id=?', (filepath, id))
    conn.commit()
    conn.close()

    return jsonify({'message': 'File berhasil diunggah', 'path': filepath})

#Endpoint cek file
@app.route('/api/koleksi/<int:id>/file', methods=['GET'])
def lihat_info_buku(id):
    conn = get_db_connection()
    buku = conn.execute('SELECT file_digital FROM koleksi WHERE id=?', (id,)).fetchone()
    conn.close()
    if buku is None or not buku['file_digital']:
        return jsonify({'error': 'Info buku belum tersedia'}), 404
    return send_file(buku['file_digital'])

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return 'Perpustakaan Digital Sudagaran'

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    admin = conn.execute('SELECT * FROM admin WHERE username=?', (username,)).fetchone()
    conn.close()

    if admin is None or not check_password_hash(admin['password_hash'], password):
        return jsonify({'error': 'Username atau password salah'}), 401

    return jsonify({'message': 'Login berhasil', 'username': admin['username']})
def generate_nomor_panggil(nomor_klasifikasi, pengarang, judul):
    tiga_huruf = pengarang[:3].upper() if pengarang else 'XXX'
    huruf_judul = judul[0].lower() if judul else 'x'
    return f"{nomor_klasifikasi} {tiga_huruf} {huruf_judul}"

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
    nomor_panggil = generate_nomor_panggil(
        data.get('nomor_klasifikasi', ''), data.get('pengarang', ''), data['judul']
    )
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO koleksi (nomor_inventaris, nomor_panggil, judul, pengarang, penerbit, tahun_terbit, jumlah_eksemplar, eksemplar_tersedia, subjek, sumber, jenjang)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['nomor_inventaris'], nomor_panggil, data['judul'], data.get('pengarang'), data.get('penerbit'),
        data.get('tahun_terbit'), data.get('jumlah_eksemplar', 1), data.get('jumlah_eksemplar', 1),
        data.get('subjek'), data.get('sumber'), data.get('jenjang')
    ))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Koleksi berhasil ditambahkan', 'nomor_panggil': nomor_panggil}), 201

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

# GET semua riwayat pinjam-kembali
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
    
    # Cek jumlah buku yang sedang dipinjam anggota ini
    maks = conn.execute("SELECT value FROM pengaturan WHERE key='maks_buku_per_orang'").fetchone()
    batas_maks = int(maks['value']) if maks else 3
    jumlah_dipinjam = conn.execute(
        "SELECT COUNT(*) as jumlah FROM sirkulasi WHERE anggota_id=? AND status='dipinjam'",
        (anggota_id,)
    ).fetchone()['jumlah']
    if jumlah_dipinjam >= batas_maks:
        conn.close()
        return jsonify({'error': f'Anggota ini sudah mencapai batas maksimal {batas_maks} buku dipinjam'}), 400

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

# GET semua riwayat kunjungan
@app.route('/api/kunjungan', methods=['GET'])
def get_kunjungan():
    conn = get_db_connection()
    kunjungan = conn.execute('''
        SELECT kunjungan.*, anggota.nama AS nama_anggota
        FROM kunjungan
        LEFT JOIN anggota ON kunjungan.anggota_id = anggota.id
    ''').fetchall()
    conn.close()
    return jsonify([dict(row) for row in kunjungan])

# POST catat kunjungan baru
@app.route('/api/kunjungan', methods=['POST'])
def catat_kunjungan():
    data = request.get_json()
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO kunjungan (anggota_id, nama_pengunjung, keperluan)
        VALUES (?, ?, ?)
    ''', (
        data.get('anggota_id'),  # boleh NULL jika bukan anggota
        data.get('nama_pengunjung'),  # diisi jika bukan anggota terdaftar
        data.get('keperluan')
    ))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Kunjungan berhasil dicatat'}), 201

# GET semua pengaturan
@app.route('/api/pengaturan', methods=['GET'])
def get_pengaturan():
    conn = get_db_connection()
    pengaturan = conn.execute('SELECT * FROM pengaturan').fetchall()
    conn.close()
    return jsonify({row['key']: row['value'] for row in pengaturan})

# PUT update satu pengaturan
@app.route('/api/pengaturan/<key>', methods=['PUT'])
def update_pengaturan(key):
    data = request.get_json()
    conn = get_db_connection()
    conn.execute('UPDATE pengaturan SET value=? WHERE key=?', (data['value'], key))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Pengaturan berhasil diperbarui'})

if __name__ == '__main__':
    app.run(debug=True)