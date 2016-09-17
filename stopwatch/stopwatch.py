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


class AggregateTimeLogger(TimeLogger):

    def __init__(self, logger, interval=10, clock=None):
        self.logger = logger
        self.interval = interval
        self.queue = Queue.Queue()
        self.aggregate_stats = {}
        self.lock = threading.Lock()

        self.clock = clock
        if not clock:
            self.clock = time

        self.interval_start = self.clock()
        self.interval_end = self.interval_start + interval

        aggregator_thread = threading.Thread(target=self.run, args=())
        aggregator_thread.daemon = True
        aggregator_thread.start()

    def log(self, time_stamp, tag, elapsed_time, event_count=1):
        try:
            self.queue.put([time_stamp, tag, elapsed_time, event_count], block=False)
        except Queue.Full as e:
            LOG.warning("Log event queue full: %s", e.message)

    def run(self):
        while True:
            log_entry = self.queue.get(block=True)
            time_stamp = log_entry[0]
            tag = log_entry[1]
            elapsed_time = log_entry[2]
            event_count = log_entry[3]

            with self.lock: # TODO: Not needed now?
                if time_stamp > self.interval_end:
                    self.flush()
                    self.interval_end += self.interval

                stat = self.aggregate_stats.get(tag, [0, 0.0])
                stat[0] += event_count
                stat[1] += elapsed_time
                self.aggregate_stats[tag] = stat

    def queue_size(self):
        return self.queue.qsize()

    def flush(self):
        self.logger.info('')
        for tag, stat in self.aggregate_stats.iteritems(): # TODO: Sort on tag
            self.logger.info(TimeLogger.FORMAT.format(time_stamp=self.interval_end,
                                                      elapsed_time=stat[1],
                                                      tag=tag,
                                                      event_count=stat[0]))
        self.logger.info('')

        self.aggregate_stats.clear()

    # TODO: Terminate threads?


class StatsdTimeLogger(TimeLogger):
    pass


class CarbonTimeLogger(TimeLogger):
    pass


class OpenTSDBTimeLogger(TimeLogger):
    pass
