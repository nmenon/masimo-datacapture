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

curl -XPUT "http://$HOSTNAME_AND_PORT/$INDEXNAME" -d '
{
    "mappings" : {
      "data" : {
        "date_detection" : false,
        "properties" : {
          "alarm" : {
            "type" : "long"
          },
          "bpm" : {
            "type" : "short"
          },
          "exc" : {
            "type" : "long"
          },
          "exc1" : {
            "type" : "long"
          },
          "exc_ambient_light" : {
            "type" : "boolean"
          },
          "exc_interference" : {
            "type" : "boolean"
          },
          "exc_low_perfusion" : {
            "type" : "boolean"
          },
          "exc_low_signal_iq" : {
            "type" : "boolean"
          },
          "exc_masimo_set" : {
            "type" : "boolean"
          },
          "exc_pulse_search" : {
            "type" : "boolean"
          },
          "exc_sensor_defective" : {
            "type" : "boolean"
          },
          "exc_sensor_no" : {
            "type" : "boolean"
          },
          "exc_sensor_off" : {
            "type" : "boolean"
          },
          "exc_sensor_unrecognized" : {
            "type" : "boolean"
          },
          "pi" : {
            "type" : "float"
          },
          "spo2" : {
            "type" : "byte"
          },
          "time" : {
            "type" : "date",
            "format" : "MM-dd-yyyy HH:mm:ss z"
          }
        }
      }
    }
}'

echo
