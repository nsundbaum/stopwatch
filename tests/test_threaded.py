import sys, time, logging, random, threading


root = logging.getLogger()
root.setLevel(logging.INFO)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
root.addHandler(ch)

from context import StopWatch, AggregateTimeLogger


log = AggregateTimeLogger(root, 2)


def work(tag):
    stop_watch = StopWatch(log)
    for i in range(100):
        time.sleep(random.uniform(0.01, 0.1))
        stop_watch.lap(tag)

root.info('Starting...')

threads = []
for i in range(100):
    t = threading.Thread(target=work, args=(str(i%10),))
    t.daemon = True
    t.start()
    threads.append(t)

for t in threads:
    t.join()

log.flush()
