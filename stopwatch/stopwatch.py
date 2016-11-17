from time import time
import Queue
import threading, logging

"""
watch = StopWatch() # creates new instance and starts watch timer
watch.start()
do_some_stuff()
watch.stop('tag') # records the execution time and prints a log message

---

watch = StopWatch()
...
watch.lap('tag.section.1')
...
watch.lap('tag.section.2')
...
watch.lap('tag.section.3')
...
watch.stop('tag.section.4')
...
watch.start()
..
watch.stop('some other section')

---

watch = StopWatch()
...
watch.stop('tag', probability=0.5)

---

watch = StopWatch()
...
watch.stop('tag', probability=0.5) # Always stops, but logs with probability of 50%

---

watch = StopWatch()
...
watch.stop('tag', threshold=2.0) # Always stops, but logs if time >= 2.0

---


TODO:
- Log with a probability of x
- Only log if time >= x
"""

LOG = logging.getLogger('stopwatch')


class StopWatch(object):

    def __init__(self, logger=None, clock=None):
        self.start_time = None
        self.logger = logger
        if not logger:
            self.logger = PrintTimeLogger()
        self.clock = clock
        if not clock:
            self.clock = time
        self.start()

    def start(self):
        self.start_time = self.clock()

    def stop(self, tag):
        elapsed_time = self.clock() - self.start_time
        self.logger.log(stopwatch_formatter, time_stamp=self.start_time, tag=tag,
                        elapsed_time=elapsed_time, event_count=1)
        return elapsed_time

    def lap(self, tag):
        elapsed_time = self.stop(tag)
        self.start()
        return elapsed_time


class Counter(object):
    def __init__(self, logger=None, clock=None):
        self.logger = logger
        if not logger:
            self.logger = PrintMetricLogger()
        self.clock = clock
        if not clock:
            self.clock = time

    def count(self, tag, event_count=1):
        self.logger.log(counter_formatter, time_stamp=self.clock(), tag=tag, event_count=event_count)


class LogFormatter(object):
    TOKEN_SEPARATOR = '|'
    START_TOKEN = '<' + TOKEN_SEPARATOR
    END_TOKEN = TOKEN_SEPARATOR + '>'

    def format(self, **kwargs):
        return self.FORMAT.format(kwargs)


class StopwatchFormatter(LogFormatter):
    FORMAT = LogFormatter.TOKEN_SEPARATOR.join([LogFormatter.START_TOKEN + '{time_stamp}',
                                                '{tag}',
                                                '{elapsed_time:f}',
                                                '{event_count}',
                                                't' + LogFormatter.END_TOKEN])


class CounterFormatter(LogFormatter):
    FORMAT = LogFormatter.TOKEN_SEPARATOR.join([LogFormatter.START_TOKEN + '{time_stamp}',
                                                '{tag}',
                                                '{event_count}',
                                                'c' + LogFormatter.END_TOKEN])

stopwatch_formatter = StopwatchFormatter()
counter_formatter = CounterFormatter()


class MetricLogger(object):
    def log(self, formatter, **kwargs):
        raise NotImplementedError()


class PrintMetricLogger(MetricLogger):

    def __init__(self):
        pass

    def log(self, formatter, **kwargs):
        print formatter.format(kwargs)


class LoggingMetricLogger(MetricLogger):

    def __init__(self, logger):
        self.logger = logger

    def log(self, formatter, **kwargs):
        if self.logger.isEnabledFor(logging.INFO):
            self.logger.info(formatter.format(kwargs))

