SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


DROP DATABASE IF EXISTS `purbeurre` ;
CREATE DATABASE IF NOT EXISTS `purbeurre` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `purbeurre`;


DROP TABLE IF EXISTS `product` ;
CREATE TABLE IF NOT EXISTS `product` (
  `id_product` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) DEFAULT NULL UNIQUE,
  `nutriscore` int(11) DEFAULT NULL,
  `url` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`id_product`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `category` ;
CREATE TABLE IF NOT EXISTS `category` (
  `id_category` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) DEFAULT NULL UNIQUE,
  PRIMARY KEY (`id_category`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `store` ;
CREATE TABLE IF NOT EXISTS `store` (
  `id_store` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) DEFAULT NULL UNIQUE,
  PRIMARY KEY (`id_store`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `category_product` ;
CREATE TABLE IF NOT EXISTS `category_product` (
  `id_category` int(11) NOT NULL,
  `id_product` int(11) NOT NULL,
  PRIMARY KEY (`id_category`, `id_product`),
  KEY `fk_category_product_category_idx` (`id_category`),
  KEY `fk_category_product_product_idx` (`id_product`),
  CONSTRAINT `fk_category_product_category` FOREIGN KEY (`id_category`) REFERENCES `category` (`id_category`),
  CONSTRAINT `fk_category_product_product` FOREIGN KEY (`id_product`) REFERENCES `product` (`id_product`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `store_product` ;
CREATE TABLE IF NOT EXISTS `store_product` (
  `id_store` int(11) NOT NULL,
  `id_product` int(11) NOT NULL,
  PRIMARY KEY (`id_store`, `id_product`),
  KEY `fk_store_product_store_idx` (`id_store`),
  KEY `fk_store_product_product_idx` (`id_product`),
  CONSTRAINT `fk_store_product_store` FOREIGN KEY (`id_store`) REFERENCES `store` (`id_store`),
  CONSTRAINT `fk_store_product_product` FOREIGN KEY (`id_product`) REFERENCES `product` (`id_product`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `favorite_product` ;
CREATE TABLE IF NOT EXISTS `favorite_product` (
  id_base_product int(11) NOT NULL,
  id_substitute_product int(11) NOT NULL,
  PRIMARY KEY (`id_base_product`,`id_substitute_product`),
  KEY `fk_favorite_product1_idx` (`id_base_product`),
  KEY `fk_favorite_product2_idx` (`id_substitute_product`),
  CONSTRAINT `fk_favorite_product1` FOREIGN KEY (`id_base_product`) REFERENCES `product` (`id_product`),
  CONSTRAINT `fk_favorite_product2` FOREIGN KEY (`id_substitute_product`) REFERENCES `product` (`id_product`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
