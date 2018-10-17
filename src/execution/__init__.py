from execution.factory import ExecutorFactory

# TODO: Maybe hide this? At least make it read only
mpi_enabled = False
budget = 0

# TODO: Hide this
_factory = ExecutorFactory()


def set_scenario(scenario_file):
    _factory.set_scenario(scenario_file)


def set_seed_window(size, movement):
    _factory.set_seed_window(size, movement)
