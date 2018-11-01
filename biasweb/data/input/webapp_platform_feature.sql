-- phpMyAdmin SQL Dump
-- version 4.7.9
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Nov 01, 2018 at 06:46 PM
-- Server version: 10.1.31-MariaDB
-- PHP Version: 7.2.3

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `biasweb`
--

-- --------------------------------------------------------

--
-- Table structure for table `webapp_platform_feature`
--

CREATE TABLE `webapp_platform_feature` (
  `id` int(11) NOT NULL,
  `feature_name` varchar(100) DEFAULT NULL,
  `feature_symbol` varchar(3) DEFAULT NULL,
  `feature_levels` varchar(126) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `webapp_platform_feature`
--

INSERT INTO `webapp_platform_feature` (`id`, `feature_name`, `feature_symbol`, `feature_levels`) VALUES
(2, 'Interactivity', 'I', 'I.0,I.1'),
(3, 'Revisability', 'R', 'R.0,R.1'),
(4, 'Weight Generation', 'W', 'W.direct,W.AHP'),
(5, 'Alternatives Display Method', 'A', 'A.all,A.1by1,A.2by2,A.user'),
(6, 'Criteria Display', 'C', 'C.full,C.pruned,C.self-extended');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `webapp_platform_feature`
--
ALTER TABLE `webapp_platform_feature`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `webapp_platform_feature`
--
ALTER TABLE `webapp_platform_feature`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
