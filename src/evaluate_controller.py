import sys
import random
import logging
# from deprecated import localsearch_setup
from automode.controller.AutoMoDeBT import BT
from automode.controller.AutoMoDeFSM import FSM

# TODO: Guess this from controller file name
path_to_scenario = "/home/jkuckling/AutoMoDe-LocalSearch/experiments/vanilla/aggregation.argos"
architecture = "FSM"
default_controller_file = "/home/jkuckling/AutoMoDe-LocalSearch/controller/FSM/agg/FSM-agg-50k.txt"


def evaluate_controller(controller_args):
    """
    Parses a controller. Tries to guess the type of the controller from the passed controller_args
    :param controller_args:
    :return:
    """
    # Guess the type of the controller
    if controller_args[0] == "--rootnode":
        controller = BT.parse_from_commandline_args(controller_args)
    else:
        controller = FSM.parse_from_commandline_args(controller_args)
    # TODO: This is duplicated code from localsearch.py -- maybe find a solution to move this out of the method?
    seed_window = list()
    for i in range(0, 10):  # TODO: Make this dependent from Configuration
        seed_window.append(random.randint(0, 2147483647))
    controller.evaluate(seed_window)
    logging.debug(controller.scores)


def evaluate_all_controllers(controller_file):
    """

    :param controller_file:
    :return:
    """
    with open(controller_file) as file:
        controllers = file.readlines()
        for controller in controllers:
            evaluate_controller(controller.split(" "))


if __name__ == "__main__":
    """
        For more than one argument, parse the parameters as a controller.
        For one argument, read all controllers from the file and evaluate them.
        The results are printed to the terminal
    """
    localsearch_setup.setup_evaluation(architecture, path_to_scenario)
    if len(sys.argv) == 1:
        evaluate_all_controllers(default_controller_file)
    elif len(sys.argv) > 2:
        evaluate_controller(sys.argv)
    else:
        evaluate_all_controllers(sys.argv[1])
