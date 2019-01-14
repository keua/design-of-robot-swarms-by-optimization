"""
This module tracks different stats over the run of a single local search
"""

import json

import stats.time
import stats.performance


def reset():
    """
    Reset the stats.
    Should be called after a single run of the local search
    """
    stats.time.reset()


def save():
    """
    Save the stats to a file.
    """
    # build a dict of all stats
    time_dict = {"total time": str(stats.time.elapsed_time()),
                 "simulation time": str(stats.time.simulation_time),
                 }
    stats_dict = {"time": time_dict}
    with open("stats.json", "w") as file:
        json.dump(stats_dict, file)
