__author__ = "Jonas Kuckling, jonas.kuckling@ulb.ac.be"
"""
Track different stats for the expenditure of time.
"""

from datetime import datetime, timedelta


start_time = None
end_time = None

simulation_time = timedelta()
simulation_start = None


def reset():
    global start_time, end_time, simulation_time, simulation_start
    start_time = None
    end_time = None
    simulation_start = None
    simulation_time = timedelta()


def start_run():
    global start_time
    start_time = datetime.now()


def end_run():
    global end_time
    end_time = datetime.now()


def elapsed_time():
    return end_time - start_time


def start_simulation():
    global simulation_start
    simulation_start = datetime.now()


def end_simulation():
    global simulation_time
    simulation_end = datetime.now()
    simulation_time += (simulation_end - simulation_start)
