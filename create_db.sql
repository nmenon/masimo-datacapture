flush privileges;
create DATABASE logmasimo;

create user 'logmasimo'@'192.168.0.1' identified by 'log@masimo-iXie3ahl';

GRANT ALL PRIVILEGES ON logmasimo . * TO 'logmasimo'@'192.168.0.1' identified by 'log@masimo-iXie3ahl';

flush privileges;
USE logmasimo;

CREATE TABLE `data` (
	`id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Unique Identifier',
	`ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Time stamp of data',
	`spo2` int(11) DEFAULT 0 COMMENT 'O2 % (peripheral capillary oxygen saturation)',
	`bpm` int(11) DEFAULT 0 COMMENT 'Beats Per Minute',
	`pi` int(11) DEFAULT 0 COMMENT 'Perfusion Index',
	`alarm` int(11) DEFAULT 0 COMMENT 'Raw Alarm value',
	`exc` int(11) DEFAULT 0 COMMENT 'Raw Exception',
	`exc1` int(11) DEFAULT 0 COMMENT 'Raw Exception 1',
	`exc_sensor_no` Boolean NOT NULL Default 0 COMMENT 'No Sensor?',
	`exc_sensor_defective` Boolean NOT NULL Default 0 COMMENT 'Sensor is Defective',
	`exc_low_perfusion` Boolean NOT NULL Default 0 COMMENT 'Low Perfusion Index',
	`exc_pulse_search` Boolean NOT NULL Default 0 COMMENT 'Searching for pulse',
	`exc_interference` Boolean NOT NULL Default 0 COMMENT 'External Interference..??',
	`exc_sensor_off` Boolean NOT NULL Default 0 COMMENT 'Sensor is OFF',
	`exc_ambient_light` Boolean NOT NULL Default 0 COMMENT 'Ambient Light',
	`exc_sensor_unrecognized` Boolean NOT NULL Default 0 COMMENT 'Sensor is Unrecognized',
	`exc_low_signal_iq` Boolean NOT NULL Default 0 COMMENT 'Signal IQ is low',
	`exc_masimo_set` Boolean NOT NULL Default 0 COMMENT 'Masimo Set sensor is being used',
	primary key(id),
	key(spo2),
	key(bpm)
	);
show tables;
describe data;
flush privileges;
