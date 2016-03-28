#!/bin/env python
import sys
import time
import random
import traceback
from influxdb import InfluxDBClient


def main():
    influx_client = InfluxDBClient('localhost', 8086, username='root', password='root', database='resin-test')
    influx_client.create_database('resin-test')

    while True:
        influx_client.write_points([{
            'measurement': 'test',
            'fields': {
                'value': random.random() * random.random() * 100
            }
        }])
        time.sleep(1)


if __name__ == '__main__':
    while True:
        try:
            main()
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback,
                                      limit=10, file=sys.stdout)
        time.sleep(5)
