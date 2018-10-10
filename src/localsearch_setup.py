import argparse
from config.configuration import Configuration
from automode.controller.AutoMoDeFSM import FSM
from automode.controller.AutoMoDeBT import BT
from execution import AutoMoDeExecutor
from logging import SimpleLogger


def set_parameters_fsm():
    # parameters for the evaluation
    FSM.scenario_file = Configuration.instance.path_to_scenario
    # parameters for the FSM
    FSM.parameters["max_states"] = Configuration.instance.FSM_max_states
    FSM.parameters["max_transitions"] = Configuration.instance.FSM_max_transitions
    FSM.parameters["max_transitions_per_state"] = Configuration.instance.FSM_max_transitions_per_state
    FSM.parameters["no_self_transition"] = Configuration.instance.FSM_no_self_transition
    FSM.parameters["initial_state_behavior"] = Configuration.instance.controller_minimal_behavior
    FSM.parameters["random_parameter_initialization"] = Configuration.instance.random_parameter_initialization


def set_parameters_bt():
    # parameters for the evaluation
    BT.scenario_file = Configuration.instance.path_to_scenario
    # parameters for the BT
    BT.parameters["max_actions"] = Configuration.instance.BT_max_actions
    BT.parameters["minimal_behavior"] = Configuration.instance.controller_minimal_behavior
    BT.parameters["minimal_condition"] = Configuration.instance.controller_minimal_condition
    BT.parameters["random_parameter_initialization"] = Configuration.instance.random_parameter_initialization


def set_controller_parameters():
    # Initialize all controller types
    set_parameters_fsm()
    set_parameters_bt()


def load_config(file_name):
    Configuration.load_from_file(file_name)
    SimpleLogger.instance.log_level = SimpleLogger.LogLevel[Configuration.instance.log_level]
    set_controller_parameters()


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


def setup_executor(controller_type, scenario):
    executor = AutoMoDeExecutor()
    executor.use_mpi = Configuration.instance.MPI
    if controller_type == "BT":
        executor.path_to_AutoMoDe_executable = Configuration.instance.BT_path_to_AutoMoDe
    else:
        executor.path_to_AutoMoDe_executable = Configuration.instance.FSM_path_to_AutoMoDe
    executor.scenario_file = scenario


def setup_logger():
    """
        Creats the default logger
    """
    print("Logger generated")
    logger = SimpleLogger()


def setup_configuration():
    """
        Creates an empty (default) configuration
    """
    config = Configuration()


def setup_localsearch():
    args = parse_input()
    load_config(args["config_file_name"])
    # TODO: Don't save this in the config
    Configuration.instance.path_to_scenario = args["path_to_scenario"]
    Configuration.instance.config_file_name = args["config_file_name"]
    Configuration.instance.src_directory = "src/"
    Configuration.instance.result_directory = args["result_directory"]
    Configuration.instance.initial_controller = args["initial_controller"]
    Configuration.instance.job_name = args["job_name"]
    Configuration.instance.controller_type = args["controller_type"]
    setup_executor(args["controller_type"], args["path_to_scenario"])


def setup_evaluation(controller_type, scenario):
    load_config("/home/jkuckling/AutoMoDe-LocalSearch/src/config/config_evaluation.ini")
    setup_executor(controller_type, scenario)


# things that always need to be done
#   generate a logger
setup_logger()
#   generate an empty configuration
setup_configuration()
