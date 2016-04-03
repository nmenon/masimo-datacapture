flush privileges;
create DATABASE logmasimo;

create user 'logmasimo'@'192.168.0.1' identified by 'log@masimo-iXie3ahl';

GRANT ALL PRIVILEGES ON logmasimo . * TO 'logmasimo'@'192.168.0.1' identified by 'log@masimo-iXie3ahl';

flush privileges;
USE logmasimo;

CREATE TABLE `data` (
	`id` INTEGER(11) NOT NULL AUTO_INCREMENT COMMENT 'Unique Identifier',
	`ts` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Time stamp of data',
	`spo2` TINYINT(3) DEFAULT 0 COMMENT 'O2 % (peripheral capillary oxygen saturation)',
	`bpm` SMALLINT(3) DEFAULT 0 COMMENT 'Beats Per Minute',
	`pi` FLOAT(3,2) DEFAULT 0 COMMENT 'Perfusion Index',
	`alarm` INTEGER(11) DEFAULT 0 COMMENT 'Raw Alarm value',
	`exc` INTEGER(11) DEFAULT 0 COMMENT 'Raw Exception',
	`exc1` INTEGER(11) DEFAULT 0 COMMENT 'Raw Exception 1',
	primary key(id, ts),
	key(spo2),
	key(bpm)
	);
show tables;
describe data;
flush privileges;
