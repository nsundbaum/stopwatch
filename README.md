# Stopwatch
Stopwatch is a StatsD-like library for logging and aggregating metrics implemented in Python. However, instead of sending metrics across the network to a
central server, it simply logs each metric locally to file, one line per logged metric event. This file can then be
parsed to get an aggregated report of logged metrics.

Stopwatch is intended to be used in scenarios where a full-blown StatsD (or similar) stack
would be overkill, for example when the amount of web servers is small.

Stopwatch comes with two parts. One API for logging metrics to file and one parser to parse such files in
order to display aggregate metrics.

## Basic usage
First, log some metrics:
```python
timer = Timer() # Starts the timer
...
timer.stop('foo') # Logs time since this instance was created under the key foo

counter = Counter()
...
counter.incr('bar') # Will log 1 event under the key bar
counter.incr('bar', count=5) # Will log 5 events under the key bar
```

Then, use `logparser.py` to get an aggregated view of the logged metrics:

```
$ python stopwatch/logparser.py my-metrics.log

Tag        Type          Count         Total(s)         Avg(s)
foo        time          7             20.902           2.986
bar        count         34            -                -

```

## Advanced usage
### Configure a logger
By default, Stopwatch logs to standard out but regular Python loggers are also supported.

To configure file-based logging using a Python logger:
```python
import logging

# Configure Python logging
logger = logging.getLogger('metrics')
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('my-metrics.log')
formatter = logging.Formatter('%(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Create a Stopwatch logger
stopwatch_logger = LoggingMetricLogger(logger)

# Pass the Stopwatch logger as part of Timer and/or Counter instantiation
# This will send metrics to my-metrics.log
timer = Timer(stopwatch_logger)
...
timer.stop('foo')

counter = Counter(stopwatch_logger)
...
counter.incr('bar')
```

### Using sample rates
To limit logging in high throughput scenarios, sample rates can be specified for timers and counters. A sample rate of
for example 0.1 means that events will be logged with a probability of 0.1. In the aggregated metrics,
sample rates will be used to project the actual metrics as if all events were logged.

```python
timer = Timer()
...
timer.stop('foo', sample_rate=0.1) # Logs with probability of 0.1

counter = Counter()
...
counter.incr('bar', sample_rate=0.5) # Logs with probability of 0.5
```

### Using thresholds
Use the optional threshold parameter to limit timer logging to events with an elapsed time greater than or equal to the
 specified threshold.

```python
timer = Timer()
...
timer.stop('foo', threshold=2.0) # Only logs events with a duration of >= 2.0 seconds
```

### Reset the timer
The timer instance can be reset using the `lap` method.
```python
timer = Timer()
for foo in foos:
    do_something()
    timer.lap('foo') # Logs duration and resets the timer
```

### Group report in time intervals
To get a more fine-grained aggregate report, the `logparser` can be invoked with an `--aggregate` parameter
to specify the time interval (in seconds, minutes or hours) for the report.

For example, to break down the report into 10 minute intervals:
```
$ python stopwatch/logparser.py my-metrics.log --aggregate 10m

Sep-09: 21:20:32 - 21:30:32
Tag        Type          Count         Total(s)         Avg(s)
foo        time          7             20.902           2.986
bar        count         34            -                -

Sep-09: 21:30:32 - 21:40:32
Tag        Type          Count         Total(s)         Avg(s)
foo        time          5             15.902           3.180
bar        count         27            -                -

Sep-09: 21:40:32 - 21:50:32
Tag        Type          Count         Total(s)         Avg(s)
foo        time          10            29.422           2.942
bar        count         15            -                -
```

## Log parser usage
```
$ python stopwatch/logparser.py -h

usage: logparser.py [-h] [-v] [-s {tag,count,total,avg}] [-r] [-a AGGREGATE]
                    file

Aggregates metrics from Stopwatch formatted file

positional arguments:
  file                  file to parse

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         verbose logging
  -s {tag,count,total,avg}, --sort {tag,count,total,avg}
                        sort order
  -r, --reverse         reverse sort order
  -a AGGREGATE, --aggregate AGGREGATE
                        aggregate stats in specified intervals. Intervals
                        should be specified on the format nx, where n is a
                        positive integer and x is one of 's' (seconds), 'm'
                        (minutes) or 'h' (hours)
```

## TODO
Stopwatch is currently under fairly heavy development, which means that new features, as well as potentially breaking changes, will be introduced continuously.

Features on the near-term roadmap include:
- Provide a context manager for timers.
- Provide decorators for timers and counters.
- Add option to generate report on csv and json format.
- Add more calculated metrics to report, e.g. percentiles and throughput.
- Flask/Django extensions to log response times.
- Add 'gauge' metric type.