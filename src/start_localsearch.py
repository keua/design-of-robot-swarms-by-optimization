#!/usr/bin/env python3

"""Use this script to start the local search. Run start_localsearch.py -h for more help."""

import argparse
import logging


def parse_arguments():

    """This method parses the arguments to this script"""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title="execution", dest="execution_subcommand")
    parser_run = subparsers.add_parser('run', help='run a local search locally')
    parser_run.add_argument("-c", help="(relative) path to the configuration file")
    parser_submit = subparsers.add_parser('submit',
                                          help='submit the local search to a scheduling system')
    parser_submit.add_argument("-c", help="(relative) path to the configuration file")
    input_args = parser.parse_args()
    logging.warning(input_args)
    if input_args.execution_subcommand == "run":
        pass
    elif input_args.execution_subcommand == "submit":
        pass
    else:
        logging.error(" Could not recognize subcommand {}."
                      "Please check the help for more information"
                      .format(input_args.execution_subcommand))


if __name__ == "__main__":
    parse_arguments()
