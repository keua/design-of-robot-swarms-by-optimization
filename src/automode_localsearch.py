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
    Run a local instance of the program on this machine
    """
    experiment_setup = load_experiment_file(experiment_file)


def submit():
    """
    Submits the program to the scheduling system
    """
    pass


def parse_arguments():
    """This method parses the arguments to this script"""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title="execution", dest="execution_subcommand")
    parser_run = subparsers.add_parser('run', help='run a local search locally')
    parser_run.add_argument("-e", dest="experiment_file",
                            help="(relative) path to the experiment file")
    parser_submit = subparsers.add_parser('submit',
                                          help='submit the local search to a scheduling system')
    parser_submit.add_argument("-e", dest="experiment_file",
                               help="(relative) path to the experiment file")
    input_args = parser.parse_args()
    logging.warning(input_args)
    if input_args.execution_subcommand == "run":
        run_local(input_args.experiment_file)
    elif input_args.execution_subcommand == "submit":
        submit()
    else:
        logging.error(" Could not recognize subcommand {}."
                      "Please check the help for more information"
                      .format(input_args.execution_subcommand))


if __name__ == "__main__":
    parse_arguments()
