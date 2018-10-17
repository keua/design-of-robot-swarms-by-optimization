from execution.factory import ExecutorFactory

# TODO: Maybe hide this? At least make it read only
mpi_enabled = False
budget = 0


def get_executor():
    return ExecutorFactory.get_executor()


def set_scenario(scenario_file):
    ExecutorFactory.set_scenario(scenario_file)


def set_seed_window(size, movement):
    ExecutorFactory.set_seed_window(size, movement)


def get_controller_type():
    return ExecutorFactory.get_executor().controller_type
