"""
This module provides functions for setting up the configuration of the local search
Examples:
     create a dummy configuration
     load a configuration from a (.ini) file
"""

import configparser
import os

from automode.architecture import FSM
from automode.architecture import BT
import execution
import localsearch.utilities
import settings


def default_configuration():
    """
    This function returns a dummy configuration.
    The dummy configuration contains a number of nonsense entries.
    Useful to test if all parameters are set.
    :return: A dummy configuration
    """
    return {
        # Default values if not read from the commandline
        "default_path_to_scenario": "/tmp/scenario",
        "default_budget": 0,
        "default_result_directory": "/tmp/result",
        # Values of the execution section of the configuration file
        "seed_window_size": 0,
        "seed_window_movement": 0,
        # Values of the controller section of the configuration file
        "controller_minimal_behavior": "None",
        "controller_minimal_condition": "None",
        "random_parameter_initialization": True,
        # Values of the FSM section of the configuration file
        "FSM_path_to_AutoMoDe": "/tmp/FSM_AutoMoDe",
        "FSM_max_states": 0,
        "FSM_max_transitions": 0,
        "FSM_max_transitions_per_state": 0,
        "FSM_no_self_transition": True,
        # Values of the BT section of the configuration file
        "BT_path_to_AutoMoDe": "/tmp/BT_AutoMoDe",
        "BT_max_actions": 0,
        # Values of the logging section of the configuration file
        "snapshot_frequency": 0,
        "log_level": "INFO",
    }


def load_configuration_from_file(config_file_name):
    """
    Loads the configuration values from the specified file.
    :param config_file_name: The file containing the configuration. If a path is given, it needs to be
    relative to the src/ folder.
    :return: a dictionary containing all necessary information
    """
    # TODO: Add checks to values

    def load_default_values():
        config["default_path_to_scenario"] = config_parser["Default Values"]["path_to_scenario"]
        config["default_result_directory"] = config_parser["Default Values"]["result_directory"]
        config["default_budget"] = int(config_parser["Default Values"]["budget"])

    def load_run_configuration():
        # parse the window size and movement
        config["seed_window_size"] = int(config_parser["Execution"]["seed_window_size"])
        config["seed_window_movement"] = int(config_parser["Execution"]["seed_window_movement"])

    def load_controller_configuration():
        # parse the controller configuration
        config["controller_minimal_behavior"] = config_parser["Controller"]["minimal_behavior"]
        config["controller_minimal_condition"] = config_parser["Controller"]["minimal_condition"]
        config["random_parameter_initialization"] = config_parser["Controller"].getboolean(
            "random_parameter_initialization")
        # parse information related to the FSM
        config["FSM_path_to_AutoMoDe"] = config_parser["FSM"]["path_to_AutoMoDe"]
        config["FSM_max_states"] = int(config_parser["FSM"]["max_states"])
        config["FSM_max_transitions"] = float(config_parser["FSM"]["max_transitions"])
        config["FSM_max_transitions_per_state"] = int(config_parser["FSM"]["max_transitions_per_state"])
        config["FSM_no_self_transition"] = config_parser["FSM"].getboolean("no_self_transition")
        # parse information related to the BT
        config["BT_path_to_AutoMoDe"] = config_parser["BT"]["path_to_AutoMoDe"]
        config["BT_max_actions"] = int(config_parser["BT"]["max_actions"])

    config = default_configuration()
    config_parser = configparser.ConfigParser()
    config_parser.read(config_file_name)
    load_default_values()
    load_run_configuration()
    load_controller_configuration()
    # parse logging configuration
    config["snapshot_frequency"] = int(config_parser["Logging"]["snapshot_frequency"])
    config["log_level"] = config_parser["Logging"]["log_level"]
    return config


BUDGET_DEFAULT = 0
SCENARIO_DEFAULT = "missing.argos"
RESULT_DEFAULT = "/dev/null"
JOB_NAME_DEFAULT = ""


def set_parameters_fsm(max_states, max_transitions, max_transitions_per_state, no_self_transition, minimal_behavior,
                       random_parameter_initialization):
    """
    Sets the configuration parameters of the FSM module
    :param max_states:
    :param max_transitions:
    :param max_transitions_per_state:
    :param no_self_transition:
    :param minimal_behavior:
    :param random_parameter_initialization:
    """
    # parameters for the FSM
    FSM.parameters["max_states"] = max_states
    FSM.parameters["max_transitions"] = max_transitions
    FSM.parameters["max_transitions_per_state"] = max_transitions_per_state
    FSM.parameters["no_self_transition"] = no_self_transition
    FSM.parameters["initial_state_behavior"] = minimal_behavior
    FSM.parameters["random_parameter_initialization"] = random_parameter_initialization


def set_parameters_bt(max_actions, minimal_behavior, minimal_condition, random_parameter_initialization):
    """
    Sets the configuration parameters of the BT module
    :param max_actions:
    :param minimal_behavior:
    :param minimal_condition:
    :param random_parameter_initialization:
    :return:
    """
    # parameters for the BT
    BT.parameters["max_actions"] = max_actions
    BT.parameters["minimal_behavior"] = minimal_behavior
    BT.parameters["minimal_condition"] = minimal_condition
    BT.parameters["random_parameter_initialization"] = random_parameter_initialization


def set_controller_parameters(config):
    """
    Sets the configuration parameters for the FSM and BT module
    :param config:
    """
    # Initialize all controller types
    set_parameters_fsm(config["FSM_max_states"], config["FSM_max_transitions"], config["FSM_max_transitions_per_state"],
                       config["FSM_no_self_transition"], config["controller_minimal_behavior"],
                       config["random_parameter_initialization"])
    set_parameters_bt(config["BT_max_actions"], config["controller_minimal_behavior"],
                      config["controller_minimal_condition"], config["random_parameter_initialization"])


def set_execution_parameters(architecture, parallel, scenario, config):
    """
    Sets the configuration parameters in the execution module
    :param architecture:
    :param parallel:
    :param scenario:
    :param config:
    :return:
    """
    if parallel > 1:
        execution.mpi_enabled = True
        execution.parallel = parallel
    else:
        execution.mpi_enabled = False

    settings.architecture = architecture
    settings.seed_window_size = config["seed_window_size"]
    settings.seed_window_movement = config["seed_window_movement"]

    if architecture == "BT":
        path_to_AutoMoDe_executable = config["BT_path_to_AutoMoDe"]
    else:
        path_to_AutoMoDe_executable = config["FSM_path_to_AutoMoDe"]
    execution.setup(path_to_AutoMoDe_executable, scenario)


def set_localsearch_parameters(initial_controller, job_name, result_directory, config_file_name, budget,
                               snapshot_frequency):
    """
    Sets the configuration parameters in the localsearch module
    :param initial_controller:
    :param job_name:
    :param result_directory:
    :param config_file_name:
    :param budget:
    :param snapshot_frequency:
    """
    localsearch.utilities.initial_controller = initial_controller
    localsearch.utilities.job_name = job_name
    localsearch.utilities.result_directory = result_directory
    localsearch.utilities.config_file_name = config_file_name
    localsearch.localsearch.budget = budget
    localsearch.localsearch.snapshot_frequency = snapshot_frequency


def apply_configuration(args, config):
    """
    Applies the combination of input arguments and configuration values.
    Does not require the input arguments (args) to be preprocessed (that is potential defaults replaced).
    :param args: The input parameters as read from the terminal
    :param config: A dictionary containing the configuration data
    """
    if args["budget"] == BUDGET_DEFAULT:
        args["budget"] = config["default_budget"]
    if args["path_to_scenario"] == SCENARIO_DEFAULT:
        args["path_to_scenario"] = config["default_path_to_scenario"]
    if args["result_directory"] == RESULT_DEFAULT:
        args["result_directory"] = config["default_result_directory"]
        print(args["result_directory"])
    if args["job_name"] == JOB_NAME_DEFAULT:
        args["job_name"] = "{}-{}-{}-{}".format(args["architecture"],
                                                # get the file name (os.path.split(...)[1])
                                                # and the file without ending (split(".")[0])
                                                os.path.split(args["path_to_scenario"])[1].split(".")[0],
                                                args["budget"], args["initial_controller"])
    # TODO: Set the right log level here
    set_controller_parameters(config)
    set_execution_parameters(args["architecture"], args["parallel"], args["path_to_scenario"], config)
    set_localsearch_parameters(args["initial_controller"], args["job_name"], args["result_directory"],
                               args["config_file_name"], args["budget"], config["snapshot_frequency"])
