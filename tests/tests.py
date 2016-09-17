import unittest

from context import StopWatch, MockClock, MockLogger


class StopWatchTest(unittest.TestCase):
    def setUp(self):
        self.clock = MockClock(0)
        self.logger = MockLogger()

    def test_should_start_on_init(self):
        stop_watch = StopWatch(self.logger, self.clock)

        self.clock.tick()

        self.assertEqual(stop_watch.stop('test'), 1)

    def test_start_should_reset_time(self):
        stop_watch = StopWatch(self.logger, self.clock)

        self.clock.tick()
        self.assertEqual(stop_watch.stop('test'), 1)

        stop_watch.start()

        self.assertEqual(stop_watch.stop('test'), 0)

    def test_stop_should_log(self):
        stop_watch = StopWatch(self.logger, self.clock)

        self.clock.tick()
        stop_watch.stop('test')

        self.assertEqual(self.logger.log_count(), 1)

    def test_stop_should_log_elapsed_time(self):
        stop_watch = StopWatch(self.logger, self.clock)

        self.clock.set(5)
        stop_watch.stop('test')

        event = self.logger.logged_events[0]
        self.assertEqual(event['elapsed_time'], 5)

    def test_stop_should_log_one_event(self):
        stop_watch = StopWatch(self.logger, self.clock)

        stop_watch.stop('test')

        event = self.logger.logged_events[0]
        self.assertEqual(event['event_count'], 1)

    def test_stop_should_log_with_tag(self):
        stop_watch = StopWatch(self.logger, self.clock)

        stop_watch.stop('test')

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
        stop_watch = StopWatch(self.logger, self.clock)

        self.clock.tick()
        self.assertEqual(stop_watch.lap('test'), 1)

    def test_lap_should_log(self):
        stop_watch = StopWatch(self.logger, self.clock)

        self.clock.tick()
        stop_watch.lap('test')

        self.assertEqual(self.logger.log_count(), 1)

    def test_lap_should_reset(self):
        stop_watch = StopWatch(self.logger, self.clock)

        self.clock.tick()
        self.assertEqual(stop_watch.lap('test'), 1)

        self.clock.tick()
        self.clock.tick()

        self.assertEqual(stop_watch.stop('test'), 2)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(StopWatchTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
