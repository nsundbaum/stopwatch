import unittest

from context import StopWatch, MockClock, MockMetricLogger, MockRand, StopWatchFormatter, InMemoryLogger


class StopWatchTest(unittest.TestCase):
    def setUp(self):
        self.clock = MockClock(0)
        self.logger = MockMetricLogger()
        self.stop_watch = StopWatch(self.logger, self.clock)

    def test_should_start_on_init(self):
        self.clock.tick()

        self.assertEqual(self.stop_watch.stop('test'), 1)

    def test_start_should_reset_time(self):
        self.clock.tick()
        self.assertEqual(self.stop_watch.stop('test'), 1)

        self.stop_watch.start()

        self.assertEqual(self.stop_watch.stop('test'), 0)

    def test_stop_should_log(self):
        self.clock.tick()
        self.stop_watch.stop('test')

        self.assertEqual(self.logger.log_count(), 1)

    def test_stop_should_log_elapsed_time(self):
        self.clock.set(5)
        self.stop_watch.stop('test')

        event = self.logger.logged_events[0]
        self.assertEqual(event['elapsed_time'], 5)

    def test_stop_should_log_one_event(self):
        self.stop_watch.stop('test')

        event = self.logger.logged_events[0]
        self.assertEqual(event['event_count'], 1)

    def test_stop_should_log_with_tag(self):
        self.stop_watch.stop('test')

        event = self.logger.logged_events[0]
        self.assertEqual(event['tag'], 'test')

    def test_stop_should_log_with_time_stamp(self):
        self.clock.set(5)
        stop_watch = StopWatch(self.logger, self.clock)

        self.clock.tick()
        stop_watch.stop('test')

        event = self.logger.logged_events[0]
        self.assertEqual(event['time_stamp'], 5)

    def test_lap_should_return_elapsed_time(self):
        self.clock.tick()
        self.assertEqual(self.stop_watch.lap('test'), 1)

    def test_lap_should_log(self):
        self.clock.tick()
        self.stop_watch.lap('test')

        self.assertEqual(self.logger.log_count(), 1)

    def test_lap_should_reset(self):
        self.clock.tick()
        self.assertEqual(self.stop_watch.lap('test'), 1)

        self.clock.tick()
        self.clock.tick()

        self.assertEqual(self.stop_watch.stop('test'), 2)

    def test_negative_sample_rate_should_never_log(self):
        self.stop_watch.rand = MockRand(0.5)
        self.stop_watch.stop('test', sample_rate=-1)

        self.assertEqual(self.logger.log_count(), 0)

    def test_zero_sample_rate_should_never_log(self):
        self.stop_watch.rand = MockRand(0.5)
        self.stop_watch.stop('test', sample_rate=0)

        self.assertEqual(self.logger.log_count(), 0)

    def test_should_log_if_elapsed_time_is_greater_than_threshold(self):
        self.clock.set(6)
        self.stop_watch.stop('test', threshold=5)

        self.assertEqual(self.logger.log_count(), 1)

    def test_should_log_if_elapsed_time_is_equal_to_threshold(self):
        self.clock.set(5)
        self.stop_watch.stop('test', threshold=5)

        self.assertEqual(self.logger.log_count(), 1)

    def test_should_not_log_if_elapsed_time_is_less_than_threshold(self):
        self.clock.set(4)
        self.stop_watch.stop('test', threshold=5)

        self.assertEqual(self.logger.log_count(), 0)

    def test_lap_should_log_if_elapsed_time_is_greater_than_threshold(self):
        self.clock.set(6)
        self.stop_watch.lap('test', threshold=5)

        self.assertEqual(self.logger.log_count(), 1)

    def test_lap_should_log_if_elapsed_time_is_equal_to_threshold(self):
        self.clock.set(5)
        self.stop_watch.lap('test', threshold=5)

        self.assertEqual(self.logger.log_count(), 1)

    def test_lap_should_not_log_if_elapsed_time_is_less_than_threshold(self):
        self.clock.set(4)
        self.stop_watch.lap('test', threshold=5)

        self.assertEqual(self.logger.log_count(), 0)

    def test_should_log_if_rand_less_than_sample_rate(self):
        self.stop_watch.rand = MockRand(0.5)
        self.stop_watch.stop('test', sample_rate=0.6)

        self.assertEqual(self.logger.log_count(), 1)

    def test_should_log_if_rand_equal_to_sample_rate(self):
        self.stop_watch.rand = MockRand(0.5)
        self.stop_watch.stop('test', sample_rate=0.5)

        self.assertEqual(self.logger.log_count(), 1)

    def test_should_not_log_if_rand_greater_than_sample_rate(self):
        self.stop_watch.rand = MockRand(0.5)
        self.stop_watch.stop('test', sample_rate=0.4)

        self.assertEqual(self.logger.log_count(), 0)

    def test_lap_should_log_if_rand_less_than_sample_rate(self):
        self.stop_watch.rand = MockRand(0.5)
        self.stop_watch.lap('test', sample_rate=0.6)

        self.assertEqual(self.logger.log_count(), 1)

    def test_lap_should_log_if_rand_equal_to_sample_rate(self):
        self.stop_watch.rand = MockRand(0.5)
        self.stop_watch.lap('test', sample_rate=0.5)

        self.assertEqual(self.logger.log_count(), 1)

    def test_lap_should_not_log_if_rand_greater_than_sample_rate(self):
        self.stop_watch.rand = MockRand(0.5)
        self.stop_watch.lap('test', sample_rate=0.4)

        self.assertEqual(self.logger.log_count(), 0)

    def test_logged_events_should_divide_by_sample_rate_1(self):
        self.stop_watch.rand = MockRand(0.4)
        self.stop_watch.stop('test', sample_rate=0.5)

        self.assertEqual(self.logger.logged_events[0]['event_count'], 2)

    def test_logged_events_should_divide_by_sample_rate_2(self):
        self.stop_watch.rand = MockRand(0.05)
        self.stop_watch.stop('test', sample_rate=0.1)

        self.assertEqual(self.logger.logged_events[0]['event_count'], 10)

    def test_logged_events_should_round_to_nearest_integer_1(self):
        self.stop_watch.rand = MockRand(0.1)
        self.stop_watch.stop('test', sample_rate=0.3)

        self.assertEqual(self.logger.logged_events[0]['event_count'], 3)

    def test_logged_events_should_round_to_nearest_integer_2(self):
        self.stop_watch.rand = MockRand(0.1)
        self.stop_watch.stop('test', sample_rate=0.66)

        self.assertEqual(self.logger.logged_events[0]['event_count'], 2)

    def test_stop_watch_format(self):
        logger = InMemoryLogger()
        self.stop_watch.logger = logger
        self.clock.tick()
        self.stop_watch.stop('test.tag')

        log_line = logger.logged_events[0]
        self.assertEqual(log_line, '<|0|test.tag|1.000000|1|t|>')


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(StopWatchTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
