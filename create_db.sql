create DATABASE logmasimo;

create user 'logmasimo'@'192.168.0.1' identified by 'log@masimo-iXie3ahl';

GRANT ALL PRIVILEGES ON logmasimo . * TO 'logmasimo'@'192.168.0.1' identified by 'log@masimo-iXie3ahl';

USE logmasimo;

CREATE TABLE `data` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`spo2` int(11) DEFAULT NULL,
	`bpm` int(11) DEFAULT NULL,
	`pi` int(11) DEFAULT NULL,
	`alarm` int(11) DEFAULT NULL,
	`exec` int(11) DEFAULT NULL,
	`exc1` int(11) DEFAULT NULL,
	primary key(id),
	key(spo2),
	key(bpm)
	);
show tables;
describe data;
