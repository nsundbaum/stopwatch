"""

    metrics: median, 80, 90, 95, 99

    --output (pretty, csv, json)

    -a --aggregate 5s 10m 1h 1d


"""
import sys, argparse
from datetime import datetime
from stopwatch import LogFormatter


class LogParser(object):

    TEN_YEARS_IN_SECONDS = 10 * 365 * 24 * 60 * 60

    sort = {
        'tag': lambda stat: stat.tag,
        'count': lambda stat: stat.event_count,
        'total': lambda stat: stat.total_time if hasattr(stat, 'total_time') else 0,
        'avg': lambda stat: stat.average if hasattr(stat, 'average') else 0
    }

    def __init__(self, in_file, verbose=True, sort_by='tag', reverse=False, interval=TEN_YEARS_IN_SECONDS):
        self.in_file = in_file
        self.verbose = verbose
        self.sort_by = sort_by
        self.reverse = reverse
        self.interval = interval
        if not self.interval:
            self.interval = self.TEN_YEARS_IN_SECONDS

    def parse(self):
        with open(self.in_file) as file:
            return self._parse_lines(file)

    def print_stats(self, aggregate_stats):
        output = PrintOutput(aggregate_stats)

        for bucket in aggregate_stats.buckets:
            output.bucket_header(bucket)
            for stat in sorted(bucket.stats.values(), key=self.sort[self.sort_by], reverse=self.reverse):
                stat.visit(output)
            output.bucket_footer(bucket)

    def _parse_lines(self, log_file):
        aggregate_stats = AggregateStats(self.interval)
        line_count = 1
        for line in log_file:
            try:
                self._parse_line(line, aggregate_stats)
            except:
                if self.verbose:
                    e = sys.exc_info()[0]
                    sys.stderr.write('Error reading line {} {}: {}'.format(line_count, line, e))
            finally:
                line_count += 1

        return aggregate_stats

    def _parse_line(self, line, aggregate_stats):
        line = line.strip()
        if not self.is_stopwatch_line(line):
            return

        aggregate_stats.parse_line(line)

    @staticmethod
    def is_stopwatch_line(line):
        return line and line.startswith(LogFormatter.START_TOKEN) and line.endswith(LogFormatter.END_TOKEN)


class Output(object):
    def bucket_header(self, bucket):
        pass

    def bucket_footer(self, bucket):
        pass

    def counter_stats(self, counter_stats):
        pass

    def timer_stats(self, timer_stats):
        pass


class PrintOutput(Output):
    def __init__(self, aggregate_stats):
        self.tag_col_width = aggregate_stats.max_tag_len() + 4
        self.include_time = len(aggregate_stats.buckets) > 1

    def bucket_header(self, bucket):
        print ''
        self._print_time(bucket)
        tag_justified = 'Tag'.ljust(self.tag_col_width)
        self._print_line(tag_justified, 'Type', 'Count', 'Total', 'Avg')

    def _print_time(self, bucket):
        if not self.include_time:
            return

        start = datetime.fromtimestamp(bucket.start_time)
        end = datetime.fromtimestamp(bucket.end_time)
        time_format = '%H:%M:%S'
        print start.strftime('%b-%m') + ': ' + start.strftime(time_format) + ' - ' + end.strftime(time_format)

    def counter_stats(self, counter_stats):
        self._print_line(counter_stats.tag, 'count', str(counter_stats.event_count), '-', '-')

    def timer_stats(self, timer_stats):
        self._print_line(timer_stats.tag, 'time', str(timer_stats.event_count),
                         '{:.3f}'.format(timer_stats.total_time),
                         '{:.3f}'.format(timer_stats.average))

    def _print_line(self, tag, type, event_count, total_time, average):
        tag_justified = tag.ljust(self.tag_col_width)
        print "{}{:<10}    {:<10}    {:<10}    {:<10}".format(tag_justified, type, event_count, total_time, average)

    def bucket_footer(self, bucket):
        print ''


class TimerStats(object):
    def __init__(self, type, tag):
        self.type = type
        self.tag = tag
        self.event_count = 0
        self.total_time = 0.0
        self.average = 0.0
        # Add rate, e.g. event_count per second

    def add(self, tokens):
        elapsed_time = float(tokens[0])
        event_count = int(tokens[1])

        self.event_count += event_count
        self.total_time += elapsed_time
        self.average = self.total_time / self.event_count

    def visit(self, visitor):
        visitor.timer_stats(self)


class CounterStats(object):
    def __init__(self, type, tag):
        self.type = type
        self.tag = tag
        self.event_count = 0
        # Add rate, e.g. event_count per second

    def add(self, tokens):
        event_count = int(tokens[0])
        self.event_count += event_count

    def visit(self, visitor):
        visitor.counter_stats(self)


class AggregateStats(object):
    def __init__(self, interval):
        self.interval = interval
        self.buckets = []

    def max_tag_len(self):
        max_tag_len = 0
        for bucket in self.buckets:
            max_tag_len = max(max_tag_len, *(len(tag) for tag in bucket.stats.keys()))
        return max_tag_len

    def parse_line(self, line):
        tokens = line.split(LogFormatter.TOKEN_SEPARATOR)
        type = tokens[-2]
        time_stamp = float(tokens[1])
        tag = tokens[2]

        if not self.buckets:
            self._new_bucket(time_stamp)

        current_bucket = self.buckets[-1]
        if not current_bucket.in_bucket(time_stamp):
            current_bucket = self._new_bucket(time_stamp)

        remaining_tokens = tokens[3:-2]
        current_bucket.add(type, tag, remaining_tokens)

    def _new_bucket(self, start_time):
        end_time = start_time + self.interval
        bucket = Bucket(start_time, end_time)
        self.buckets.append(bucket)
        return bucket


class Bucket(object):
    aggregate_stats_classes = {
        't': TimerStats,
        'c': CounterStats
    }

    def __init__(self, start_time, end_time):
        self.start_time = start_time
        self.end_time = end_time
        self.stats = {}

    def in_bucket(self, time_stamp):
        return time_stamp >= self.start_time and time_stamp <= self.end_time

    def add(self, type, tag, tokens):
        if tag not in self.stats:
            self.stats[tag] = self.aggregate_stats_classes[type](type, tag)

        tag_stats = self.stats[tag]
        tag_stats.add(tokens)


parser = argparse.ArgumentParser(description='Aggregates metrics from Stopwatch formatted file')
parser.add_argument('-v', '--verbose', help='verbose logging', action='store_true', default=False)
parser.add_argument('-s', '--sort', help='sort order', choices=['tag', 'count', 'total', 'avg'], default='tag')
parser.add_argument('-r', '--reverse', help='reverse sort order', action='store_true', default=False)
parser.add_argument('-a', '--aggregate', help='aggregate stats in specified intervals. Intervals should be specified '
                                              'on the format nx, where n is a positive integer and x is one of \'s\' '
                                              '(seconds), \'m\' (minutes) or \'h\' (hours) ',
                    default=None)
parser.add_argument('file', help='file to parse')


def parse_interval(str_interval):
    if not str_interval:
        return None

    str_value = str_interval[0:-1]
    unit = str_interval[-1]

    intervals = {'s': 1, 'm': 60, 'h': 3600}
    if unit not in intervals:
        raise ValueError('Unknown unit: ' + unit + '. Expected one of ' + str(intervals.keys()))
    value = int(str_value)

    return value * intervals[unit]

if __name__ == "__main__":
    args = parser.parse_args()

    file_name = args.file

    log_interval = parse_interval(args.aggregate)
    print 'Interval: ' + str(log_interval)
    parser = LogParser(file_name, verbose=args.verbose, sort_by=args.sort, reverse=args.reverse,
                       interval=log_interval)
    stats = parser.parse()
    parser.print_stats(stats)