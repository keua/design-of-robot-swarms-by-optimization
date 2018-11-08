"""
    The main.py script can be called from various sources to start a local search.
    It guarantees that all necessary resources are always created.
"""

import logging

from deprecated import localsearch_setup
from localsearch import iterative_improvement
import localsearch.utilities


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
    best_controller = result.convert_to_commandline_args()
    logging.info(best_controller)
    with open("best_controller.txt", mode="w") as file:
        file.write(" ".join(best_controller))


if __name__ == "__main__":
    automode_localsearch()
