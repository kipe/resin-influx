#!/bin/sh

mkdir /data/influxdb
chown influxdb:influxdb /data/influxdb
service influxdb start
python /app/load_logger.py
