"""

    metrics: median, 80, 90, 95, 99

    --output (pretty, csv, json)


"""
import sys, argparse
from stopwatch import TimeLogger


class LogParser(object):

    sort = {
        'tag': lambda stat: stat.tag,
        'count': lambda stat: stat.event_count,
        'total': lambda stat: stat.total_time,
        'avg': lambda stat: stat.average
    }

    def __init__(self, in_file, verbose=True, sort_by='tag', reverse=False):
        self.in_file = in_file
        self.verbose = verbose
        self.sort_by = sort_by
        self.reverse = reverse

    def parse(self):
        with open(self.in_file) as file:
            return self._parse_lines(file)

    def print_stats(self, aggregate_stats):
        tag_col_width = max(len(tag_stats.tag) for tag_stats in aggregate_stats) + 2

        print ''
        print "{}{:>10}    {:>10}    {:>10}".format('Tag'.ljust(tag_col_width), 'Count', 'Total', 'Avg')
        for tag_stats in sorted(aggregate_stats, key=self.sort[self.sort_by], reverse=self.reverse):
            tag_justified = tag_stats.tag.ljust(tag_col_width)
            print "{}{:10d}    {:10.3f}    {:10.3f}".format(tag_justified, tag_stats.event_count, tag_stats.total_time,
                                                            tag_stats.average)
        print ''

    def _parse_lines(self, file):
        aggregate_stats = {}
        line_count = 1
        for line in file:
            try:
                line = line.strip()
                self._parse_line(line, aggregate_stats)
                line_count += 1
            except:
                if self.verbose:
                    e = sys.exc_info()[0]
                    sys.stderr.write('Error reading line {} {}: {}'.format(line_count, line, e))
        return aggregate_stats.values()

    def _parse_line(self, line, aggregate_stats):
        if not self.is_stopwatch_line(line):
            return

        tokens = line.split()
        time_stamp = tokens[1]
        event_count = int(tokens[-2])
        elapsed_time = float(tokens[-3])
        tag = ' '.join(tokens[2:-3])

        if tag not in aggregate_stats:
            aggregate_stats[tag] = AggregateTagStats(tag)

        tag_stats = aggregate_stats[tag]
        tag_stats.add(event_count=event_count, elapsed_time=elapsed_time)

    @staticmethod
    def is_stopwatch_line(line):
        return line and line.startswith(TimeLogger.START_TOKEN) and line.endswith(TimeLogger.END_TOKEN)


class AggregateTagStats(object):
    def __init__(self, tag):
        self.tag = tag
        self.event_count = 0
        self.total_time = 0.0
        self.average = 0.0

    def add(self, event_count, elapsed_time):
        self.event_count += event_count
        self.total_time += elapsed_time
        self.average = self.total_time / self.event_count


parser = argparse.ArgumentParser(description='Aggregates metrics from Stopwatch formatted file')
parser.add_argument('-v', '--verbose', help='verbose logging', action='store_true', default=False)
parser.add_argument('-s', '--sort', help='sort order', choices=['tag', 'count', 'total', 'avg'], default='tag')
parser.add_argument('-r', '--reverse', help='reverse sort order', action='store_true', default=False)
parser.add_argument('file', help='file to parse')

if __name__ == "__main__":
    args = parser.parse_args()

    file_name = args.file

    parser = LogParser(file_name, verbose=args.verbose, sort_by=args.sort, reverse=args.reverse)
    stats = parser.parse()
    parser.print_stats(stats)