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
        self.logger.log(self.start_time, tag, elapsed_time, event_count=1)
        return elapsed_time

    def lap(self, tag):
        elapsed_time = self.stop(tag)
        self.start()
        return elapsed_time


class TimeLogger(object):
    START_TOKEN = '<<<'
    END_TOKEN = '>>>'
    FORMAT = START_TOKEN + ' {time_stamp} {tag} {elapsed_time:f} {event_count} ' + END_TOKEN

    def log(self, time_stamp, tag, elapsed_time, event_count=1):
        raise NotImplementedError()


class PrintTimeLogger(TimeLogger):

    def __init__(self):
        pass

    def log(self, time_stamp, tag, elapsed_time, event_count=1):
        print TimeLogger.FORMAT.format(time_stamp=time_stamp, elapsed_time=elapsed_time, tag=tag, event_count=event_count)


class LoggingTimeLogger(TimeLogger):

    def __init__(self, logger):
        self.logger = logger

    def log(self, time_stamp, tag, elapsed_time, event_count=1):
        if self.logger.isEnabledFor(logging.INFO):
            self.logger.info(TimeLogger.FORMAT.format(time_stamp=time_stamp,
                                                      elapsed_time=elapsed_time,
                                                      tag=tag,
                                                      event_count=event_count))
