CREATE TABLE `users_data` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(50) NOT NULL,
  `cpf` VARCHAR(11) NOT NULL,
  `email` VARCHAR(50) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `gender` ENUM('M','F','I') NOT NULL,
  `phone` VARCHAR(14) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `cpf` (`cpf`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `users_data` (`id`, `name`, `cpf`, `email`, `password`, `gender`, `phone`) VALUES
(1, 'Vivian Lethycia', '06673469021', 'vivian@hotmail.com', '$2b$12$/w21unHeqBEcHVN8g4inOujZQ.XgSVqaf4Pv0VYbPdEa1zMlVbNf2', 'F', '(11)98725-6530');
