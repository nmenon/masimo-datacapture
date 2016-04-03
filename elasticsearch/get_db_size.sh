#!/bin/bash
# Shamelessly copied from:
# https://github.com/yahnatan/pulseox/blob/master/create_index_and_mappings.sh
INDEXNAME=$1
HOSTNAME_AND_PORT=$2

if [ -z $INDEXNAME ]; then
  echo "usage:  create_index_and_mappings.sh <indexname> <host:9200>"
  exit
fi

if [ -z $HOSTNAME_AND_PORT ]; then
  echo "usage:  create_index_and_mappings.sh <indexname> <host:9200>"
  exit
fi

curl "http://$HOSTNAME_AND_PORT/_cat/indices?v"
