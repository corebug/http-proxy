CREATE DATABASE ProxyUsers DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;

GRANT ALL PRIVILEGES ON ProxyUsers.* TO 'ProxyUser'@'localhost' IDENTIFIED BY 'ProxyUserPass';

CREATE TABLE `users` (
`id` int NOT NULL AUTO_INCREMENT,
`User` char(16) COLLATE utf8_bin NOT NULL DEFAULT '',
`Password` char(41) CHARACTER SET latin1 COLLATE latin1_bin NOT NULL DEFAULT '',
PRIMARY KEY(`id`),
UNIQUE KEY `username` (`User`)
)ENGINE=InnoDB;