import os
from datetime import datetime
from automode.controller import FSM, BT
import shutil
from config.configuration import Configuration
import localsearch_setup
from simple_logging.simple_logging import SimpleLogger
from localsearch import iterative_improvement

"""
    The main.py script can be called from various sources to start a local search.
    It guarantees that all necessary resources are always created.
"""


def run_local_search(controller):
    return iterative_improvement(controller)


def create_directory():
    SimpleLogger.instance.log_debug("Directory of this file {}".format(os.path.realpath(__file__)))
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


def get_controller_class():
    if Configuration.instance.controller_type == "FSM":
        return FSM
    elif Configuration.instance.controller_type == "BT":
        return BT
    else:
        SimpleLogger.instance.log_warning("WARNING: The specified type {} is not known.".format(Configuration.instance.controller_type))
        return None


def automode_localsearch():
    localsearch_setup.setup_localsearch()
    create_directory()
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
    initial_controller = Configuration.instance.initial_controller
    initial_controller.draw("initial")
    result = run_local_search(initial_controller)
    result.draw("final")
    SimpleLogger.instance.log(result.convert_to_commandline_args())


# print(__name__)
if __name__ == "__main__":
    automode_localsearch()

if __name__ == "__worker__":
    SimpleLogger()
