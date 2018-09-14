import os
from datetime import datetime
from automode.controller import FSM, BT
import shutil
import argparse
from configuration import Configuration
from automode.execution import AutoMoDeExecutor
from simple_logging import Logger
import localsearch

"""
    The main.py script can be called from various sources to start a local search.
    It guarantees that all necessary resources are always created.
"""


def run_local_search(controller):
    return localsearch.iterative_improvement(controller)


def load_config():
    Configuration.load_from_file(Configuration.instance.config_file_name)


def create_directory():
    Logger.instance.log_debug("Directory of this file {}".format(os.path.realpath(__file__)))
    src_directory = os.path.split(os.path.realpath(__file__))[0]
    os.chdir(Configuration.instance.result_directory)
    str_time = datetime.now().strftime("%Y%m%d-%H:%M:%S")
    exp_dir = "{}_{}".format(Configuration.instance.job_name, str_time)
    os.mkdir(exp_dir)
    os.chdir(exp_dir)
    # copy the configuration file
    new_config_filename = "config_{}.ini".format(str_time)
    shutil.copyfile("{}/{}".format(
        src_directory, Configuration.instance.config_file_name), "{}/{}".format(os.getcwd(), new_config_filename))


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


def set_parameters():
    # Initialize all controller types
    set_parameters_fsm()
    set_parameters_bt()


def get_controller_class():
    if Configuration.instance.controller_type == "FSM":
        return FSM
    elif Configuration.instance.controller_type == "BT":
        return BT
    else:
        Logger.instance.log_warning("WARNING: The specified type {} is not known.".format(Configuration.instance.controller_type))
        return None


def parse_input():
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
    Configuration.instance.config_file_name = input_args.config_file
    Configuration.instance.result_directory = input_args.result_dir
    Configuration.instance.path_to_scenario = input_args.scenario_file
    Configuration.instance.initial_controller = input_args.initial_controller
    Configuration.instance.path_to_AutoMoDe = input_args.executable
    Configuration.instance.job_name = input_args.job_name
    Configuration.instance.controller_type = input_args.controller_type


def create_executor():
    executor = AutoMoDeExecutor()


def automode_localsearch():
    logger = Logger()
    config = Configuration()
    parse_input()
    load_config()
    Logger.instance.log_level = Logger.LogLevel[Configuration.instance.log_level]
    create_directory()
    set_parameters()
    create_executor()
    if Configuration.instance.initial_controller == "minimal":
        Configuration.instance.initial_controller = get_controller_class()()
    else:
        controller_file, line = Configuration.instance.initial_controller.split(":")
        with open(controller_file, mode='r') as file:
            for i in range(0, int(line)):
                controller = file.readline()
        controller = controller.split(" ")
        Configuration.instance.initial_controller = get_controller_class()().parse_from_commandline_args(controller)
    # Run local search
    for i in range(0, Configuration.instance.num_runs):
        # generate initial FSM
        initial_controller = Configuration.instance.initial_controller
        os.mkdir("run_{}".format(i))
        os.chdir("run_{}".format(i))
        initial_controller.draw("initial")
        result = run_local_search(initial_controller)
        result.draw("final")
        Logger.instance.log(result.convert_to_commandline_args())
        os.chdir("..")


# print(__name__)
if __name__ == "__main__":
    automode_localsearch()

if __name__ == "__worker__":
    Logger()
