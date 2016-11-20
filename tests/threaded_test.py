import logging
from context import Timer, Counter, LoggingMetricLogger

# Configure Python logging
logger = logging.getLogger('metrics')
file_handler = logging.FileHandler('my-metrics.log')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Create a Stopwatch logger
stopwatch_logger = LoggingMetricLogger(logger)

# Pass the Stopwatch logger as part of Timer and/or Counter instantiation
timer = Timer(stopwatch_logger)

timer.stop('foo')

counter = Counter(stopwatch_logger)

counter.incr('bar')
counter.incr('bar', count=4)