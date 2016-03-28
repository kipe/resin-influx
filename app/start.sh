#!/bin/sh

# Make and chown influxdb data directories
mkdir /data/influxdb
chown influxdb:influxdb /data/influxdb

# Run the application with supervisor
supervisord -n -c /etc/supervisor/supervisord.conf
