from time import time
import Queue
import threading, logging

"""
watch = StopWatch('basic_timer')
watch.start()
do_stuff()
watch.stop() # records the execution time and prints a log message
watch.stop('tag') # records the execution time and prints a log message

TODO:
- Log with a probability of x
- Only log if time > x
- Only log if time < x
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
