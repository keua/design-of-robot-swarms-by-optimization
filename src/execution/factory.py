from execution.automode_executor import AutoMoDeExecutor


class ExecutorFactory:

    _instance = None

    def __init__(self):
        self._executor = AutoMoDeExecutor()
        ExecutorFactory._instance = self

    @staticmethod
    def get_executor():
        return ExecutorFactory._instance._executor

    @staticmethod
    def set_scenario(scenario):
        ExecutorFactory._instance.scenario_file = scenario

    @staticmethod
    def set_seed_window(size, movement):
        ExecutorFactory._instance._executor.seed_window_size = size
        ExecutorFactory._instance._executor.seed_window_move = movement
        ExecutorFactory._instance._executor.create_seeds()


if ExecutorFactory._instance is None:
    ExecutorFactory()
