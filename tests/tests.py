import unittest

from context import Timer, Counter, MockClock, MockMetricLogger, MockRand, InMemoryLogger


class TimerTest(unittest.TestCase):
    def setUp(self):
        self.clock = MockClock(0)
        self.logger = MockMetricLogger()
        self.timer = Timer(self.logger, self.clock)

    def test_should_start_on_init(self):
        self.clock.tick()

        self.assertEqual(self.timer.stop('test'), 1)

    def test_start_should_reset_time(self):
        self.clock.tick()
        self.assertEqual(self.timer.stop('test'), 1)

        self.timer.start()

        self.assertEqual(self.timer.stop('test'), 0)

    def test_stop_should_log(self):
        self.clock.tick()
        self.timer.stop('test')

        self.assertEqual(self.logger.log_count(), 1)

    def test_stop_should_log_elapsed_time(self):
        self.clock.set(5)
        self.timer.stop('test')

        event = self.logger.logged_events[0]
        self.assertEqual(event['elapsed_time'], 5)

    def test_stop_should_log_one_event(self):
        self.timer.stop('test')

        event = self.logger.logged_events[0]
        self.assertEqual(event['event_count'], 1)

    def test_stop_should_log_with_tag(self):
        self.timer.stop('test')

        event = self.logger.logged_events[0]
        self.assertEqual(event['tag'], 'test')

    def test_stop_should_log_with_time_stamp(self):
        self.clock.set(5)
        timer = Timer(self.logger, self.clock)

        self.clock.tick()
        timer.stop('test')

        event = self.logger.logged_events[0]
        self.assertEqual(event['time_stamp'], 5)

    def test_lap_should_return_elapsed_time(self):
        self.clock.tick()
        self.assertEqual(self.timer.lap('test'), 1)

    def test_lap_should_log(self):
        self.clock.tick()
        self.timer.lap('test')

        self.assertEqual(self.logger.log_count(), 1)

    def test_lap_should_reset(self):
        self.clock.tick()
        self.assertEqual(self.timer.lap('test'), 1)

        self.clock.tick()
        self.clock.tick()

        self.assertEqual(self.timer.stop('test'), 2)

    def test_negative_sample_rate_should_not_log(self):
        self.timer.rand = MockRand(0.5)
        self.timer.stop('test', sample_rate=-1)

        self.assertEqual(self.logger.log_count(), 0)

    def test_zero_sample_rate_should_not_log(self):
        self.timer.rand = MockRand(0.5)
        self.timer.stop('test', sample_rate=0)

        self.assertEqual(self.logger.log_count(), 0)

    def test_should_log_if_elapsed_time_is_greater_than_threshold(self):
        self.clock.set(6)
        self.timer.stop('test', threshold=5)

        self.assertEqual(self.logger.log_count(), 1)

    def test_should_log_if_elapsed_time_is_equal_to_threshold(self):
        self.clock.set(5)
        self.timer.stop('test', threshold=5)

        self.assertEqual(self.logger.log_count(), 1)

    def test_should_not_log_if_elapsed_time_is_less_than_threshold(self):
        self.clock.set(4)
        self.timer.stop('test', threshold=5)

        self.assertEqual(self.logger.log_count(), 0)

    def test_lap_should_log_if_elapsed_time_is_greater_than_threshold(self):
        self.clock.set(6)
        self.timer.lap('test', threshold=5)

        self.assertEqual(self.logger.log_count(), 1)

    def test_lap_should_log_if_elapsed_time_is_equal_to_threshold(self):
        self.clock.set(5)
        self.timer.lap('test', threshold=5)

        self.assertEqual(self.logger.log_count(), 1)

    def test_lap_should_not_log_if_elapsed_time_is_less_than_threshold(self):
        self.clock.set(4)
        self.timer.lap('test', threshold=5)

        self.assertEqual(self.logger.log_count(), 0)

    def test_should_log_if_rand_less_than_sample_rate(self):
        self.timer.rand = MockRand(0.5)
        self.timer.stop('test', sample_rate=0.6)

        self.assertEqual(self.logger.log_count(), 1)

    def test_should_log_if_rand_equal_to_sample_rate(self):
        self.timer.rand = MockRand(0.5)
        self.timer.stop('test', sample_rate=0.5)

        self.assertEqual(self.logger.log_count(), 1)

    def test_should_not_log_if_rand_greater_than_sample_rate(self):
        self.timer.rand = MockRand(0.5)
        self.timer.stop('test', sample_rate=0.4)

        self.assertEqual(self.logger.log_count(), 0)

    def test_lap_should_log_if_rand_less_than_sample_rate(self):
        self.timer.rand = MockRand(0.5)
        self.timer.lap('test', sample_rate=0.6)

        self.assertEqual(self.logger.log_count(), 1)

    def test_lap_should_log_if_rand_equal_to_sample_rate(self):
        self.timer.rand = MockRand(0.5)
        self.timer.lap('test', sample_rate=0.5)

        self.assertEqual(self.logger.log_count(), 1)

    def test_lap_should_not_log_if_rand_greater_than_sample_rate(self):
        self.timer.rand = MockRand(0.5)
        self.timer.lap('test', sample_rate=0.4)

        self.assertEqual(self.logger.log_count(), 0)

    def test_logged_events_should_divide_by_sample_rate_1(self):
        self.timer.rand = MockRand(0.4)
        self.timer.stop('test', sample_rate=0.5)

        self.assertEqual(self.logger.logged_events[0]['event_count'], 2)

    def test_logged_events_should_divide_by_sample_rate_2(self):
        self.timer.rand = MockRand(0.05)
        self.timer.stop('test', sample_rate=0.1)

        self.assertEqual(self.logger.logged_events[0]['event_count'], 10)

    def test_logged_events_should_round_to_nearest_integer_1(self):
        self.timer.rand = MockRand(0.1)
        self.timer.stop('test', sample_rate=0.3)

        self.assertEqual(self.logger.logged_events[0]['event_count'], 3)

    def test_logged_events_should_round_to_nearest_integer_2(self):
        self.timer.rand = MockRand(0.1)
        self.timer.stop('test', sample_rate=0.66)

        self.assertEqual(self.logger.logged_events[0]['event_count'], 2)

    def test_timer_format(self):
        logger = InMemoryLogger()
        self.timer.logger = logger
        self.clock.tick()
        self.timer.stop('test.tag')

        log_line = logger.logged_events[0]
        self.assertEqual(log_line, '<|0|test.tag|1.000000|1|t|>')


class CounterTest(unittest.TestCase):
    def setUp(self):
        self.logger = MockMetricLogger()
        self.clock = MockClock(0)
        self.counter = Counter(self.logger, self.clock)

    def test_incr_should_log(self):
        self.counter.incr('test')

        self.assertEqual(self.logger.log_count(), 1)

        self.counter.incr('test')

        self.assertEqual(self.logger.log_count(), 2)

    def test_incr_should_log_one_by_default(self):
        self.counter.incr('test')

        self.assertEqual(self.logger.logged_events[0]['event_count'], 1)

    def test_incr_should_log_tag(self):
        self.counter.incr('test.tag')

        self.assertEqual(self.logger.logged_events[0]['tag'], 'test.tag')

    def test_event_count_should_have_specified_value(self):
        self.counter.incr('test', 7)

        self.assertEqual(self.logger.logged_events[0]['event_count'], 7)

    def test_counter_format(self):
        logger = InMemoryLogger()
        self.counter.logger = logger
        self.clock.set(15)

        self.counter.incr('test', 7)

        log_line = logger.logged_events[0]
        self.assertEqual(log_line, '<|15|test|7|c|>')

    def test_negative_sample_rate_should_not_log(self):
        self.counter.rand = MockRand(0.5)
        self.counter.incr('test', sample_rate=-1)

        self.assertEqual(self.logger.log_count(), 0)

    def test_zero_sample_rate_should_not_log(self):
        self.counter.rand = MockRand(0.5)
        self.counter.incr('test', sample_rate=0)

        self.assertEqual(self.logger.log_count(), 0)

    def test_should_log_if_rand_less_than_sample_rate(self):
        self.counter.rand = MockRand(0.5)
        self.counter.incr('test', sample_rate=0.6)

        self.assertEqual(self.logger.log_count(), 1)

    def test_should_log_if_rand_equal_to_sample_rate(self):
        self.counter.rand = MockRand(0.5)
        self.counter.incr('test', sample_rate=0.5)

        self.assertEqual(self.logger.log_count(), 1)

    def test_should_not_log_if_rand_greater_than_sample_rate(self):
        self.counter.rand = MockRand(0.5)
        self.counter.incr('test', sample_rate=0.4)

        self.assertEqual(self.logger.log_count(), 0)

    def test_logged_events_should_divide_by_sample_rate_1(self):
        self.counter.rand = MockRand(0.4)
        self.counter.incr('test', sample_rate=0.5)

        self.assertEqual(self.logger.logged_events[0]['event_count'], 2)

    def test_logged_events_should_divide_by_sample_rate_2(self):
        self.counter.rand = MockRand(0.05)
        self.counter.incr('test', sample_rate=0.1)

        self.assertEqual(self.logger.logged_events[0]['event_count'], 10)

    def test_logged_events_should_divide_by_sample_rate_3(self):
        self.counter.rand = MockRand(0.05)
        self.counter.incr('test', count=2, sample_rate=0.1)

        self.assertEqual(self.logger.logged_events[0]['event_count'], 20)

    def test_logged_events_should_round_to_nearest_integer_1(self):
        self.counter.rand = MockRand(0.1)
        self.counter.incr('test', sample_rate=0.3)

        self.assertEqual(self.logger.logged_events[0]['event_count'], 3)

    def test_logged_events_should_round_to_nearest_integer_2(self):
        self.counter.rand = MockRand(0.1)
        self.counter.incr('test', sample_rate=0.66)

        self.assertEqual(self.logger.logged_events[0]['event_count'], 2)

if __name__ == '__main__':
    suite = unittest.TestSuite()
    for test_class in [TimerTest, CounterTest]:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    unittest.TextTestRunner(verbosity=2).run(suite)
