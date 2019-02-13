"""
This module provides functions for setting up the configuration of the local search
"""

import logging
import json

from automode.architecture import FSM
from automode.architecture import BT

import localsearch.utilities
import settings


def load_from_file(file_name):
    """
    Reads a JSON formatted file and sets the data in settings.py.
    Warning! This method does not yet support recursive loading of dictionaries.
    :param file_name:
    :return:
    """
    with open(file_name) as f:
        data = json.load(f)
    # check if other files need to be loaded
    if "include_files" in data:
        for include_file_name in data["include_files"]:
            logging.debug("Including configuration file {}".format(include_file_name))
            # TODO: This should rather be a recursive call to load_from_file and
            #  also do a recursive merge of the dictionary
            with open(include_file_name) as include_file:
                included_data = json.load(include_file)
            data.update(included_data)
    return data


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


def set_localsearch_parameters():
    """
    Sets the configuration parameters in the localsearch module
    """
    localsearch.utilities.initial_controller = settings.initial_controller
    localsearch.utilities.job_name = settings.job_name
    localsearch.utilities.result_directory = settings.result_directory
    localsearch.utilities.config_file_name = settings.config_file_name


def apply(configuration):
    """
    Applies the current settings. Unfortunately this is still necessary at the moment.
    """
    level = logging.getLevelName(configuration["logging"]["log_level"])
    logging.getLogger().setLevel(level)
    # apply the configuration
    for key in configuration:
        setattr(settings, key, configuration[key])


def write_to_file(configuration, file_name):
    """

    :param configuration:
    :param file_name:
    :return:
    """
    with open(file_name, 'w') as f:
        json.dump(configuration, f)


def write_settings_to_file(file_name):
    settings_list = dir(settings)
    settings_list = [x for x in settings_list if isinstance(getattr(settings, x), dict) and not x.startswith("__")]
    data = {}
    for setting in settings_list:
        data[setting] = getattr(settings, setting)
    write_to_file(data, file_name)
