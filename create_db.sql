flush privileges;
create DATABASE logmasimo;

create user 'logmasimo'@'192.168.0.1' identified by 'log@masimo-iXie3ahl';

GRANT ALL PRIVILEGES ON logmasimo . * TO 'logmasimo'@'192.168.0.1' identified by 'log@masimo-iXie3ahl';

flush privileges;
USE logmasimo;

CREATE TABLE `data` (
	`ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Time stamp of data',
	`spo2` int(3) DEFAULT 0 COMMENT 'O2 % (peripheral capillary oxygen saturation)',
	`bpm` int(3) DEFAULT 0 COMMENT 'Beats Per Minute',
	`pi` float DEFAULT 0 COMMENT 'Perfusion Index',
	`alarm` int(11) DEFAULT 0 COMMENT 'Raw Alarm value',
	`exc` int(11) DEFAULT 0 COMMENT 'Raw Exception',
	`exc1` int(11) DEFAULT 0 COMMENT 'Raw Exception 1',
	primary key(ts),
	key(spo2),
	key(bpm)
	);
show tables;
describe data;
flush privileges;
