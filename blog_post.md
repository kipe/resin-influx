# InfluxDB on resin.io #

## What is InfluxDB? ##

In short, [InfluxDB](https://influxdata.com/time-series-platform/influxdb/) is
a time-series database, designed to handle large amounts of numeric data.

What makes InfluxDB special when compared to many other time series databases,
is that it doesn't have any external dependencies. This makes it fairly easy
to deploy as there isn't much to install and setup. Just compile the sources or
use the provided packages.

With version 0.11 InfluxDB started to provide official packages for `armhf`,
which makes it possible to run the database on many embedded linux boards.
This of course makes one wonder if it's possible to run it on Raspberry Pi, and
especially through resin.io...



## Why InfluxDB? ##

The issue with running databases on embedded hardware is most commonly the
performance, especially when handling large amounts of data. In the past I've
used anything from [PostgreSQL](http://www.postgresql.org) to
[CSV](https://en.wikipedia.org/wiki/Comma-separated_values) files to save measurement data.
This is however quite problematic when logging for long periods of time
(most of my systems have been running for months, some for years).
Typically values are logged once per minute from multiple sources.

The main issue is not saving the data but getting the data out in a usable form.
With CSV files I've done various custom solutions, including averaging the data
from one file to a new one, just to get the amount of data to a more reasonable level.

With SQL, the issue typically is that it's fairly slow and averaging the data
to a more reasonable amount is quite difficult. I've even used different tables
for different time ranges, with montly data averaged to one hour et cetera. After
this I've removed the time range from the original data.

My main goal with InfluxDB is to have the database doing the averaging for me,
without the need for removing any of the original data. From my previous experiences
InfluxDB seems to have a very well optimized algorithms and a fairly simple query language.



## Setting up ##

Setting up the Docker image was fairly straight forward, in essence the
Dockerfile is just fetching the ready-made packages for `armhf`, installing, and
configuring them. The only change I made to the configuration was to move all
storage to the `/data` partition, to preserve it between boots.

The project uses the Python-image as a base, as the measurement script is
written in Python. Luckily InfluxDB also has [Python-library](https://github.com/influxdata/influxdb-python)
available, making the logging fairly straightforward. It should however be
noted, that the Python-library doesn't seem to officially support 0.11 yet...

The measurement script reads 9 values from the board. The values are read ~once
per second, and written to the database. The values are
  - load averages: 1, 5 and 15 minutes
  - memory: total, available, and percentage used
  - disk usage for `/data`: total, used, and free

Once both the measurement script and the database are setup, the next thing is
to start them and most important of all, keep them running. At first, the
`systemd` -script included in the InfluxDB package was used, which proved problematic.

The main issue was that the database was moved to `/data`, which of course the
`influxdb` user doesn't have rights to, at least when specifially defining them.
The rights were given in the `start.sh`, but this was run after the database was
started, leading to errors. I couldn't bother messing with it and moved on to
[supervisord](http://supervisord.org) instead, as I've used it in the past with
great success...

After the supervisor -configurations were setup, everything worked flawlessly.
The monitoring script does fail a couple of times before the database has started.
Other than that, everything just worked.



## Performance ##

As noted before, the issue is not saving the data but getting the data out. For
testing this a small Python-script was developed which fetches different amounts
of data, averaging it to different time periods. These tests were run after a
sufficient amount of data was collected, meaning ~3 million measurements.

The tests were run on two different boards, [Raspberry Pi 1 Model B+](https://www.raspberrypi.org/products/model-b-plus/)
and [ODROID-C1](http://www.hardkernel.com/main/products/prdt_info.php?g_code=G141578608433),
as I happened to have them available.

To make the tests fair both hardware used the same memory card with the same
`Dockerfile.template`. The database was backed up before changing the board
and restored once the other board was provisioned. To minimise the random
effects, the tests were run four times on both boards. Both boards also used
the same WiFi -dongle for connectivity, as the test-script was run on my laptop.


The number of points fetched in each test is as follows (double for "multiple" test):

| Range length | Raw    | 1m average | 1h average |
|--------------|--------|------------|------------|
| 2 hours      | ~7200  | 120        | 2          |
| 6 hours      | ~21600 | 360        | 6          |
| 12 hours     | ~43200 | 720        | 12         |
| 24 hours     | ~86400 | 1440       | 24         |

It should be noted, that the database has to handle all the raw points also when
running the averaged tests, as the averages are calculated from the raw points.
Therefore the numbers presented in the table correspond to the number of points
in the result.


The average times (in milliseconds) for fetching load averages from RPi B+:

| Range length | Raw    | 1m average | 1h average |
|--------------|--------|------------|------------|
| 2 hours      | 3676   | 161        | 98         |
| 6 hours      | 9630   | 662        | 175        |
| 12 hours     | 20073  | 679        | 362        |
| 24 hours     | 30674  | 1120       | 1145       |


The average times (in milliseconds) for fetching load averages from ODROID-C1:

| Range length | Raw    | 1m average | 1h average |
|--------------|--------|------------|------------|
| 2 hours      | 843    | 57         | 40         |
| 6 hours      | 1804   | 91         | 48         |
| 12 hours     | 3760   | 239        | 87         |
| 24 hours     | 6025   | 339        | 124        |


Overall the performance is fairly good even on the Raspberry Pi. With ODROID it's
exceptional! The ODROID performs the queries in ~10-30 percent of the time used
by the Raspberry Pi. Furthermore the times are more constant on the ODROID,
which might be because of the multi-core processor. With multiple cores,
different background tasks don't slow down the processing that much, leading
to a more consistent experience.

The results were consistent also on the memory test. However running two
queries with the same request didn't seem consistent for whatever reason.
Sometimes the times were double compared to the results of one query, sometimes
4 times longer et cetera. So if you're looking for consistency, the best bet is
to run the queries one by one, at least for now.

The memory usage of the database daemon seems to stay within a reasonable limits,
leaving enough headroom for the user application. The CPU usage also stays under
control, with the daemon taking ~1-4 percent of a single core when idling.
I didn't check the CPU loads when feching the data, but it's safe to assume that
it's 100 % of at least one core is used...



## Conclusion ##

Overall I'm more than satisfied with the performance. The number of points was
fairly extreme, at least for my usecases. Typically I use a logging interval of
60 - 120 seconds, so the number of points is reduced by quite a lot. If the
performance stays linear, I could fetch hourly averages for a month in under
500 milliseconds even on a first generation Raspberry Pi. This is on par with
my current logging solutions, but a lot easier to manage and to create different
averages for different uses.
