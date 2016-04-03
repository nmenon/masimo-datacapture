grafana: v2.6.0 on Debian Jessie

Installation
============
See: http://docs.grafana.org/installation/debian/
1. Switch to sudo shell
		sudo su
2. Install https proto for apt
		apt-get install apt-transport-https
3. Put the grafana sources for apt
		echo 'deb https://packagecloud.io/grafana/testing/debian/ jessie main'>/etc/apt/sources.list.d/grafana.list
4. Get the keys please.
		curl https://packagecloud.io/gpg.key | apt-key add -
5. And... install..
		apt-get update && apt-get install grafana


Configuration
=============
See: http://docs.grafana.org/installation/configuration/
Example [grafana.ini][file://grafana.ini] which I use is modified from /etc/grafana/grafana.ini .

I like mysql for some legacy reasons, so we use mysql instead of sqlite3 default
for storing configuration data. Feel free to change things as you see fit.

Startup the server
==================
Start things up with systemd:
	systemctl daemon-reload
	systemctl start grafana-server
	systemctl status grafana-server


the status should show if something is broken. if yes, needs a bunch of fixups and
permission etc..
