resin-influx
============

A basic example of running [influxdb](https://influxdata.com/time-series-platform/influxdb/) via [resin.io](https://resin.io).

All it does, is write load averages via Python -script to the database.
This database can then be queried via the built-in webinterface, at `http://<resin-ip>:8083`


#### Performance
Initial performance looks to be ok on Raspberry Pi B+:
  - writing a single measurement (3 values): ~20 milliseconds
  - querying ~1800 points (10 minutes) and taking 1 minute averages: ~30 milliseconds

    `SELECT MEAN(value) FROM load_avg WHERE time > '2016-03-28' GROUP BY time(1m), avg_time`
