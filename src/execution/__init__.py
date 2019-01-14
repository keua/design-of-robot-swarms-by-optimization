from execution.automode_executor import SequentialExecutor

# TODO: Maybe hide this? At least make it read only
mpi_enabled = False
parallel = 0

_executor = None


def setup(path_to_AutoMoDe, scenario_file):
    global _executor
    if parallel == 0:  # no parallelization
        _executor = SequentialExecutor(path_to_AutoMoDe, scenario_file)


def evaluate_controller(controller):
    return _executor.evaluate_controller(controller)


def advance_seeds():
    _executor.advance_seeds()
