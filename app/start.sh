#!/bin/sh

# Make and chown influxdb data directories
mkdir /data/influxdb
chown influxdb:influxdb /data/influxdb

# Run the application with supervisor
supervisord -n -c /usr/local/etc/supervisord.conf
