import os
import logging

from automode.architecture import FSM, BT
import settings

src_directory = "/home/kubedaar/masterthesis/localsearch/src/"  # TODO: Detect this?


def return_to_src_directory():
    """
    Move the cwd back to the src directory (for the next run of the LS)
    TODO: Find better naming here
    :return:
    """
    os.chdir(src_directory)


def get_controller_class():
    if settings.experiment["architecture"] == "FSM":
        return FSM
    elif settings.experiment["architecture"] == "BT":
        return BT
    else:
        logging.warning("WARNING: The specified type {} is not known.".format(settings.experiment["architecture"]))
        return None


def get_initial_controller():
    initial_controller = settings.experiment["initial_controller"]
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
