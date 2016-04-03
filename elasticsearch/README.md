Elastic Search installation
==========================

This is for the configuartion as follows
```json
	{
	  "name" : "somemachine",
	  "cluster_name" : "masmio-data-collector",
	  "version" : {
	    "number" : "2.3.0",
	    "build_hash" : "8371be8d5fe5df7fb9c0516c474d77b9feddd888",
	    "build_timestamp" : "2016-03-29T07:54:48Z",
	    "build_snapshot" : false,
	    "lucene_version" : "5.5.0"
	  },
	  "tagline" : "You Know, for Search"
	}
```

References:
===========
* https://www.elastic.co/guide/en/elasticsearch/reference/current/setup-repositories.html
* https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-elasticsearch-on-ubuntu-14-04


Elasticplastic Installation steps:
===================
1. Install Java	(Grumble... OK, I dont personally am too thrilled about having JAVA running on my machine)
	sudo apt-get install openjdk-7-jre
1. Setup the key
	wget -qO - https://packages.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
2. Setup the repository
	echo "deb http://packages.elastic.co/elasticsearch/2.x/debian stable main" | sudo tee -a /etc/apt/sources.list.d/elasticsearch-2.x.list
3. Install Elastic Search:
	sudo apt-get install elasticsearch

Configuration
=============

1. Create a data store location for elastic search: I have a raid on /backup
	mdkir -p /backup/elasticsearch/data  /backup/elasticsearch/logs;sudo chown -R elasticsearch.elasticsearch /backup/elasticsearch/

2. Modify the /etc/elasticsearch/elasticsearch.yml as required. I have a [local][file://elasticsearch.yml] version that is in the git repo for reference.

NOTE: elastic search is meant for pretty much a lot of stuff including multi rack system.
I just have a single machine in my "farm".. that the beaglebone-black throws in data.


Security:
========

I know, I have a local lan, but still, I dont like my kid's data to be compromized. for now
I have constrained which specific machines can access over firewall rules.. but I'd probably want some sort of authentication mechanism to do things here.


Creating basic index
====================

Elastic Search works with "documents" and indices.. which makes it pretty capable..

Create DB:
* ```./create_db index_name host:port```. Example:
	./create_db logmasimo 192.168.0.6:9610
* ```./delete_db index_name host:port```. Example:
	./delete_db logmasimo 192.168.0.6:9610
