-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Dec 23, 2025 at 04:52 AM
-- Server version: 10.4.28-MariaDB
-- PHP Version: 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `Rekam_medis`;
DROP TABLE IF EXISTS `Pasien_telepon`;
DROP TABLE IF EXISTS `Resepsionis_telepon`;
DROP TABLE IF EXISTS `Dokter_telepon`;
DROP TABLE IF EXISTS `Dijadwalkan`;
DROP TABLE IF EXISTS `Appointment`;
DROP TABLE IF EXISTS `Jadwal_dokter`;
DROP TABLE IF EXISTS `Resepsionis`;
DROP TABLE IF EXISTS `Dokter`;
DROP TABLE IF EXISTS `Pasien`;

SET FOREIGN_KEY_CHECKS = 1;

--
-- Database: `DBProject`
--

-- --------------------------------------------------------

--
-- Table structure for table `Appointment`
--

CREATE TABLE `Appointment` (
  `appointment_id` int(11) NOT NULL,
  `tanggal` date NOT NULL,
  `waktu` char(13) NOT NULL,
  `status` varchar(20) NOT NULL,
  `pasien_id` int(11) NOT NULL,
  `dokter_id` int(11) NOT NULL,
  `resepsionis_id` int(11) DEFAULT NULL,
  `jadwal_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `Appointment`
--

INSERT INTO `Appointment` (`appointment_id`, `tanggal`, `waktu`, `status`, `pasien_id`, `dokter_id`, `resepsionis_id`, `jadwal_id`) VALUES
(1, '2025-11-23', '09:30', 'completed', 4, 1, NULL, 1);

-- --------------------------------------------------------

--
-- Table structure for table `Dijadwalkan`
--

CREATE TABLE `Dijadwalkan` (
  `dokter_id` int(11) NOT NULL,
  `jadwal_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `Dijadwalkan`
--

INSERT INTO `Dijadwalkan` (`dokter_id`, `jadwal_id`) VALUES
(1, 1),
(2, 2),
(3, 3),
(4, 4),
(5, 5);

-- --------------------------------------------------------

--
-- Table structure for table `Dokter`
--

CREATE TABLE `Dokter` (
  `dokter_id` int(11) NOT NULL,
  `nama_depan` varchar(50) NOT NULL,
  `nama_belakang` varchar(50) NOT NULL,
  `tanggal_masuk` date NOT NULL,
  `status` varchar(20) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `foto` varchar(255) DEFAULT 'default.jpg'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `Dokter`
--


INSERT INTO `Dokter` (`dokter_id`, `nama_depan`, `nama_belakang`, `tanggal_masuk`, `status`, `email`, `password`, `foto`) VALUES
(1, 'Rafathin', 'Ardian', '2025-11-23', 'Active', NULL, NULL, 'doctor1.jpg'),
(2, 'James', 'Wilson', '2025-11-23', 'Active', NULL, NULL, 'doctor2.jpg'),
(3, 'Emily', 'Carter', '2025-11-23', 'Active', 'emily@gmail.com', '1111111', 'doctor3.jpg'),
(4, 'Michael', 'Brown', '2025-11-23', 'Active', NULL, NULL, 'doctor4.jpg'),
(5, 'David', 'Kim', '2025-11-23', 'Active', NULL, NULL, 'doctor5.jpg');

-- --------------------------------------------------------

--
-- Table structure for table `Dokter_telepon`
--

CREATE TABLE `Dokter_telepon` (
  `telepon` varchar(50) NOT NULL,
  `dokter_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `Jadwal_dokter`
--

CREATE TABLE `Jadwal_dokter` (
  `jadwal_id` int(11) NOT NULL,
  `hari` varchar(10) NOT NULL,
  `jam_mulai` char(5) NOT NULL,
  `jam_selesai` char(5) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `Jadwal_dokter`
--

INSERT INTO `Jadwal_dokter` (`jadwal_id`, `hari`, `jam_mulai`, `jam_selesai`) VALUES
(1, 'Senin', '09:00', '12:00'),
(2, 'Selasa', '10:00', '14:00'),
(3, 'Rabu', '08:00', '12:00'),
(4, 'Kamis', '13:00', '17:00'),
(5, 'Jumat', '09:00', '15:00');

-- --------------------------------------------------------

--
-- Table structure for table `Pasien`
--

CREATE TABLE `Pasien` (
  `pasien_id` int(11) NOT NULL,
  `nama_depan` varchar(50) DEFAULT NULL,
  `nama_belakang` varchar(50) DEFAULT NULL,
  `email` varchar(100) NOT NULL,
  `gender` enum('Male','Female') DEFAULT NULL,
  `tanggal_daftar` date DEFAULT current_timestamp(),,
  `tanggal_lahir` date DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `kota` varchar(50) DEFAULT NULL,
  `jalan` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `Pasien`
--

INSERT INTO `Pasien` (`pasien_id`, `nama_depan`, `nama_belakang`, `email`, `gender`, `tanggal_daftar`, `tanggal_lahir`, `password`, `kota`, `jalan`) VALUES
(2, 'Rafathin', 'Ardian Satari', 'rafa', 'Male', '2025-11-17', '2007-05-14', 'aliya', 'Makassar', 'Jl Nikel 3'),
(4, 'Farsya', 'Nabila Tori', 'tori@gmail.com', 'Female', '2025-11-23', '2006-02-02', 'pbkdf2:sha256:1000000$MtqjXlpCU1aw13Tc$1ece0052c0020d8a78951a7b0b7d7d95505aed57d6a0325699e33c4b5f94e64e', 'Medan', 'JL Kaliurang KM. 200 No. 28');

-- --------------------------------------------------------

--
-- Table structure for table `Pasien_telepon`
--

CREATE TABLE `Pasien_telepon` (
  `telepon` varchar(50) NOT NULL,
  `pasien_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `Pasien_telepon`
--

INSERT INTO `Pasien_telepon` (`telepon`, `pasien_id`) VALUES
('0838238974328', 2),
('2938472892323', 4),
('3874823473847', 2),
('3928473284732', 2);

-- --------------------------------------------------------

--
-- Table structure for table `Rekam_medis`
--

CREATE TABLE `Rekam_medis` (
  `rekam_id` int(11) NOT NULL,
  `diagnosis` varchar(100) NOT NULL,
  `description` varchar(255) NOT NULL,
  `appointment_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `Rekam_medis`
--

INSERT INTO `Rekam_medis` (`rekam_id`, `diagnosis`, `description`, `appointment_id`) VALUES
(1, 'Flu Berat', 'Pasien demam tinggi, diberikan paracetamol dan istirahat.', 1);


-- --------------------------------------------------------

--
-- Table structure for table `Resepsionis`
--

CREATE TABLE `Resepsionis` (
  `resepsionis_id` int(11) NOT NULL,
  `nama_depan` varchar(50) NOT NULL,
  `nama_belakang` varchar(50) NOT NULL,
  `tanggal_masuk` date NOT NULL,
  `status` varchar(20) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `Resepsionis_telepon`
--

CREATE TABLE `Resepsionis_telepon` (
  `telepon` varchar(50) NOT NULL,
  `resepsionis_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Dumping data for table `Resepsionis`
--

INSERT INTO `Resepsionis` (`resepsionis_id`, `nama_depan`, `nama_belakang`, `tanggal_masuk`, `status`, `email`, `password`) VALUES
(1, 'Aliya', 'Rahman', '2025-11-23', 'Active', 'aliya@gmail.com', '11111111');

--
-- Dumping data for table `Dokter` (additional)
--

INSERT INTO `Dokter` (`dokter_id`, `nama_depan`, `nama_belakang`, `tanggal_masuk`, `status`, `email`, `password`, `foto`) VALUES
(6, 'Aliya', 'Rahman', '2025-11-23', 'Active', 'aliya@gmail.com', '11111111', 'default.jpg');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `Appointment`
--
ALTER TABLE `Appointment`
  ADD PRIMARY KEY (`appointment_id`),
  ADD KEY `pasien_id` (`pasien_id`),
  ADD KEY `dokter_id` (`dokter_id`),
  ADD KEY `resepsionis_id` (`resepsionis_id`),
  ADD KEY `jadwal_id` (`jadwal_id`);

--
-- Indexes for table `Dijadwalkan`
--
ALTER TABLE `Dijadwalkan`
  ADD PRIMARY KEY (`dokter_id`,`jadwal_id`),
  ADD KEY `jadwal_id` (`jadwal_id`);

--
-- Indexes for table `Dokter`
--
ALTER TABLE `Dokter`
  ADD PRIMARY KEY (`dokter_id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `Dokter_telepon`
--
ALTER TABLE `Dokter_telepon`
  ADD PRIMARY KEY (`telepon`,`dokter_id`),
  ADD KEY `dokter_id` (`dokter_id`);

--
-- Indexes for table `Jadwal_dokter`
--
ALTER TABLE `Jadwal_dokter`
  ADD PRIMARY KEY (`jadwal_id`);

--
-- Indexes for table `Pasien`
--
ALTER TABLE `Pasien`
  ADD PRIMARY KEY (`pasien_id`);

--
-- Indexes for table `Pasien_telepon`
--
ALTER TABLE `Pasien_telepon`
  ADD PRIMARY KEY (`telepon`,`pasien_id`),
  ADD KEY `pasien_id` (`pasien_id`);

--
-- Indexes for table `Rekam_medis`
--
ALTER TABLE `Rekam_medis`
  ADD PRIMARY KEY (`rekam_id`),
  ADD KEY `appointment_id` (`appointment_id`);

--
-- Indexes for table `Resepsionis`
--
ALTER TABLE `Resepsionis`
  ADD PRIMARY KEY (`resepsionis_id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `Resepsionis_telepon`
--
ALTER TABLE `Resepsionis_telepon`
  ADD PRIMARY KEY (`telepon`,`resepsionis_id`),
  ADD KEY `resepsionis_id` (`resepsionis_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `Appointment`
--
ALTER TABLE `Appointment`
  MODIFY `appointment_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `Dokter`
--
ALTER TABLE `Dokter`
  MODIFY `dokter_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `Jadwal_dokter`
--
ALTER TABLE `Jadwal_dokter`
  MODIFY `jadwal_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `Pasien`
--
ALTER TABLE `Pasien`
  MODIFY `pasien_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `Rekam_medis`
--
ALTER TABLE `Rekam_medis`
  MODIFY `rekam_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `Resepsionis`
--
ALTER TABLE `Resepsionis`
  MODIFY `resepsionis_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `Appointment`
--
ALTER TABLE `Appointment`
  ADD CONSTRAINT `appointment_ibfk_1` FOREIGN KEY (`pasien_id`) REFERENCES `Pasien` (`pasien_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `appointment_ibfk_2` FOREIGN KEY (`dokter_id`) REFERENCES `Dokter` (`dokter_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `appointment_ibfk_3` FOREIGN KEY (`resepsionis_id`) REFERENCES `Resepsionis` (`resepsionis_id`) ON DELETE SET NULL,
  ADD CONSTRAINT `appointment_ibfk_4` FOREIGN KEY (`jadwal_id`) REFERENCES `Jadwal_dokter` (`jadwal_id`) ON DELETE CASCADE;

--
-- Constraints for table `Dijadwalkan`
--
ALTER TABLE `Dijadwalkan`
  ADD CONSTRAINT `dijadwalkan_ibfk_1` FOREIGN KEY (`dokter_id`) REFERENCES `Dokter` (`dokter_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `dijadwalkan_ibfk_2` FOREIGN KEY (`jadwal_id`) REFERENCES `Jadwal_dokter` (`jadwal_id`) ON DELETE CASCADE;

--
-- Constraints for table `Dokter_telepon`
--
ALTER TABLE `Dokter_telepon`
  ADD CONSTRAINT `dokter_telepon_ibfk_1` FOREIGN KEY (`dokter_id`) REFERENCES `Dokter` (`dokter_id`) ON DELETE CASCADE;

--
-- Constraints for table `Pasien_telepon`
--
ALTER TABLE `Pasien_telepon`
  ADD CONSTRAINT `pasien_telepon_ibfk_1` FOREIGN KEY (`pasien_id`) REFERENCES `Pasien` (`pasien_id`);

--
-- Constraints for table `Rekam_medis`
--
ALTER TABLE `Rekam_medis`
  ADD CONSTRAINT `rekam_medis_ibfk_1` FOREIGN KEY (`appointment_id`) REFERENCES `Appointment` (`appointment_id`) ON DELETE CASCADE;

--
-- Constraints for table `Resepsionis_telepon`
--
ALTER TABLE `Resepsionis_telepon`
  ADD CONSTRAINT `resepsionis_telepon_ibfk_1` FOREIGN KEY (`resepsionis_id`) REFERENCES `Resepsionis` (`resepsionis_id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
