-- MySQL dump 10.13  Distrib 8.0.22, for Win64 (x86_64)
--
-- Host: payhere-database.ch8yxcb5zndd.ap-northeast-2.rds.amazonaws.com    Database: payhere_database
-- ------------------------------------------------------
-- Server version	5.7.41-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;
SET @@SESSION.SQL_LOG_BIN= 0;

--
-- GTID state at the beginning of the backup 
--

SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ '';

--
-- Table structure for table `AccountBook`
--

DROP TABLE IF EXISTS `AccountBook`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `AccountBook` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `date_at` datetime(6) NOT NULL,
  `day_total_money` int(11) NOT NULL,
  `owner_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `AccountBook_owner_id_db6fd5bc_fk_User_id` (`owner_id`),
  CONSTRAINT `AccountBook_owner_id_db6fd5bc_fk_User_id` FOREIGN KEY (`owner_id`) REFERENCES `User` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Expense`
--

DROP TABLE IF EXISTS `Expense`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Expense` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `money` int(11) NOT NULL,
  `expense_detail` varchar(15) DEFAULT NULL,
  `payment_method` varchar(2) NOT NULL,
  `memo` varchar(255) DEFAULT NULL,
  `account_book_id` bigint(20) NOT NULL,
  `category_id` bigint(20) DEFAULT NULL,
  `owner_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `Expense_owner_id_f2ee6ea5_fk_User_id` (`owner_id`),
  KEY `Expense_account_book_id_a001c11d_fk_AccountBook_id` (`account_book_id`),
  KEY `Expense_category_id_442f889d` (`category_id`),
  CONSTRAINT `Expense_account_book_id_a001c11d_fk_AccountBook_id` FOREIGN KEY (`account_book_id`) REFERENCES `AccountBook` (`id`),
  CONSTRAINT `Expense_category_id_442f889d_fk_ExpenseCategory_id` FOREIGN KEY (`category_id`) REFERENCES `ExpenseCategory` (`id`),
  CONSTRAINT `Expense_owner_id_f2ee6ea5_fk_User_id` FOREIGN KEY (`owner_id`) REFERENCES `User` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ExpenseCategory`
--

DROP TABLE IF EXISTS `ExpenseCategory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ExpenseCategory` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `lft` int(10) unsigned NOT NULL,
  `rght` int(10) unsigned NOT NULL,
  `tree_id` int(10) unsigned NOT NULL,
  `level` int(10) unsigned NOT NULL,
  `parent_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `ExpenseCategory_tree_id_b05d46d6` (`tree_id`),
  KEY `ExpenseCategory_parent_id_3f4f3e60` (`parent_id`),
  CONSTRAINT `ExpenseCategory_parent_id_3f4f3e60_fk_ExpenseCategory_id` FOREIGN KEY (`parent_id`) REFERENCES `ExpenseCategory` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ExpenseURL`
--

DROP TABLE IF EXISTS `ExpenseURL`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ExpenseURL` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `shared_url` varchar(200) NOT NULL,
  `expired_at` datetime(6) NOT NULL,
  `expense_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `expense_id` (`expense_id`),
  CONSTRAINT `ExpenseURL_expense_id_ab93406f_fk_Expense_id` FOREIGN KEY (`expense_id`) REFERENCES `Expense` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `Income`
--

DROP TABLE IF EXISTS `Income`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Income` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `money` int(11) NOT NULL,
  `income_detail` varchar(15) DEFAULT NULL,
  `payment_method` varchar(2) DEFAULT NULL,
  `memo` varchar(255) DEFAULT NULL,
  `account_book_id` bigint(20) NOT NULL,
  `category_id` bigint(20) DEFAULT NULL,
  `owner_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `Income_owner_id_b8e6fef1_fk_User_id` (`owner_id`),
  KEY `Income_account_book_id_a0f27bb1_fk_AccountBook_id` (`account_book_id`),
  KEY `Income_category_id_b0237108` (`category_id`),
  CONSTRAINT `Income_account_book_id_a0f27bb1_fk_AccountBook_id` FOREIGN KEY (`account_book_id`) REFERENCES `AccountBook` (`id`),
  CONSTRAINT `Income_category_id_b0237108_fk_IncomeCategory_id` FOREIGN KEY (`category_id`) REFERENCES `IncomeCategory` (`id`),
  CONSTRAINT `Income_owner_id_b8e6fef1_fk_User_id` FOREIGN KEY (`owner_id`) REFERENCES `User` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `IncomeCategory`
--

DROP TABLE IF EXISTS `IncomeCategory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `IncomeCategory` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `lft` int(10) unsigned NOT NULL,
  `rght` int(10) unsigned NOT NULL,
  `tree_id` int(10) unsigned NOT NULL,
  `level` int(10) unsigned NOT NULL,
  `parent_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `IncomeCategory_tree_id_8264f52a` (`tree_id`),
  KEY `IncomeCategory_parent_id_9e39e5a4` (`parent_id`),
  CONSTRAINT `IncomeCategory_parent_id_9e39e5a4_fk_IncomeCategory_id` FOREIGN KEY (`parent_id`) REFERENCES `IncomeCategory` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `IncomeURL`
--

DROP TABLE IF EXISTS `IncomeURL`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `IncomeURL` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `shared_url` varchar(200) NOT NULL,
  `expired_at` datetime(6) NOT NULL,
  `income_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `income_id` (`income_id`),
  CONSTRAINT `IncomeURL_income_id_02a00168_fk_Income_id` FOREIGN KEY (`income_id`) REFERENCES `Income` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `User`
--

DROP TABLE IF EXISTS `User`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `User` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `email` varchar(255) NOT NULL,
  `nickname` varchar(10) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `is_admin` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `nickname` (`nickname`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=61 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_User_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_User_id` FOREIGN KEY (`user_id`) REFERENCES `User` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `token_blacklist_blacklistedtoken`
--

DROP TABLE IF EXISTS `token_blacklist_blacklistedtoken`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `token_blacklist_blacklistedtoken` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `blacklisted_at` datetime(6) NOT NULL,
  `token_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `token_id` (`token_id`),
  CONSTRAINT `token_blacklist_blacklistedtoken_token_id_3cc7fe56_fk` FOREIGN KEY (`token_id`) REFERENCES `token_blacklist_outstandingtoken` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `token_blacklist_outstandingtoken`
--

DROP TABLE IF EXISTS `token_blacklist_outstandingtoken`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `token_blacklist_outstandingtoken` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `token` longtext NOT NULL,
  `created_at` datetime(6) DEFAULT NULL,
  `expires_at` datetime(6) NOT NULL,
  `user_id` bigint(20) DEFAULT NULL,
  `jti` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `token_blacklist_outstandingtoken_jti_hex_d9bdf6f7_uniq` (`jti`),
  KEY `token_blacklist_outstandingtoken_user_id_83bc629a_fk_User_id` (`user_id`),
  CONSTRAINT `token_blacklist_outstandingtoken_user_id_83bc629a_fk_User_id` FOREIGN KEY (`user_id`) REFERENCES `User` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-02-04 18:39:13
