-- ========================================
-- CLINIC APPOINTMENT SYSTEM - DATABASE SETUP
-- ========================================
-- Jalankan file ini di phpMyAdmin atau MySQL command line
-- untuk membuat database dan semua tabel yang diperlukan

-- 1. CREATE DATABASE
CREATE DATABASE IF NOT EXISTS DBProject;
USE DBProject;

-- 2. CREATE TABLES

CREATE TABLE IF NOT EXISTS Pasien
(
  pasien_id INT NOT NULL AUTO_INCREMENT,
  nama_depan VARCHAR(50),
  nama_belakang VARCHAR(50),
  email VARCHAR(100) NOT NULL UNIQUE,
  gender VARCHAR(10),
  tanggal_daftar DATE,
  tanggal_lahir DATE,
  password VARCHAR(255) NOT NULL,
  Kota VARCHAR(50),
  Jalan VARCHAR(255),
  PRIMARY KEY (pasien_id)
);

CREATE TABLE IF NOT EXISTS Dokter
(
  dokter_id INT NOT NULL AUTO_INCREMENT,
  nama_depan VARCHAR(50) NOT NULL,
  nama_belakang VARCHAR(50) NOT NULL,
  tanggal_masuk DATE NOT NULL,
  status VARCHAR(20) NOT NULL,
  PRIMARY KEY (dokter_id)
);

CREATE TABLE IF NOT EXISTS Resepsionis
(
  resepsionis_id INT NOT NULL AUTO_INCREMENT,
  nama_depan VARCHAR(50) NOT NULL,
  nama_belakang VARCHAR(50) NOT NULL,
  tanggal_masuk DATE NOT NULL,
  status VARCHAR(20) NOT NULL,
  PRIMARY KEY (resepsionis_id)
);

CREATE TABLE IF NOT EXISTS Jadwal_dokter
(
  jadwal_id INT NOT NULL AUTO_INCREMENT,
  hari VARCHAR(10) NOT NULL,
  jam_mulai CHAR(5) NOT NULL,
  jam_selesai CHAR(5) NOT NULL,
  PRIMARY KEY (jadwal_id)
);

CREATE TABLE IF NOT EXISTS Dijadwalkan
(
  dokter_id INT NOT NULL,
  jadwal_id INT NOT NULL,
  PRIMARY KEY (dokter_id, jadwal_id),
  FOREIGN KEY (dokter_id) REFERENCES Dokter(dokter_id) ON DELETE CASCADE,
  FOREIGN KEY (jadwal_id) REFERENCES Jadwal_dokter(jadwal_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Pasien_telepon
(
  telepon VARCHAR(50),
  pasien_id INT NOT NULL,
  PRIMARY KEY (telepon, pasien_id),
  FOREIGN KEY (pasien_id) REFERENCES Pasien(pasien_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Dokter_telepon
(
  telepon VARCHAR(50) NOT NULL,
  dokter_id INT NOT NULL,
  PRIMARY KEY (telepon, dokter_id),
  FOREIGN KEY (dokter_id) REFERENCES Dokter(dokter_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Resepsionis_telepon
(
  telepon VARCHAR(50) NOT NULL,
  resepsionis_id INT NOT NULL,
  PRIMARY KEY (telepon, resepsionis_id),
  FOREIGN KEY (resepsionis_id) REFERENCES Resepsionis(resepsionis_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Appointment
(
  appointment_id INT NOT NULL AUTO_INCREMENT,
  tanggal DATE NOT NULL,
  waktu CHAR(13) NOT NULL,
  status VARCHAR(20) NOT NULL,
  pasien_id INT NOT NULL,
  dokter_id INT NOT NULL,
  resepsionis_id INT,
  jadwal_id INT NOT NULL,
  PRIMARY KEY (appointment_id),
  FOREIGN KEY (pasien_id) REFERENCES Pasien(pasien_id) ON DELETE CASCADE,
  FOREIGN KEY (dokter_id) REFERENCES Dokter(dokter_id) ON DELETE CASCADE,
  FOREIGN KEY (resepsionis_id) REFERENCES Resepsionis(resepsionis_id) ON DELETE SET NULL,
  FOREIGN KEY (jadwal_id) REFERENCES Jadwal_dokter(jadwal_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Rekam_medis
(
  rekam_id INT NOT NULL AUTO_INCREMENT,
  diagnosis VARCHAR(100) NOT NULL,
  description VARCHAR(255) NOT NULL,
  appointment_id INT NOT NULL,
  PRIMARY KEY (rekam_id),
  FOREIGN KEY (appointment_id) REFERENCES Appointment(appointment_id) ON DELETE CASCADE
);

-- 3. INSERT SAMPLE DATA (Optional - untuk testing)

INSERT INTO Pasien (email, password, nama_depan, nama_belakang, gender, tanggal_daftar, tanggal_lahir, Kota, Jalan) 
VALUES 
('test@example.com', 'password123', 'Test', 'User', 'Male', CURDATE(), '1990-01-01', 'Jakarta', 'Jl. Test No. 123'),
('admin@clinic.com', 'admin', 'Admin', 'Clinic', 'Female', CURDATE(), '1985-05-15', 'Bandung', 'Jl. Admin No. 1');

-- ========================================
-- SETUP COMPLETE!
-- ========================================
