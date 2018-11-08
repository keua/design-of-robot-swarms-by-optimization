#!/usr/bin/env python3

"""
Use this script to start the local search. Run start_localsearch.py -h for more help.
"""

import argparse
import logging
from configuration import BUDGET_DEFAULT, SCENARIO_DEFAULT, RESULT_DEFAULT, JOB_NAME_DEFAULT


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

    def create_subparser_local():
        """
        Sets up the parser for the subcommand local.
        This subcommand will execute a whole experiment on the local machine.
        """
        parser_local = subparsers.add_parser('local', help='run an experiment locally')
        parser_local.add_argument("-e", dest="experiment_file",
                                  help="(relative) path to the experiment file")

    def create_subparser_submit():
        """
        Sets up the parser for the subcommand submit.
        This subcommand will submit a whole experiment to the scheduler.
        """
        parser_submit = subparsers.add_parser('submit',
                                              help='submit an experiment to a scheduling system')
        parser_submit.add_argument("-e", dest="experiment_file",
                                   help="(relative) path to the experiment file")

    def create_subparser_run():
        """
        Sets up the parser for the subcommand run.
        This subcommand will execute a single local search.
        """
        parser_run = subparsers.add_parser('run', help='run a single execution of the local search')
        # Required arguments
        parser_run.add_argument('-c', '--config', dest="config_file", required=True,
                                help="The configuration file for the local search algorithm. "
                                " (REQUIRED)")
        parser_run.add_argument('-t', '--controller_type', dest="controller_type", default="FSM", required=True,
                                help="The type of controller used (FSM or BT). "
                                "(REQUIRED)")
        # Recommended arguments
        parser_run.add_argument('-s', '--scenario_file', dest="scenario_file", default=SCENARIO_DEFAULT, required=False,
                                help="The scenario file for the improvement. "
                                "If this is not set, the default from the config file is used.")
        parser_run.add_argument('-b', '--budget', dest="budget", default=BUDGET_DEFAULT, type=int, required=False,
                                help="The budget allocated for the localsearch. "
                                "If this is not set, the default from the config file is used.")
        parser_run.add_argument('-i', '--initial_controller', dest="initial_controller", default="minimal",
                                help="The initial controller for the local search. "
                                "If this is not set, the localsearch will start from a minimal controller.")
        parser_run.add_argument('-j', '--job_name', dest="job_name", default=JOB_NAME_DEFAULT, required=False,
                                help="The job name, used for the results folder. "
                                "If this is not set, one will be created from the scenario, budget and initial "
                                "controller information.")
        # Optional arguments
        parser_run.add_argument('-r', '--result_directory', dest="result_dir", default=RESULT_DEFAULT, required=False,
                                help="The directory where the results of the local search algorithm are written. "
                                "If this is not set, the default from the config file is used.")
        # TODO: Check that -p is at least 2
        parser_run.add_argument('-p', '--parallel', dest="parallel", default=0, required=False, type=int,
                                help="The number of parallel nodes reserved for the execution. "
                                "If this is not set, then the localsearch will be executed completely sequential.")

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title="execution", dest="execution_subcommand")
    create_subparser_local()
    create_subparser_submit()
    create_subparser_run()
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
