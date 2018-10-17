from execution.automode_executor import AutoMoDeExecutor


class ExecutorFactory:

    def __init__(self):
        self._executor = AutoMoDeExecutor()

    def get_executor(self):
        return self._executor

    def set_scenario(self, scenario):
        self._executor.scenario_file = scenario

    def set_seed_window(self, size, movement):
        self._executor.seed_window_size = size
        self._executor.seed_window_move = movement
        self._executor.create_seeds()
