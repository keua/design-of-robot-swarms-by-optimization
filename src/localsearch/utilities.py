import os
import logging
import shutil
from datetime import datetime

from automode.architecture import FSM, BT
import settings

result_directory = "default/"
job_name = "LocalSearch"
config_file_name = "config.ini"
initial_controller = ""
src_directory = "/home/jkuckling/AutoMoDe-LocalSearch/src/"  # TODO: Detect this?


def return_to_src_directory():
    """
    Move the cwd back to the src directory (for the next run of the LS)
    TODO: Find better naming here
    :return:
    """
    os.chdir(src_directory)


def get_controller_class():
    if settings.architecture == "FSM":
        return FSM
    elif settings.architecture == "BT":
        return BT
    else:
        logging.warning("WARNING: The specified type {} is not known.".format(settings.architecture))
        return None


def get_initial_controller():
    if initial_controller == "minimal":
        return get_controller_class()(minimal=True)
    else:
        controller_file, line = initial_controller.split(":")
        with open(controller_file, mode='r') as file:
            for i in range(0, int(line)):
                controller = file.readline()
        controller = controller.split(" ")
        return get_controller_class()().parse_from_commandline_args(controller)
