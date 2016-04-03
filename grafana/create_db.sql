flush privileges;
create DATABASE grafana;

create user 'grafanauser'@'localhost' identified by 'aoL7iJ23ayX3FMrveS';

GRANT ALL PRIVILEGES ON grafana. * TO 'grafanauser'@'localhost' identified by 'aoL7iJ23ayX3FMrveS';

flush privileges;
