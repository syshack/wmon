CREATE TABLE IF NOT EXISTS `wmon_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `server_name` varchar(128) NOT NULL,
  `ip` varchar(15) NOT NULL,
  `time` int(11) NOT NULL,
  `localtime` char(19) NOT NULL,
  `cpu` text NOT NULL,
  `uptime` text NOT NULL,
  `load` text NOT NULL,
  `top` text NOT NULL,
  `partitions` text NOT NULL,
  `services` text NOT NULL,
  PRIMARY KEY (`id`),
  KEY `server_name` (`server_name`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8;
