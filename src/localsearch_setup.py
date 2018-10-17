import argparse
from config.configuration import Configuration
from automode.controller.AutoMoDeFSM import FSM
from automode.controller.AutoMoDeBT import BT
import execution
import logging
import localsearch.utilities


def set_parameters_fsm(config):
    # parameters for the evaluation
    FSM.scenario_file = config.path_to_scenario
    # parameters for the FSM
    FSM.parameters["max_states"] = config.FSM_max_states
    FSM.parameters["max_transitions"] = config.FSM_max_transitions
    FSM.parameters["max_transitions_per_state"] = config.FSM_max_transitions_per_state
    FSM.parameters["no_self_transition"] = config.FSM_no_self_transition
    FSM.parameters["initial_state_behavior"] = config.controller_minimal_behavior
    FSM.parameters["random_parameter_initialization"] = config.random_parameter_initialization


def set_parameters_bt(config):
    # parameters for the evaluation
    BT.scenario_file = config.path_to_scenario
    # parameters for the BT
    BT.parameters["max_actions"] = config.BT_max_actions
    BT.parameters["minimal_behavior"] = config.controller_minimal_behavior
    BT.parameters["minimal_condition"] = config.controller_minimal_condition
    BT.parameters["random_parameter_initialization"] = config.random_parameter_initialization


def set_controller_parameters(config):
    # Initialize all controller types
    set_parameters_fsm(config)
    set_parameters_bt(config)


def set_execution_parameters(controller_type, config):
    execution.use_mpi = config.MPI
    execution.set_scenario(config.path_to_scenario)
    execution.set_seed_window(config.seed_window_size, config.seed_window_movement)
    executor = execution.get_executor()
    executor.controller_type = controller_type
    if controller_type == "BT":
        executor.path_to_AutoMoDe_executable = config.BT_path_to_AutoMoDe
    else:
        executor.path_to_AutoMoDe_executable = config.FSM_path_to_AutoMoDe


def set_localsearch_parameters(args, config):
    localsearch.utilities.initial_controller = args["initial_controller"]
    localsearch.utilities.job_name = args["job_name"]
    localsearch.utilities.result_directory = args["result_directory"]
    localsearch.utilities.config_file_name = args["config_file_name"]


def load_config(args):
    config = Configuration.load_from_file(args["config_file_name"])
    # TODO: Set the right log level here
    # SimpleLogger.instance.log_level = SimpleLogger.LogLevel[Configuration.instance.log_level]
    set_controller_parameters(config)
    set_execution_parameters(args["controller_type"], config)
    set_localsearch_parameters(args, config)
    # Configuration.instance.src_directory = "src/"


def parse_input():
    """
    Parses the input from the command line
    :return: A dictionary containing the parsed arguments
    """
    parser = argparse.ArgumentParser(description="Run the local search algorithm")
    parser.add_argument('-c', '--config', dest="config_file", default="config.ini",
                        help="The configuration file for the local search algorithm")
    parser.add_argument('-r', '--result_directory', dest="result_dir", default="result/",
                        help="The directory where the results of the local search algorithm are written")
    parser.add_argument('-s', '--scenario_file', dest="scenario_file", default="missing.argos",
                        help="The scenario file for the improvement")
    parser.add_argument('-i', '--initial_controller', dest="initial_controller", default="minimal",
                        help="The initial controller for the local search. Empty if there it should start from a minimal controller")
    parser.add_argument('-exe', '--automode_executable', dest="executable", default="automode_main",
                        help="The AutoMoDe executable")
    parser.add_argument('-j', '--job_name', dest="job_name", default="",
                        help="The job name, used for the results folder")
    parser.add_argument('-t', '--controller_type', dest="controller_type", default="FSM",
                        help="The type of controller used (important for a minimal start)")
    input_args = parser.parse_args()
    # Get the information
    arguments = {"config_file_name": input_args.config_file,
                 "result_directory": input_args.result_dir,
                 "path_to_scenario": input_args.scenario_file,
                 "initial_controller": input_args.initial_controller,
                 "job_name": input_args.job_name,
                 "controller_type": input_args.controller_type
                 }
    return arguments


def setup_localsearch():
    args = parse_input()
    load_config(args)


def setup_evaluation(controller_type, scenario):
    load_config("/home/jkuckling/AutoMoDe-LocalSearch/src/config/config_evaluation.ini")

