-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Dec 13, 2025 at 11:28 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `airline_system`
--

-- --------------------------------------------------------

--
-- Table structure for table `aircrafts`
--

CREATE TABLE `aircrafts` (
  `aircraft_id` int(11) NOT NULL,
  `model` varchar(50) DEFAULT NULL,
  `status` enum('Active','In-Maintenance') DEFAULT 'Active'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `aircrafts`
--

INSERT INTO `aircrafts` (`aircraft_id`, `model`, `status`) VALUES
(1, 'Boeing 737', 'Active'),
(2, 'Airbus A320', 'Active'),
(5, '22323', 'Active');

-- --------------------------------------------------------

--
-- Table structure for table `bookings`
--

CREATE TABLE `bookings` (
  `booking_id` int(11) NOT NULL,
  `pnr` varchar(6) DEFAULT NULL,
  `flight_id` int(11) DEFAULT NULL,
  `passenger_id` int(11) DEFAULT NULL,
  `seat_class` enum('Economy','Business') DEFAULT NULL,
  `seat_number` varchar(5) DEFAULT NULL,
  `price` decimal(10,2) DEFAULT NULL,
  `status` enum('Confirmed','Cancelled') DEFAULT 'Confirmed'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `bookings`
--

INSERT INTO `bookings` (`booking_id`, `pnr`, `flight_id`, `passenger_id`, `seat_class`, `seat_number`, `price`, `status`) VALUES
(1, 'LBB2SO', 1, 2, 'Business', '10', 15000.00, 'Confirmed'),
(3, 'EGSNEZ', 1, 2, 'Business', '10', 15000.00, 'Confirmed'),
(4, 'RA9PVP', 1, 4, 'Business', '10', 15000.00, 'Cancelled'),
(5, 'COUJ3Y', 1, 5, 'Business', '12', 15000.00, 'Confirmed'),
(6, 'PV3OE1', 1, 7, 'Economy', '10A', 5000.00, 'Confirmed'),
(7, 'K9UVQ2', 1, 8, 'Business', '11A', 15000.00, 'Confirmed'),
(8, 'G53ZWT', 1, 9, 'Business', '10B', 15000.00, 'Confirmed'),
(9, 'B4AG44', 1, 10, 'Business', '30A', 15000.00, 'Confirmed');

-- --------------------------------------------------------

--
-- Table structure for table `checkin`
--

CREATE TABLE `checkin` (
  `checkin_id` int(11) NOT NULL,
  `booking_id` int(11) DEFAULT NULL,
  `bags_checked` int(11) DEFAULT NULL,
  `boarding_time` datetime DEFAULT current_timestamp(),
  `status` enum('Checked-In','Boarded','No-Show') DEFAULT 'Checked-In'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `checkin`
--

INSERT INTO `checkin` (`checkin_id`, `booking_id`, `bags_checked`, `boarding_time`, `status`) VALUES
(1, 3, 2, '2025-12-05 21:10:11', 'Checked-In');

-- --------------------------------------------------------

--
-- Table structure for table `crew`
--

CREATE TABLE `crew` (
  `crew_id` int(11) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `role` varchar(50) DEFAULT NULL,
  `status` enum('Available','On-Duty','Resting') DEFAULT 'Available',
  `salary_rate` int(11) DEFAULT 5000,
  `license_status` varchar(50) DEFAULT 'Active',
  `flight_hours` int(11) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `crew`
--

INSERT INTO `crew` (`crew_id`, `name`, `role`, `status`, `salary_rate`, `license_status`, `flight_hours`) VALUES
(1, 'Capt. Ri', 'Captain', 'Available', 150000, 'Active', 100),
(2, 'Christian Daing', 'Captain', 'On-Duty', 150000, 'Active', 54),
(3, 'Michael Boquiron', 'First Officer', 'On-Duty', 90000, 'Active', 24),
(4, 'Ken Sebastian', 'First Officer', 'Available', 90000, 'Active', 30),
(5, 'John Paul Irenio', 'Second Officer', 'Available', 60000, 'Active', 10),
(6, 'Sarah Lin', 'Purser', 'Available', 40000, 'Active', 80),
(7, 'Jhastine Bieber', 'Flight Attendant', 'On-Duty', 25000, 'Active', 44),
(8, 'John Martin', 'Flight Attendant', 'Available', 25000, 'Active', 40),
(9, 'Jordan Cabs', 'Flight Attendant', 'Available', 25000, 'Active', 10),
(10, 'Carlos Smith', 'Loadmaster', 'Available', 30000, 'Active', 5),
(11, 'Capt. Marco De Leon', 'Captain', 'Available', 150000, 'Active', 110),
(12, 'Capt. Victoria Vance', 'Captain', 'Available', 152000, 'Active', 140),
(13, 'Capt. Elias Thorne', 'Captain', 'Available', 148000, 'Active', 95),
(14, 'Lucas Wright', 'First Officer', 'Available', 92000, 'Active', 45),
(15, 'Aiyah Lopez', 'First Officer', 'Available', 89000, 'Active', 30),
(16, 'David Kim', 'First Officer', 'Available', 90000, 'Active', 55),
(17, 'Kevin Tan', 'Second Officer', 'Available', 62000, 'Active', 15),
(18, 'Rachel Green', 'Purser', 'Available', 46000, 'Active', 100),
(19, 'Mateo Guidicelli', 'Purser', 'Available', 44000, 'Active', 85),
(20, 'Jenny Dizon', 'Flight Attendant', 'Available', 25000, 'Active', 20),
(21, 'Markus Cruz', 'Flight Attendant', 'Available', 25000, 'Active', 22),
(22, 'Bea Morales', 'Flight Attendant', 'Available', 26000, 'Active', 35),
(23, 'Rico Pascual', 'Flight Attendant', 'Available', 24000, 'Active', 12),
(24, 'Sofia Andres', 'Flight Attendant', 'Available', 25000, 'Active', 18),
(25, 'Nurse Elena Cruz', 'Flight Nurse', 'Available', 36000, 'Active', 50),
(26, 'Agent Jack Reacher', 'Air Marshal', 'Available', 52000, 'Active', 10),
(27, 'Maria Clara', 'Flight Nurse', 'Available', 35000, 'Active', 40),
(28, 'Dr. Derek Shepherd', 'Flight Nurse', 'Available', 38000, 'Active', 120),
(29, 'Nurse Joy', 'Flight Nurse', 'Available', 32000, 'Active', 15),
(30, 'Ricardo Dalisay', 'Air Marshal', 'Available', 55000, 'Active', 200),
(31, 'Ethan Hunt', 'Air Marshal', 'Available', 58000, 'Active', 150),
(32, 'Natasha Romanoff', 'Air Marshal', 'Available', 60000, 'Active', 180),
(33, 'Arthur Curry', 'Loadmaster', 'Available', 30000, 'Active', 50),
(34, 'Gregor Clegane', 'Loadmaster', 'Available', 32000, 'Active', 60),
(35, 'Montgomery Scott', 'Flight Engineer', 'Available', 70000, 'Active', 300),
(36, 'Tony Stark', 'Flight Engineer', 'Available', 75000, 'Active', 500);

-- --------------------------------------------------------

--
-- Table structure for table `crew_roles`
--

CREATE TABLE `crew_roles` (
  `role_id` int(11) NOT NULL,
  `role_name` varchar(50) NOT NULL,
  `default_salary` int(11) DEFAULT 5000
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `crew_roles`
--

INSERT INTO `crew_roles` (`role_id`, `role_name`, `default_salary`) VALUES
(1, 'Captain', 150000),
(2, 'First Officer', 90000),
(3, 'Second Officer', 60000),
(4, 'Flight Engineer', 70000),
(5, 'Purser', 40000),
(6, 'Flight Attendant', 25000),
(7, 'Flight Nurse', 35000),
(8, 'Air Marshal', 50000),
(9, 'Loadmaster', 30000);

-- --------------------------------------------------------

--
-- Table structure for table `feedback`
--

CREATE TABLE `feedback` (
  `feedback_id` int(11) NOT NULL,
  `passenger_id` int(11) DEFAULT NULL,
  `category` varchar(50) DEFAULT NULL,
  `message` text DEFAULT NULL,
  `status` varchar(20) DEFAULT 'Open',
  `date_filed` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `feedback`
--

INSERT INTO `feedback` (`feedback_id`, `passenger_id`, `category`, `message`, `status`, `date_filed`) VALUES
(1, 2, 'Feedback', 'It\'s Amazing Customer Service Thank you for your hardwork keep it up!', 'Resolved', '2025-12-06 00:22:53');

-- --------------------------------------------------------

--
-- Table structure for table `flights`
--

CREATE TABLE `flights` (
  `flight_id` int(11) NOT NULL,
  `flight_number` varchar(10) DEFAULT NULL,
  `origin` varchar(50) DEFAULT NULL,
  `destination` varchar(50) DEFAULT NULL,
  `flight_date` date DEFAULT NULL,
  `gate` varchar(10) DEFAULT NULL,
  `status` enum('Scheduled','Delayed','Cancelled','Arrived') DEFAULT 'Scheduled',
  `aircraft_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `flights`
--

INSERT INTO `flights` (`flight_id`, `flight_number`, `origin`, `destination`, `flight_date`, `gate`, `status`, `aircraft_id`) VALUES
(1, 'PR101', 'Manila', 'Cebu', '2025-12-25', NULL, 'Scheduled', 1),
(3, '1', 'Manila', 'Hong Kong', '2025-12-05', 'G1', 'Scheduled', 1);

-- --------------------------------------------------------

--
-- Table structure for table `flight_crew`
--

CREATE TABLE `flight_crew` (
  `assignment_id` int(11) NOT NULL,
  `flight_id` int(11) DEFAULT NULL,
  `crew_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `flight_crew`
--

INSERT INTO `flight_crew` (`assignment_id`, `flight_id`, `crew_id`) VALUES
(1, 1, 2),
(2, 1, 3),
(3, 1, 7);

-- --------------------------------------------------------

--
-- Table structure for table `maintenance_logs`
--

CREATE TABLE `maintenance_logs` (
  `log_id` int(11) NOT NULL,
  `aircraft_id` int(11) DEFAULT NULL,
  `issue_description` text DEFAULT NULL,
  `action_taken` varchar(100) DEFAULT NULL,
  `log_date` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `passengers`
--

CREATE TABLE `passengers` (
  `passenger_id` int(11) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `loyalty_points` int(11) DEFAULT 0,
  `tier` enum('Blue','Silver','Gold') DEFAULT 'Blue'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `passengers`
--

INSERT INTO `passengers` (`passenger_id`, `name`, `email`, `phone`, `loyalty_points`, `tier`) VALUES
(1, 'Juan Cruz', 'juan@email.com', NULL, 10000000, 'Silver'),
(2, 'Michael April Boquiron', 'Michael@gmai.com', NULL, 3000, 'Blue'),
(3, '', 'Michael@gmail.com', NULL, 0, 'Blue'),
(4, 'Ken Sapantan Delos Santos Jr.', 'Sapanta@gmail.com', NULL, 1500, 'Blue'),
(5, 'Ken Abner Rapanan Sr.', 'Ken@gmail.com', NULL, 1500, 'Blue'),
(6, 'Jabners Ramos', 'Abner@gmail.com', NULL, 0, 'Blue'),
(7, 'Kent Santino Juan', 'Ramos@gmail.com', NULL, 500, 'Blue'),
(8, 'Eric Yvez Ramos', 'KenRamos@gmail.com', NULL, 1500, 'Blue'),
(9, 'Sander Cruz Ford', 'Sander@gmail.com', NULL, 1500, 'Blue'),
(10, 'Ken Yap', 'KenEricYap@gmail.com', NULL, 1500, 'Blue');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `aircrafts`
--
ALTER TABLE `aircrafts`
  ADD PRIMARY KEY (`aircraft_id`);

--
-- Indexes for table `bookings`
--
ALTER TABLE `bookings`
  ADD PRIMARY KEY (`booking_id`),
  ADD UNIQUE KEY `pnr` (`pnr`),
  ADD KEY `flight_id` (`flight_id`),
  ADD KEY `passenger_id` (`passenger_id`);

--
-- Indexes for table `checkin`
--
ALTER TABLE `checkin`
  ADD PRIMARY KEY (`checkin_id`),
  ADD KEY `booking_id` (`booking_id`);

--
-- Indexes for table `crew`
--
ALTER TABLE `crew`
  ADD PRIMARY KEY (`crew_id`);

--
-- Indexes for table `crew_roles`
--
ALTER TABLE `crew_roles`
  ADD PRIMARY KEY (`role_id`),
  ADD UNIQUE KEY `role_name` (`role_name`);

--
-- Indexes for table `feedback`
--
ALTER TABLE `feedback`
  ADD PRIMARY KEY (`feedback_id`),
  ADD KEY `passenger_id` (`passenger_id`);

--
-- Indexes for table `flights`
--
ALTER TABLE `flights`
  ADD PRIMARY KEY (`flight_id`),
  ADD UNIQUE KEY `flight_number` (`flight_number`),
  ADD KEY `aircraft_id` (`aircraft_id`);

--
-- Indexes for table `flight_crew`
--
ALTER TABLE `flight_crew`
  ADD PRIMARY KEY (`assignment_id`),
  ADD KEY `flight_id` (`flight_id`),
  ADD KEY `crew_id` (`crew_id`);

--
-- Indexes for table `maintenance_logs`
--
ALTER TABLE `maintenance_logs`
  ADD PRIMARY KEY (`log_id`),
  ADD KEY `aircraft_id` (`aircraft_id`);

--
-- Indexes for table `passengers`
--
ALTER TABLE `passengers`
  ADD PRIMARY KEY (`passenger_id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `aircrafts`
--
ALTER TABLE `aircrafts`
  MODIFY `aircraft_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `bookings`
--
ALTER TABLE `bookings`
  MODIFY `booking_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `checkin`
--
ALTER TABLE `checkin`
  MODIFY `checkin_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `crew`
--
ALTER TABLE `crew`
  MODIFY `crew_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=37;

--
-- AUTO_INCREMENT for table `crew_roles`
--
ALTER TABLE `crew_roles`
  MODIFY `role_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `feedback`
--
ALTER TABLE `feedback`
  MODIFY `feedback_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `flights`
--
ALTER TABLE `flights`
  MODIFY `flight_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `flight_crew`
--
ALTER TABLE `flight_crew`
  MODIFY `assignment_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `maintenance_logs`
--
ALTER TABLE `maintenance_logs`
  MODIFY `log_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `passengers`
--
ALTER TABLE `passengers`
  MODIFY `passenger_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `bookings`
--
ALTER TABLE `bookings`
  ADD CONSTRAINT `bookings_ibfk_1` FOREIGN KEY (`flight_id`) REFERENCES `flights` (`flight_id`),
  ADD CONSTRAINT `bookings_ibfk_2` FOREIGN KEY (`passenger_id`) REFERENCES `passengers` (`passenger_id`);

--
-- Constraints for table `checkin`
--
ALTER TABLE `checkin`
  ADD CONSTRAINT `checkin_ibfk_1` FOREIGN KEY (`booking_id`) REFERENCES `bookings` (`booking_id`);

--
-- Constraints for table `feedback`
--
ALTER TABLE `feedback`
  ADD CONSTRAINT `feedback_ibfk_1` FOREIGN KEY (`passenger_id`) REFERENCES `passengers` (`passenger_id`);

--
-- Constraints for table `flights`
--
ALTER TABLE `flights`
  ADD CONSTRAINT `flights_ibfk_1` FOREIGN KEY (`aircraft_id`) REFERENCES `aircrafts` (`aircraft_id`);

--
-- Constraints for table `flight_crew`
--
ALTER TABLE `flight_crew`
  ADD CONSTRAINT `flight_crew_ibfk_1` FOREIGN KEY (`flight_id`) REFERENCES `flights` (`flight_id`),
  ADD CONSTRAINT `flight_crew_ibfk_2` FOREIGN KEY (`crew_id`) REFERENCES `crew` (`crew_id`);

--
-- Constraints for table `maintenance_logs`
--
ALTER TABLE `maintenance_logs`
  ADD CONSTRAINT `maintenance_logs_ibfk_1` FOREIGN KEY (`aircraft_id`) REFERENCES `aircrafts` (`aircraft_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
