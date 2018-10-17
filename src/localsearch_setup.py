import argparse
from config.configuration import Configuration
from automode.controller.AutoMoDeFSM import FSM
from automode.controller.AutoMoDeBT import BT
import execution
import logging
import localsearch.utilities
import os

BUDGET_DEFAULT = 0
SCENARIO_DEFAULT = "missing.argos"
RESULT_DEFAULT = "/dev/null"
JOB_NAME_DEFAULT = ""


def set_parameters_fsm(config):
    # parameters for the FSM
    FSM.parameters["max_states"] = config.FSM_max_states
    FSM.parameters["max_transitions"] = config.FSM_max_transitions
    FSM.parameters["max_transitions_per_state"] = config.FSM_max_transitions_per_state
    FSM.parameters["no_self_transition"] = config.FSM_no_self_transition
    FSM.parameters["initial_state_behavior"] = config.controller_minimal_behavior
    FSM.parameters["random_parameter_initialization"] = config.random_parameter_initialization


def set_parameters_bt(config):
    # parameters for the BT
    BT.parameters["max_actions"] = config.BT_max_actions
    BT.parameters["minimal_behavior"] = config.controller_minimal_behavior
    BT.parameters["minimal_condition"] = config.controller_minimal_condition
    BT.parameters["random_parameter_initialization"] = config.random_parameter_initialization


def set_controller_parameters(config):
    # Initialize all controller types
    set_parameters_fsm(config)
    set_parameters_bt(config)


def set_execution_parameters(controller_type, parallel, scenario, config):
    if parallel > 1:
        execution.mpi_enabled = True
        execution.parallel = parallel
    else:
        execution.mpi_enabled = False
    execution.set_scenario(scenario)
    execution.set_seed_window(config.seed_window_size, config.seed_window_movement)
    executor = execution.get_executor()
    executor.controller_type = controller_type
    if controller_type == "BT":
        executor.path_to_AutoMoDe_executable = config.BT_path_to_AutoMoDe
    else:
        executor.path_to_AutoMoDe_executable = config.FSM_path_to_AutoMoDe


def set_localsearch_parameters(args):
    localsearch.utilities.initial_controller = args["initial_controller"]
    localsearch.utilities.job_name = args["job_name"]
    localsearch.utilities.result_directory = args["result_directory"]
    localsearch.utilities.config_file_name = args["config_file_name"]


def load_config(file_name):
    return Configuration.load_from_file(file_name)


def parse_input():
    """
    Parses the input from the command line
    :return: A dictionary containing the parsed arguments
    """
    parser = argparse.ArgumentParser(description="Run the local search algorithm")
    # Required arguments
    parser.add_argument('-c', '--config', dest="config_file", required=True,
                        help="The configuration file for the local search algorithm. "
                             " (REQUIRED)")
    parser.add_argument('-t', '--controller_type', dest="controller_type", default="FSM", required=True,
                        help="The type of controller used (FSM or BT). "
                             "(REQUIRED)")
    # Recommended arguments
    parser.add_argument('-s', '--scenario_file', dest="scenario_file", default=SCENARIO_DEFAULT, required=False,
                        help="The scenario file for the improvement. "
                             "If this is not set, the default from the config file is used.")
    parser.add_argument('-b', '--budget', dest="budget", default=BUDGET_DEFAULT, type=int, required=False,
                        help="The budget allocated for the localsearch. "
                             "If this is not set, the default from the config file is used.")
    parser.add_argument('-i', '--initial_controller', dest="initial_controller", default="minimal",
                        help="The initial controller for the local search. "
                             "If this is not set, the localsearch will start from a minimal controller.")
    parser.add_argument('-j', '--job_name', dest="job_name", default=JOB_NAME_DEFAULT, required=False,
                        help="The job name, used for the results folder. "
                             "If this is not set, one will be created from the scenario, budget and initial "
                             "controller information.")
    # Optional arguments
    parser.add_argument('-r', '--result_directory', dest="result_dir", default=RESULT_DEFAULT, required=False,
                        help="The directory where the results of the local search algorithm are written. "
                             "If this is not set, the default from the config file is used.")
    # TODO: Check that -p is at least 2
    parser.add_argument('-p', '--parallel', dest="parallel", default=0, required=False, type=int,
                        help="The number of parallel nodes reserved for the execution. "
                             "If this is not set, then the localsearch will be executed completely sequential.")
    input_args = parser.parse_args()
    # Get the information
    arguments = {"config_file_name": input_args.config_file,
                 "controller_type": input_args.controller_type,
                 "path_to_scenario": input_args.scenario_file,
                 "budget": input_args.budget,
                 "initial_controller": input_args.initial_controller,
                 "job_name": input_args.job_name,
                 "result_directory": input_args.result_dir,
                 "parallel": input_args.parallel,
                 }
    return arguments


def setup_localsearch():
    args = parse_input()
    config = load_config(args["config_file_name"])
    # check if defaults are needed
    if args["budget"] == BUDGET_DEFAULT:
        args["budget"] = config.default_budget
    if args["path_to_scenario"] == SCENARIO_DEFAULT:
        args["path_to_scenario"] = config.default_path_to_scenario
    if args["result_directory"] == RESULT_DEFAULT:
        args["result_directory"] = config.default_result_directory
        print(args["result_directory"])
    if args["job_name"] == JOB_NAME_DEFAULT:
        args["job_name"] = "{}-{}-{}-{}".format(args["controller_type"],
                                                # get the file name (os.path.split(...)[1])
                                                # and the file without ending (split(".")[0])
                                                os.path.split(args["path_to_scenario"])[1].split(".")[0],
                                                args["budget"], args["initial_controller"])
    # TODO: Set the right log level here
    set_controller_parameters(config)
    set_execution_parameters(args["controller_type"], args["parallel"], args["path_to_scenario"], config)
    set_localsearch_parameters(args)


def setup_evaluation(controller_type, scenario):
    # TODO: Fix this!!!!
    load_config("/home/jkuckling/AutoMoDe-LocalSearch/src/config/config_evaluation.ini")

