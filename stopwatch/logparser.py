"""
    logparser [IN_FILE]

    import argparse

    parser = argparse.ArgumentParser(description='Parse stopwatch compatible log files and produce aggregate statistics')
    parser.add_argument('file', metavar='FILE', type=file,
                    help='file to parse')

    args = parser.parse_args()

"""
import sys
from stopwatch import TimeLogger


class LogParser(object):

    def __init__(self, in_file):
        self.in_file = in_file

    def parse(self):
        with open(self.in_file) as file:
            return self._parse_lines(file)

    def print_stats(self, aggregate_stats):
        tag_col_width = max(len(tag) for tag in aggregate_stats.keys()) + 2

        print ''
        print ''
        for tag in sorted(aggregate_stats):
            tag_justified = tag.ljust(tag_col_width)
            tag_stats = aggregate_stats[tag]
            print "{}{:10d}    {:10.3f}    {:10.3f}".format(tag_justified, tag_stats.event_count, tag_stats.total_time, tag_stats.average())
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
                e = sys.exc_info()[0]
                sys.stderr.write('Error reading line {} {}: {}'.format(line_count, line, e))
        return aggregate_stats

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

    def add(self, event_count, elapsed_time):
        self.event_count += event_count
        self.total_time += elapsed_time

    def average(self):
        return self.total_time / self.event_count

if __name__ == "__main__":
    file_name = sys.argv[1]

    parser = LogParser(file_name)
    stats = parser.parse()
    parser.print_stats(stats)