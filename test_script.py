#!/bin/env python
import os
import time
from influxdb import InfluxDBClient

influx_client = InfluxDBClient(os.environ['RESIN_HOST'], 8086, database='resin-test')


def _timed_query(q):
    '''
    Runs the query on InfluxDB.
    Returns time in milliseconds and the results.
    '''
    start = time.time()
    result = influx_client.query(q)
    return (time.time() - start) * 1000, result


def test_load_avg(duration):
    '''
    Tests fetching 1 minute load averages for the duration.
    - without any averaging (returns ~3600 points per hour)
    - with 1 minute averaging (60 points)
    - with 1 hour averaging (1 point)
    '''
    raw = _timed_query("SELECT value FROM load_avg WHERE avg_time = '1m' AND time > now() - %ih AND time < now() - %ih" % (duration * 2, duration))[0]
    avg_1m = _timed_query("SELECT mean(value) FROM load_avg WHERE avg_time = '1m' AND time > now() - %ih AND time < now() - %ih GROUP BY time(1m)" % (duration * 2, duration))[0]
    avg_1h = _timed_query("SELECT mean(value) FROM load_avg WHERE avg_time = '1m' AND time > now() - %ih AND time < now() - %ih GROUP BY time(1h)" % (duration * 2, duration))[0]

    print('Load average (%ih): %.2fms (raw, ~%i points), %.2fms (1m avg, %i points), %.2fms (1h avg, %i points)' % (duration, raw, duration * 3600, avg_1m, duration * 60, avg_1h, duration))
    return [raw, avg_1m, avg_1h]


def test_memory(duration):
    '''
    Tests fetching amount of free memory for the last duration.
    - without any averaging (returns ~3600 points per hour)
    - with 1 minute averaging (60 points)
    - with 1 hour averaging (1 point)
    '''
    raw = _timed_query("SELECT value FROM memory WHERE type = 'available' AND time > now() - %ih AND time < now() - %ih" % (duration * 2, duration))[0]
    avg_1m = _timed_query("SELECT mean(value) FROM memory WHERE type = 'available' AND time > now() - %ih AND time < now() - %ih GROUP BY time(1m)" % (duration * 2, duration))[0]
    avg_1h = _timed_query("SELECT mean(value) FROM memory WHERE type = 'available' AND time > now() - %ih AND time < now() - %ih GROUP BY time(1h)" % (duration * 2, duration))[0]

    print('Memory (%ih): %.2fms (raw, ~%i points), %.2fms (1m avg, %i points), %.2fms (1h avg, %i points)' % (duration, raw, duration * 3600, avg_1m, duration * 60, avg_1h, duration))
    return [raw, avg_1m, avg_1h]


def test_multiple(duration):
    '''
    Tests running both query types at once.
    - without any averaging (returns ~7200 points per hour)
    - with 1 minute averaging (120 points)
    - with 1 hour averaging (2 points)
    '''
    raw = _timed_query("SELECT value FROM load_avg WHERE avg_time = '1m' AND time > now() - %ih AND time < now() - %ih; SELECT value FROM memory WHERE type = 'available' AND time > now() - %ih AND time < now() - %ih" % (duration * 2, duration, duration * 2, duration))[0]
    avg_1m = _timed_query("SELECT mean(value) FROM load_avg WHERE avg_time = '1m' AND time > now() - %ih AND time < now() - %ih GROUP BY time(1m); SELECT mean(value) FROM memory WHERE type = 'available' AND time > now() - %ih AND time < now() - %ih GROUP BY time(1m)" % (duration * 2, duration, duration * 2, duration))[0]
    avg_1h = _timed_query("SELECT mean(value) FROM load_avg WHERE avg_time = '1m' AND time > now() - %ih AND time < now() - %ih GROUP BY time(1h); SELECT mean(value) FROM memory WHERE type = 'available' AND time > now() - %ih AND time < now() - %ih GROUP BY time(1h)" % (duration * 2, duration, duration * 2, duration))[0]

    print('Multiple (%ih): %.2fms (raw, ~%i points), %.2fms (1m avg, %i points), %.2fms (1h avg, %i points)' % (duration, raw, duration * 3600, avg_1m, duration * 60, avg_1h, duration))
    return [raw, avg_1m, avg_1h]


def save_results(filename, timestamp, duration, results):
    with open('test_results/%s.csv' % filename, 'a') as f:
        results.insert(0, duration)
        results.insert(0, timestamp)
        f.write('\t'.join(['%s' % x for x in results]))
        f.write('\n')


if __name__ == '__main__':
    from datetime import datetime
    timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M')
    durations = [2, 6, 12, 24]
    board_under_test = 'odroid_c1'

    for d in durations:
        save_results('%s_load_avg' % board_under_test, timestamp, d, test_load_avg(d))

    for d in durations:
        save_results('%s_memory' % board_under_test, timestamp, d, test_memory(d))

    for d in durations:
        save_results('%s_multiple' % board_under_test, timestamp, d, test_multiple(d))
