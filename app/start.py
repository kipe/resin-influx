#!/bin/env python
import os
import sys
import time
import traceback
from influxdb import InfluxDBClient


def main():
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


# Main loop, printing exceptions but keeping the system running
if __name__ == '__main__':
    while True:
        try:
            main()
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback,
                                      limit=10, file=sys.stdout)
        time.sleep(5)
