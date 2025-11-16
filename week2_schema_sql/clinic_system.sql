CREATE DATABASE IF NOT EXISTS clinic_appointment_db;
USE clinic_appointment_db;

DROP TABLE IF EXISTS Rekam_medis;
DROP TABLE IF EXISTS Appointment;
DROP TABLE IF EXISTS Dijadwalkan;
DROP TABLE IF EXISTS Pasien_telepon;
DROP TABLE IF EXISTS Dokter_telepon;
DROP TABLE IF EXISTS Resepsionis_telepon;
DROP TABLE IF EXISTS Jadwal_dokter;
DROP TABLE IF EXISTS Dokter;
DROP TABLE IF EXISTS Resepsionis;
DROP TABLE IF EXISTS Pasien;

CREATE TABLE Pasien
(
  pasien_id INT NOT NULL,
  nama_depan VARCHAR(50) NOT NULL,
  nama_belakang VARCHAR(50) NOT NULL,
  email VARCHAR(100) NOT NULL,
  gender ENUM('Laki-laki', 'Perempuan') NOT NULL,
  tanggal_daftar DATE NOT NULL,
  tanggal_lahir DATE NOT NULL,
  password VARCHAR(50) NOT NULL,
  Kota VARCHAR(50) NOT NULL,
  Jalan VARCHAR(255) NOT NULL,
  PRIMARY KEY (pasien_id)
);

CREATE TABLE Dokter
(
  dokter_id INT NOT NULL,
  nama_depan VARCHAR(50) NOT NULL,
  nama_belakang VARCHAR(50) NOT NULL,
  tanggal_masuk DATE NOT NULL,
  status ENUM('Aktif', 'Nonaktif') NOT NULL,
  PRIMARY KEY (dokter_id)
);

CREATE TABLE Resepsionis
(
  resepsionis_id INT NOT NULL,
  nama_depan VARCHAR(50) NOT NULL,
  nama_belakang VARCHAR(50) NOT NULL,
  tanggal_masuk DATE NOT NULL,
  status ENUM('Aktif', 'Nonaktif') NOT NULL,
  PRIMARY KEY (resepsionis_id)
);

CREATE TABLE Jadwal_dokter
(
  jadwal_id INT NOT NULL,
  hari ENUM('Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu') NOT NULL,
  jam_mulai TIME NOT NULL,
  jam_selesai TIME NOT NULL,
  PRIMARY KEY (jadwal_id)
);

CREATE TABLE Dijadwalkan
(
  dokter_id INT NOT NULL,
  jadwal_id INT NOT NULL,
  PRIMARY KEY (dokter_id, jadwal_id),
  FOREIGN KEY (dokter_id) REFERENCES Dokter(dokter_id),
  FOREIGN KEY (jadwal_id) REFERENCES Jadwal_dokter(jadwal_id)
);

CREATE TABLE Pasien_telepon
(
  telepon VARCHAR(50) NOT NULL,
  pasien_id INT NOT NULL,
  PRIMARY KEY (telepon, pasien_id),
  FOREIGN KEY (pasien_id) REFERENCES Pasien(pasien_id)
);

CREATE TABLE Dokter_telepon
(
  telepon VARCHAR(50) NOT NULL,
  dokter_id INT NOT NULL,
  PRIMARY KEY (telepon, dokter_id),
  FOREIGN KEY (dokter_id) REFERENCES Dokter(dokter_id)
);

CREATE TABLE Resepsionis_telepon
(
  telepon VARCHAR(50) NOT NULL,
  resepsionis_id INT NOT NULL,
  PRIMARY KEY (telepon, resepsionis_id),
  FOREIGN KEY (resepsionis_id) REFERENCES Resepsionis(resepsionis_id)
);

CREATE TABLE Appointment
(
  appointment_id INT NOT NULL,
  tanggal DATE NOT NULL,
  waktu CHAR(13) NOT NULL,
  status ENUM('Selesai', 'Dijadwalkan', 'Dibatalkan') NOT NULL,
  pasien_id INT NOT NULL,
  dokter_id INT NOT NULL,
  resepsionis_id INT,
  jadwal_id INT NOT NULL,
  PRIMARY KEY (appointment_id),
  FOREIGN KEY (pasien_id) REFERENCES Pasien(pasien_id),
  FOREIGN KEY (dokter_id) REFERENCES Dokter(dokter_id),
  FOREIGN KEY (resepsionis_id) REFERENCES Resepsionis(resepsionis_id),
  FOREIGN KEY (jadwal_id) REFERENCES Jadwal_dokter(jadwal_id)
);

CREATE TABLE Rekam_medis
(
  diagnosis VARCHAR(100) NOT NULL,
  description TEXT NOT NULL,
  appointment_id INT NOT NULL,
  PRIMARY KEY (diagnosis, appointment_id),
  FOREIGN KEY (appointment_id) REFERENCES Appointment(appointment_id)
);
