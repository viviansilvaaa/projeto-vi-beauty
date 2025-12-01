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

CREATE TABLE `salons` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `description` VARCHAR(255) NULL,
  `address` VARCHAR(500) NOT NULL,
  `phone` VARCHAR(15) NOT NULL,
  `image_url` VARCHAR(500) NOT NULL,
  `opening_day` ENUM('segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado', 'domingo') NOT NULL DEFAULT 'segunda',
  `closing_day` ENUM('segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado', 'domingo') NOT NULL DEFAULT 'sexta',
  `opening_time` TIME NOT NULL DEFAULT '09:00:00',
  `closing_time` TIME NOT NULL DEFAULT '18:00:00',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `hairdressers` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `salon_id` INT(11) NOT NULL,
  `specialties` SET(
    'Corte Masculino',
    'Corte Feminino',
    'Coloracao',
    'Hidratacao',
    'Escova',
    'Alisamento',
    'Penteado',
    'Manicure',
    'Pedicure',
    'Barba',
    'Design de Sobrancelha',
    'Maquiagem'
  ) NULL,
  `phone` VARCHAR(15) NOT NULL,
  `email` VARCHAR(100) NOT NULL,
  `image_url` VARCHAR(500) NULL,
  `bio` TEXT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`salon_id`) REFERENCES `salons`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `appointments` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `user_id` INT(11) NOT NULL,
  `salon_id` INT(11) NOT NULL,
  `hairdresser_id` INT(11) NOT NULL,
  `appointment_date` DATE NOT NULL,
  `appointment_time` TIME NOT NULL,
  `service_type` VARCHAR(255) NOT NULL,
  `status` ENUM('pending', 'confirmed', 'cancelled') NOT NULL DEFAULT 'pending',
  `notes` TEXT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`user_id`) REFERENCES `users_data`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`salon_id`) REFERENCES `salons`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`hairdresser_id`) REFERENCES `hairdressers`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
