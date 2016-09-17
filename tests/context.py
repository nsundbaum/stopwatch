import os
import sys
sys.path.insert(0, os.path.abspath('..'))

from stopwatch import StopWatch, AggregateTimeLogger

class MockLogger(object):
    def __init__(self):
        self.logged_events = []

    def log(self, time_stamp, tag, elapsed_time, event_count=1):
        self.logged_events.append({'time_stamp': time_stamp, 'tag': tag, 'elapsed_time': elapsed_time, 'event_count': event_count})

    def log_count(self):
        return len(self.logged_events)


class MockClock(object):
    def __init__(self, current_time=1):
        self.current_time = current_time

    def __call__(self, *args, **kwargs):
        return self.current_time

    def tick(self):
        self.current_time += 1

    def set(self, time):
        self.current_time = time