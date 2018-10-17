import logging

import localsearch_setup
from localsearch import iterative_improvement
import localsearch.utilities

"""
    The main.py script can be called from various sources to start a local search.
    It guarantees that all necessary resources are always created.
"""


def run_local_search(controller):
    return iterative_improvement(controller)


def automode_localsearch():
    localsearch_setup.setup_localsearch()
    localsearch.utilities.create_directory()
    # Run local search
    initial_controller = localsearch.utilities.get_initial_controller()
    initial_controller.draw("initial")
    result = run_local_search(initial_controller)
    result.draw("final")
    logging.info(result.convert_to_commandline_args())


if __name__ == "__main__":
    automode_localsearch()
