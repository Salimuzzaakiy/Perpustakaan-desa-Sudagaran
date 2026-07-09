CREATE TABLE IF NOT EXISTS koleksi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nomor_inventaris TEXT UNIQUE NOT NULL,
    nomor_panggil TEXT,
    judul TEXT NOT NULL,
    pengarang TEXT,
    penerbit TEXT,
    tahun_terbit INTEGER,
    jumlah_eksemplar INTEGER DEFAULT 1,
    eksemplar_tersedia INTEGER DEFAULT 1,
    subjek TEXT,
    sumber TEXT,
    jenjang TEXT,
    status TEXT DEFAULT 'tersedia',
    tanggal_masuk DATE DEFAULT CURRENT_DATE,
    file_digital TEXT
);

CREATE TABLE IF NOT EXISTS anggota (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nomor_anggota TEXT UNIQUE NOT NULL,
    nama TEXT NOT NULL,
    jenis_kelamin TEXT,
    no_kontak TEXT,
    asal TEXT,
    tanggal_bergabung DATE DEFAULT CURRENT_DATE,
    keterangan TEXT
);

CREATE TABLE IF NOT EXISTS sirkulasi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    koleksi_id INTEGER NOT NULL,
    anggota_id INTEGER NOT NULL,
    tanggal_pinjam DATE DEFAULT CURRENT_DATE,
    tanggal_jatuh_tempo DATE,
    tanggal_kembali DATE,
    status TEXT DEFAULT 'dipinjam',
    FOREIGN KEY (koleksi_id) REFERENCES koleksi(id),
    FOREIGN KEY (anggota_id) REFERENCES anggota(id)
);

CREATE TABLE IF NOT EXISTS kunjungan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    anggota_id INTEGER,
    nama_pengunjung TEXT,
    tanggal_kunjungan DATE DEFAULT CURRENT_DATE,
    keperluan TEXT,
    FOREIGN KEY (anggota_id) REFERENCES anggota(id)
);

CREATE TABLE IF NOT EXISTS pengaturan (
    key TEXT PRIMARY KEY,
    value TEXT
);

INSERT OR IGNORE INTO pengaturan (key, value) VALUES ('durasi_pinjam_default', '7');
INSERT OR IGNORE INTO pengaturan (key, value) VALUES ('maks_buku_per_orang', '3');