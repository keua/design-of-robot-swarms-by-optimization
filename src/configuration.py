"""
This module provides functions for setting up the configuration of the local search
Examples:
     create a dummy configuration
     load a configuration from a (.ini) file
"""

import configparser
import os
import logging

from automode.architecture import FSM
from automode.architecture import BT
import execution
import localsearch.utilities
import settings


def default_configuration():
    """
    This function sets the settings.py module a dummy configuration.
    The dummy configuration contains a number of nonsense entries.
    Useful to test if all parameters are set.
    """
    settings.architecture = settings.ARCHITECTURE_DEFAULT
    # TODO: Find other settings from args
    # Default values if not read from the commandline
    settings.path_to_scenario = settings.SCENARIO_DEFAULT
    settings.budget = settings.BUDGET_DEFAULT
    settings.result_directory = settings.RESULT_DEFAULT
    # Values of the execution section of the configuration file
    settings.seed_window_size = settings.SEED_SIZE_DEFAULT
    settings.seed_window_movement = settings.SEED_MOVE_DEFAULT
    # Values of the controller section of the configuration file
    settings.minimal_behavior = settings.MINIMAL_BEHAVIOR_DEFAULT
    settings.minimal_condition = settings.MINIMAL_CONDITION_DEFAULT
    settings.random_parameter_initialization = settings.RANDOM_PARAMETER_DEFAULT
    # Values of the FSM section of the configuration file
    settings.FSM_path_to_AutoMoDe = settings.FSM_AUTOMODE_DEFAULT
    settings.FSM_max_states = settings.FSM_MAX_STATES_DEFAULT
    settings.FSM_max_transitions = settings.FSM_MAX_TRANSITIONS_DEFAULT
    settings.FSM_max_transitions_per_state = settings.FSM_MAX_TRANSITIONS_PER_STATE_DEFAULT
    settings.FSM_no_self_transition = not settings.FSM_SELF_TRANSITION_DEFAULT  # TODO: Refactor this setting to positive
    # Values of the BT section of the configuration file
    settings.BT_path_to_AutoMoDe = settings.BT_AUTOMODE_DEFAULT
    settings.BT_max_actions = settings.BT_MAX_ACTIONS_DEFAULT
    # Values of the logging section of the configuration file
    settings.snapshot_frequency = settings.SNAPSHOT_FREQUENCY_DEFAULT
    settings.log_level = settings.LOG_LEVEL_DEFAULT


def load_from_file(config_file_name):
    """
    Loads the configuration values from the specified file and updates the settings.py module.
    :param config_file_name: The file containing the configuration. If a path is given, it needs to be
    relative to the src/ folder.
    """
    # TODO: Add checks to values

    def load_default_values():
        settings.path_to_scenario = config_parser["Default Values"]["path_to_scenario"]
        settings.result_directory = config_parser["Default Values"]["result_directory"]
        settings.budget = int(config_parser["Default Values"]["budget"])

    def load_run_configuration():
        # parse the window size and movement
        settings.seed_window_size = int(config_parser["Execution"]["seed_window_size"])
        settings.seed_window_movement = int(config_parser["Execution"]["seed_window_movement"])

    def load_controller_configuration():
        # parse the controller configuration
        settings.minimal_behavior = config_parser["Controller"]["minimal_behavior"]
        settings.minimal_condition = config_parser["Controller"]["minimal_condition"]
        settings.random_parameter_initialization = config_parser["Controller"].getboolean(
            "random_parameter_initialization")
        # parse information related to the FSM
        settings.FSM_path_to_AutoMoDe = config_parser["FSM"]["path_to_AutoMoDe"]
        settings.FSM_max_states = int(config_parser["FSM"]["max_states"])
        settings.FSM_max_transitions = float(config_parser["FSM"]["max_transitions"])
        settings.FSM_max_transitions_per_state = int(config_parser["FSM"]["max_transitions_per_state"])
        settings.FSM_no_self_transition = config_parser["FSM"].getboolean("no_self_transition")
        # parse information related to the BT
        settings.BT_path_to_AutoMoDe = config_parser["BT"]["path_to_AutoMoDe"]
        settings.BT_max_actions = int(config_parser["BT"]["max_actions"])

    config_parser = configparser.ConfigParser()
    config_parser.read(config_file_name)
    load_default_values()
    load_run_configuration()
    load_controller_configuration()
    # parse logging configuration
    settings.snapshot_frequency = int(config_parser["Logging"]["snapshot_frequency"])
    settings.log_level = config_parser["Logging"]["log_level"]


def load_from_arguments(args):
    """
    Overrides parameters from the load_from_file method. Do not call without load_from_file.
    # TODO: Better docstring
    :param args:
    :return:
    """
    # config file (unneeded)
    settings.config_file_name = args["config_file_name"]
    # architecture
    settings.architecture = args["architecture"]
    # scenario
    # TODO: Implement failsafe (that is using config values if they don't exist from the cmd)
    settings.path_to_scenario = args["path_to_scenario"]
    # budget
    settings.budget = args["budget"]
    # initial_controller
    settings.initial_controller = args["initial_controller"]
    # job_name
    if args["job_name"] == settings.JOB_NAME_DEFAULT:
        settings.job_name = "{}-{}-{}-{}".format(args["architecture"],
                                                 # get the file name (os.path.split(...)[1])
                                                 # and the file without ending (split(".")[0])
                                                 os.path.split(args["path_to_scenario"])[1].split(".")[0],
                                                 args["budget"], args["initial_controller"])
    else:
        settings.job_name = args["job_name"]
    # result_directory
    settings.result_directory = args["result_directory"]
    # parallel
    # TODO: Implement parallel
    # TODO: Implement complete overriding of config


def set_parameters_fsm():
    """
    Sets the configuration parameters of the FSM module
    """
    # parameters for the FSM
    FSM.parameters["max_states"] = settings.FSM_max_states
    FSM.parameters["max_transitions"] = settings.FSM_max_transitions
    FSM.parameters["max_transitions_per_state"] = settings.FSM_max_transitions_per_state
    FSM.parameters["no_self_transition"] = settings.FSM_no_self_transition
    FSM.parameters["initial_state_behavior"] = settings.minimal_behavior
    FSM.parameters["random_parameter_initialization"] = settings.random_parameter_initialization


def set_parameters_bt():
    """
    Sets the configuration parameters of the BT module
    """
    # parameters for the BT
    BT.parameters["max_actions"] = settings.BT_max_actions
    BT.parameters["minimal_behavior"] = settings.minimal_behavior
    BT.parameters["minimal_condition"] = settings.minimal_condition
    BT.parameters["random_parameter_initialization"] = settings.random_parameter_initialization


def set_controller_parameters():
    """
    Sets the configuration parameters for the FSM and BT module
    """
    # Initialize all controller types
    set_parameters_fsm()
    set_parameters_bt()


def set_execution_parameters():
    """
    Sets the configuration parameters in the execution module
    """
    pass



def set_localsearch_parameters():
    """
    Sets the configuration parameters in the localsearch module
    """
    localsearch.utilities.initial_controller = settings.initial_controller
    localsearch.utilities.job_name = settings.job_name
    localsearch.utilities.result_directory = settings.result_directory
    localsearch.utilities.config_file_name = settings.config_file_name
    localsearch.localsearch.budget = settings.budget
    localsearch.localsearch.snapshot_frequency = settings.snapshot_frequency


def apply():
    """
    Applies the current settings. Unfortunately this is still necessary at the moment.
    # TODO: Somehow refactor this method away
    """
    level = logging.getLevelName(settings.log_level)
    logging.getLogger().setLevel(level)
    # TODO: Instead of setting here, let them look up
    set_controller_parameters()
    # set_execution_parameters()
    set_localsearch_parameters()
