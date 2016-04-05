#!/bin/bash
# Shamelessly copied from:
# https://github.com/yahnatan/pulseox/blob/master/create_index_and_mappings.sh
INDEXNAME=$1
HOSTNAME_AND_PORT=$2

if [ -z $INDEXNAME ]; then
  echo "usage:  $0 <indexname> <host:9200>"
  exit
fi

if [ -z $HOSTNAME_AND_PORT ]; then
  echo "usage:  $0 <indexname> <host:9200>"
  exit
fi

curl -XGET "http://$HOSTNAME_AND_PORT/$INDEXNAME/"'data/_mapping?pretty'

echo
