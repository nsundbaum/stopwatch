import os
import sys
sys.path.insert(0, os.path.abspath('..'))

from stopwatch import MetricLogger, Timer


class MockMetricLogger(MetricLogger):
    def __init__(self):
        self.logged_events = []
        self.formatter = None

    def log(self, formatter, **kwargs):
        self.formatter = formatter
        self.logged_events.append(kwargs)

    def log_count(self):
        return len(self.logged_events)


class InMemoryLogger(MetricLogger):
    def __init__(self):
        self.logged_events = []

    def log(self, formatter, **kwargs):
        self.logged_events.append(formatter.format(**kwargs))


class MockClock(object):
    def __init__(self, current_time=1):
        self.current_time = current_time

    def __call__(self, *args, **kwargs):
        return self.current_time

    def tick(self):
        self.current_time += 1

    def set(self, time):
        self.current_time = time


class MockRand(object):
    def __init__(self, value):
        self.value = value

    def __call__(self, *args, **kwargs):
        return self.value