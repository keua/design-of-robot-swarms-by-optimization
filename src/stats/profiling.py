__author__ = "Jonas Kuckling, jonas.kuckling@ulb.ac.be"
import cProfile
import tracemalloc


def profile_runtime(method):
    """
    Takes the method as string that can be passed to exec
    :param method:
    :return:
    """
    cProfile.run(method)


last_snapshot = None


def start_profiling_memory():
    tracemalloc.start()
    global last_snapshot
    last_snapshot = tracemalloc.take_snapshot()


def get_memory_snapshot():
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')

    print("[ Snapshot Top 10 ]")
    for stat in top_stats[:10]:
        print(stat)
    global last_snapshot
    last_snapshot = snapshot


def get_memory_diff():
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.compare_to(last_snapshot, 'lineno')

    print("[ Top 10 differences ]")
    for stat in top_stats[:10]:
        print(stat)
