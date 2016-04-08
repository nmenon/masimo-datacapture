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

Apache2 setup
==============
* Modify grafana.ini for:

```shell
# Protocol (http or https)
protocol = http
# The ip address to bind to, empty will bind to all interfaces
http_addr = localhost

# The full public facing url
root_url = %(protocol)s://%(domain)s:%(http_port)s/limited/stats


```
NOTE: if you'd like apps like background screen savers to work without needing login:
```
  # enable anonymous access
 enabled = true
  
  # specify organization name that should be used for unauthenticated users
 org_name = Organization
  
  # specify role for unauthenticated users
 org_role = Viewer
``

* Enable Reverse Proxy over apache

First install apache2 and install ssl as your default:
Some useful websites:
* https://www.digicert.com/ssl-certificate-installation-ubuntu-server-with-apache2.htm
* https://www.digitalocean.com/community/tutorials/how-to-create-a-ssl-certificate-on-apache-for-ubuntu-14-04


```bash
	sudo  a2enmod proxy
```

in /etc/apache2/sites-available/default-ssl.conf -> since we enable  ssl, the changes are
as follows (based on Debian Jessie):

```patch
diff --git a/apache2/sites-available/default-ssl.conf b/apache2/sites-available/default-ssl.conf
index 230e812..6b81211 100644
--- a/apache2/sites-available/default-ssl.conf
+++ b/apache2/sites-available/default-ssl.conf
@@ -1,3 +1,6 @@
+LoadModule proxy_module /usr/lib/apache2/modules/mod_proxy.so
+LoadModule proxy_http_module /usr/lib/apache2/modules/mod_proxy_http.so
+
 <IfModule mod_ssl.c>
        <VirtualHost _default_:443>
                ServerAdmin someone@somewhere.com
@@ -131,6 +134,10 @@
                # MSIE 7 and newer should be able to use keepalive
                BrowserMatch "MSIE [17-9]" ssl-unclean-shutdown
 
+           # Grafana Proxy setup
+           ProxyPreserveHost On
+           ProxyPass /limited/stats http://localhost:4800
+           ProxyPassReverse /limited/stats http://localhost:4800
        </VirtualHost>
 </IfModule>
 
```

Apache2 Setup with SSL and HTTP
===============================

Typically we would NOT like to expose http clients to the bad internet
outside world without some level of authentication.

So, using apache proxy, we can create two sites: an http world
for inside the home(secure private network) and https world with
authentication for external world. NOTE:
* sites-available/000-default.conf is your http webpage
* sites-available/default-ssl.conf is your secure https webpage settings
you need to link them in the /etc/apache2/sites-enabled directory for them to
be active. a simple step as follows will do the job
```bash
cd /etc/apache2/sites-enabled
ln -s ../sites-available/000-default.conf
ln -s ../sites-available/default-ssl.conf
```

<b> See http://www.colostate.edu/~ric/htpass.html for information on how to create a password
access control for Apache</b>

```patch
diff --git a/apache2/sites-available/000-default.conf b/apache2/sites-available/000-default.conf
index cfe8df5..6462a56 100644
--- a/apache2/sites-available/000-default.conf
+++ b/apache2/sites-available/000-default.conf
@@ -26,6 +26,12 @@
        # following line enables the CGI configuration for this host only
        # after it has been globally disabled with "a2disconf".
        #Include conf-available/serve-cgi-bin.conf
+
+       # Grafana Proxy setup
+       ProxyPreserveHost On
+       ProxyPass /limited/stats http://localhost:9600
+       ProxyPassReverse /limited/stats http://localhost:9600
+
 </VirtualHost>
 
 # vim: syntax=apache ts=4 sw=4 sts=4 sr noet
diff --git a/apache2/sites-available/default-ssl.conf b/apache2/sites-available/default-ssl.conf
index 6b81211..7be0ec0 100644
--- a/apache2/sites-available/default-ssl.conf
+++ b/apache2/sites-available/default-ssl.conf
@@ -138,6 +138,15 @@ LoadModule proxy_http_module /usr/lib/apache2/modules/mod_proxy_http.so
            ProxyPreserveHost On
            ProxyPass /limited/stats http://localhost:9600
            ProxyPassReverse /limited/stats http://localhost:9600
+           # Grafana Authentication setup
+           <Location "/limited/stats">
+                       AuthType Basic
+                       AuthName "Gimme Your Creds"
+                       AuthUserFile "/opt/secureworld/.htpasswd"
+                       Require valid-user
+                       Order allow,deny
+                       Allow from all
+           </Location>
        </VirtualHost>
 </IfModule>
 

```
<b>
IMPORTANT NOTE: The credentials accessed over https is also used to authenticate
on grafana end as well. So, ensure the username and password match.
</b>

Also See https://blog.raintank.io/authproxy-howto-use-external-authentication-handlers-with-grafana/
I <b>DONOT</b> recommend that you auto signup users. Be careful who you let in your home aka your data..

Setting up Linux screensaver with webpage
========================================
Thanks to http://blog.kaiserapps.com/2014/02/how-to-set-webpage-as-screensaver-in.html
Copy https://github.com/lmartinking/webscreensaver

Modify ~/.xscreensaver as follows:

* If direct hosting locally:

```script
programs:                                                                     \
          webscreensaver -u                             \
          https://192.168.1.6/dashboard/db/data \n\
```


* If hosting over apache proxy:

```script
programs:                                                                     \
          webscreensaver -u                             \
          https://192.168.1.6/limited/stats/dashboard/db/data \n\
```

Setting up Windows screensaver with webpage
========================================
Thanks to yahantan from https://github.com/yahnatan/pulseox/blob/master/README.md

```
I am using https://github.com/rocketinventor/web-page-screensaver to
bring the default medical monitoring dashboard up on the screen of
the computer in my son's room. I also set one corner of the screen as
a "hot corner" to activate the screensaver,so that any of my son's
caregivers can quickly bring the Grafana monitoring dashboard back up.
```

windows 7 quick link: 
https://github.com/rocketinventor/web-page-screensaver/raw/master/Web-Page-Screensaver.scr


Setting up Android screensaver
==============================
https://play.google.com/store/apps/details?id=uk.co.liamnewmarch.daydream&hl=en
