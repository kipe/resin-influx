#!/bin/env python
import os
import time
from influxdb import InfluxDBClient


# Initialize connection to the database
influx_client = InfluxDBClient('localhost', 8086, database='resin-test')
# Create database (might already exist)
influx_client.create_database('resin-test')

while True:
    # Get load averages
    one_minute, five_minute, fifteen_minute = os.getloadavg()
    points = {'1m': one_minute, '5m': five_minute, '15m': fifteen_minute}

    # Write load averages to the database
    influx_client.write_points([
        {
            'measurement': 'load_avg',
            'tags': {
                'avg_time': key,
            },
            'fields': {
                'value': value
            }
        }
        for key, value in points.items()
    ])
    time.sleep(1)
