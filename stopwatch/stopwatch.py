from time import time
import random, logging

LOG = logging.getLogger('stopwatch')


class Timer(object):

    def __init__(self, logger=None, clock=None):
        self.start_time = None
        self.logger = logger
        if not logger:
            self.logger = PrintMetricLogger()
        self.clock = clock
        if not clock:
            self.clock = time
        self.rand = random.random
        self.start()

    def start(self):
        self.start_time = self.clock()

    def stop(self, tag, sample_rate=1, threshold=0):
        elapsed_time = self.clock() - self.start_time

        if sample_rate <= 0 or sample_rate < self.rand() or elapsed_time < threshold:
            return elapsed_time

        event_count = int(round(1 / sample_rate))
        self.logger.log(timer_formatter, time_stamp=self.start_time, tag=tag,
                        elapsed_time=elapsed_time, event_count=event_count)
        return elapsed_time

    def lap(self, tag, sample_rate=1, threshold=0):
        elapsed_time = self.stop(tag, sample_rate, threshold)
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
        self.rand = random.random

    def incr(self, tag, count=1, sample_rate=1):
        if sample_rate > 0 and sample_rate >= self.rand():
            event_count = int(round(count / sample_rate))
            self.logger.log(counter_formatter, time_stamp=self.clock(), tag=tag, event_count=event_count)


class LogFormatter(object):
    TOKEN_SEPARATOR = '|'
    START_TOKEN = '<' + TOKEN_SEPARATOR
    END_TOKEN = TOKEN_SEPARATOR + '>'

    def format(self, **kwargs):
        return self.FORMAT.format(**kwargs)


class TimerFormatter(LogFormatter):
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

timer_formatter = TimerFormatter()
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
            self.logger.info(formatter.format(**kwargs))

