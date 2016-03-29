resin-influx
============

A basic example of running [InfluxDB](https://influxdata.com/time-series-platform/influxdb/) via [resin.io](https://resin.io).

Logs various data (load averages, memory usage, `/data` partition usage) via Python -script to the database.
This database can then be queried via the built-in webinterface, at `http://<resin-ip>:8083`


#### Performance
This example was mainly done as a test of InfluxDB performance on RPi, so here:

Raspberry Pi B+:
  - writing a single measurement (9 values): ~20 milliseconds
  - querying ~1800 points (10 minutes) and taking 1 minute averages: ~30 milliseconds

    `SELECT MEAN(value) FROM load_avg WHERE time > '2016-03-28' GROUP BY time(1m), avg_time`
