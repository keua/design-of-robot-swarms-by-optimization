__author__ = "Jonas Kuckling, jonas.kuckling@ulb.ac.be"
"""
This module provides functions for setting up the configuration of the local search
"""

import logging
import json
import os

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
            # TODO: maybe include checks against circular imports
            included_data = load_from_file(include_file_name)
            # TODO: maybe make this a recursive update
            data.update(included_data)
    return data


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

def update_dirs(data):
    """
    """
    if 'dirs' in data:
        data["dirs"]["resdir"] = os.environ[data["dirs"]["resdir"]]
        data["dirs"]["srcdir"] = os.environ[data["dirs"]["srcdir"]]

def update_path_automode(data):
    """
    """
    if data["experiment"]["architecture"] == "BT":
        data["BT"]["path_to_AutoMoDe"] = \
            data["dirs"]["srcdir"] + data["BT"]["path_to_AutoMoDe"]
    elif data["experiment"]["architecture"] == "FSM":
        data["FSM"]["path_to_AutoMoDe"] = \
            data["dirs"]["srcdir"] + data["FSM"]["path_to_AutoMoDe"]
    data["cwd"]["dir"] = data["dirs"]["srcdir"] + data["cwd"]["dir"]

def update_path_experiment(args, data):
    """
    """
    args["result_directory"] = data["dirs"]["resdir"] + args["result_directory"]
    args["scenario_file"] = data["dirs"]["srcdir"] + args["scenario_file"]