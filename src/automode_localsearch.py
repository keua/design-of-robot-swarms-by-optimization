#!/usr/bin/env python3

"""
Use this script to start the local search. Run start_localsearch.py -h for more help.
"""

import argparse
import logging


def load_experiment_file(experiment_file):
    """
    Loads the specified experiment file and returns a dictionary containing the values.
    :param experiment_file:
    :return: A dictionary containing the values defined in the experiment file
    """
    # TODO: Load the experiment file here
    return {}


def run_local(experiment_file):
    """
    Reads the experiments_file and performs the experiment on the local machine
    """
    experiment_setup = load_experiment_file(experiment_file)


def submit():
    """
    Reads the experiments_file and submits the experiment to the scheduling system
    """
    pass


def execute_localsearch():
    """
    Executes a single run of the localsearch
    """
    pass


def parse_arguments():
    """This method parses the arguments to this script"""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title="execution", dest="execution_subcommand")
    parser_local = subparsers.add_parser('local', help='run an experiment locally')
    parser_local.add_argument("-e", dest="experiment_file",
                              help="(relative) path to the experiment file")
    parser_submit = subparsers.add_parser('submit',
                                          help='submit an experiment to a scheduling system')
    parser_submit.add_argument("-e", dest="experiment_file",
                               help="(relative) path to the experiment file")
    parser_local = subparsers.add_parser('run', help='run a single execution of the local search')
    # TODO: Add run configuration (or load it from the helper)
    input_args = parser.parse_args()
    logging.warning(input_args)
    if input_args.execution_subcommand == "local":
        run_local(input_args.experiment_file)
    elif input_args.execution_subcommand == "submit":
        submit()
    elif input_args.execution_subcommand == "run":
        execute_localsearch()
    else:
        logging.error(" Could not recognize subcommand {}."
                      "Please check the help for more information"
                      .format(input_args.execution_subcommand))


if __name__ == "__main__":
    parse_arguments()
