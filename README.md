resin-influx
============

A basic example of running [InfluxDB](https://influxdata.com/time-series-platform/influxdb/) via [resin.io](https://resin.io).

Logs various data (load averages, memory usage, `/data` partition usage) via Python -script to the database.
This database can then be queried via the built-in webinterface, at `http://<resin-ip>:8083`


#### Performance
This example was mainly done as a test of InfluxDB performance on RPi, so here:

Raspberry Pi B+:
- writing a single measurement (9 values): ~20-30 milliseconds

- querying ~130 000 load averages (last 12 hours) and calculating 15 minute averages: ~1.2 seconds
    `select mean(value) from load_avg where time > now() - 12h group by avg_time, time(15m)`

- with 1 minute averages: ~2.3 seconds
    `select mean(value) from load_avg where time > now() - 12h group by avg_time, time(1m)`

- with 15 minute averages, last 2 hours: ~0.25 seconds
    `select mean(value) from load_avg where time > now() - 2h group by avg_time, time(15m)`

- with 1 minute averages, last 2 hours: ~0.5 seconds
    `select mean(value) from load_avg where time > now() - 2h group by avg_time, time(1m)`

- querying free memory, load average, and free disk space for the last 2 hours, 15 minute averages: ~0.25
    **Note:** 1 query!
    ```
    select mean(value) / 1024 / 1024 from memory where type = 'available' and time > now() - 2h group by time(5m);
    select mean(value) from load_avg where avg_time = '1m' and time > now() - 2h group by time(5m);
    select mean(value) / 1024 / 1024 from disk_usage where type = 'free' and time > now() - 2h group by time(5m)
    ```

- memory usage: ~53 % -> 255 MB
- ~260 000 points stored in the database, in 9 series
