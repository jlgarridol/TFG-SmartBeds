
SET NAMES utf8;
SET time_zone = '+00:00';
SET foreign_key_checks = 0;
SET sql_mode = 'NO_AUTO_VALUE_ON_ZERO';

DROP TABLE IF EXISTS `Beds`;
CREATE TABLE `Beds` (
  `MAC` char(12) DEFAULT NULL,
  `bed_name` varchar(50) NOT NULL,
  `UUID` char(12) DEFAULT NULL,
  `port` int(11) unsigned NOT NULL,
  `ip_group` char(15) NOT NULL,
  `IDB` int(11) unsigned NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`IDB`),
  UNIQUE KEY `port` (`port`,`ip_group`),
  UNIQUE KEY `bed_name` (`bed_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `Beds` (`MAC`, `bed_name`, `UUID`, `port`, `ip_group`, `IDB`) VALUES
('886B0F59968A',	'Cama 1',	'00AEFAADD6C3',	5007,	'224.3.29.71',	1);

DROP TABLE IF EXISTS `Users`;
CREATE TABLE `Users` (
  `password` char(88) NOT NULL,
  `token` char(88) NOT NULL,
  `rol` char(5) DEFAULT 'user',
  `nickname` varchar(50) NOT NULL,
  `IDU` int(11) unsigned NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`IDU`),
  UNIQUE KEY `token` (`token`),
  UNIQUE KEY `nickname` (`nickname`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `Users` (`password`, `token`, `rol`, `nickname`, `IDU`) VALUES
('x61Ey612Kl2gpFL56FT9weDnpSo4AV8j8+qx2AuTHdRyY036xxzTTrw10Wq3+4qQyB+XURPWx1ONxp3Y3pB37A==',	'nXnYASKvBsVO4MdhKO1qf1YiBpB5GeElIT/Ucj6Za1bLy3w0UHI4KJ7QUr8hr3vkr9omQRMPGPiRe9HOrfJy0Q==',	'admin',	'admin',	1),
('THr1/U70NU9T0uw4poHagIK2bOxyGsHqNyHvceuwf21MYEZ1pgECb6nF5zdR3hMBThYSQqLHZx5+SDOgp8Ny6g==',	'495IZ7fNxnZzZJRWPRYThqvpudK9EA7Bcj7NHre/8taJgyHKAwokG01ihjmDHSVYGFVKbF34ux2Vm5LovLSczw==',	'user',	'joselu',	6),
('NStTmUyfNNmdsBTrS417GKouoDxRQ5Q/NrE4VDdCpJkacrC1Km9qcIzJauS4qw+kMsWrWITbyLCS+yQ6u6y08w==',	'rrSaSs3Rivm47E3Ot3NrH2QPXxd82+dM+Xixz1D2ynO6NeDBwnuyYOmujJEf8YgWwc/0FDhNB2gCsu+Lwbf3qQ==',	'user',	'alicia',	7);

DROP TABLE IF EXISTS `Users_Beds`;
CREATE TABLE `Users_Beds` (
  `IDB` int(11) unsigned NOT NULL,
  `IDU` int(11) unsigned NOT NULL,
  PRIMARY KEY (`IDU`,`IDB`),
  KEY `IDB` (`IDB`),
  CONSTRAINT `Users_Beds_ibfk_4` FOREIGN KEY (`IDB`) REFERENCES `Beds` (`IDB`) ON DELETE CASCADE,
  CONSTRAINT `Users_Beds_ibfk_5` FOREIGN KEY (`IDU`) REFERENCES `Users` (`IDU`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


