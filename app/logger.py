#!/bin/env python
import os
import time
import psutil
from influxdb import InfluxDBClient


# Initialize connection to the database
influx_client = InfluxDBClient('localhost', 8086, database='resin-test')
# Create database (might already exist)
influx_client.create_database('resin-test')

while True:
    # Get load averages
    one_minute, five_minute, fifteen_minute = os.getloadavg()
    points = {'1m': one_minute, '5m': five_minute, '15m': fifteen_minute}
    # Create array of measurement points
    measurements = [
        {
            'measurement': 'load_avg',
            'tags': {
                'avg_time': key,
            },
            'fields': {
                'value': float(value)
            }
        }
        for key, value in points.items()
    ]

    # Get memory information
    memory = psutil.virtual_memory()
    points = {
        'total': memory.total,
        'available': memory.available,
        'percent_used': memory.percent,
    }
    # Extend the measurements array with memory information
    measurements.extend([
        {
            'measurement': 'memory',
            'tags': {
                'type': key,
            },
            'fields': {
                'value': float(value)
            }
        }
        for key, value in points.items()
    ])

    # Get /data partition information
    disk_usage = psutil.disk_usage('/data')
    points = {
        'total': disk_usage.total,
        'used': disk_usage.used,
        'free': disk_usage.free,
    }
    # Extend the measurements array with memory information
    measurements.extend([
        {
            'measurement': 'disk_usage',
            'tags': {
                'type': key,
            },
            'fields': {
                'value': float(value)
            }
        }
        for key, value in points.items()
    ])

    # Write load averages to the database
    influx_client.write_points(measurements)
    time.sleep(1)
