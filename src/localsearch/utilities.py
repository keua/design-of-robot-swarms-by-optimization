import os
import logging
import shutil
from datetime import datetime

from automode.architecture import FSM, BT
import settings

SCORES_DIR = "scores/"
result_directory = "default/"
job_name = "LocalSearch"
config_file_name = "config.ini"
initial_controller = ""
src_directory = "/home/masterulb/masterthesis/localsearch/src/"  # TODO: Detect this?


def create_directory():
    logging.debug("Directory of this file {}".format(os.path.realpath(__file__)))
    # src_directory = os.path.split(os.path.realpath(__file__))[0]
    os.chdir(result_directory)
    str_time = datetime.now().strftime("%Y%m%d-%H:%M:%S")
    exp_dir = "{}_{}".format(job_name, str_time)
    os.mkdir(exp_dir)
    os.chdir(exp_dir)
    # copy the configuration file
    new_config_filename = "config_{}.ini".format(str_time)
    shutil.copyfile("{}/{}".format(
        src_directory, config_file_name), "{}/{}".format(os.getcwd(), new_config_filename))


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

def get_class( kls ):
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__( module )
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m