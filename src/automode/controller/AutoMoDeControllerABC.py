from abc import ABCMeta, abstractmethod
import statistics

#
use_mean = False  # if False then use the median

class AutoMoDeControllerABC:
    __metaclass__ = ABCMeta

    # Paths needed to evaluate the controller
    path_to_automode_executable = ""
    scenario_file = ""

    def __init__(self):
        self.score = float("inf")

    @abstractmethod
    def draw(self):
        pass

    @staticmethod
    @abstractmethod
    def parse_from_commandline_args(cmd_args):
        pass

    @abstractmethod
    def convert_to_commandline_args(self):
        pass

    @abstractmethod
    def evaluate_single_run(self, seed):
        pass

    def evaluate(self, seeds):
        #TODO: Fix this method and remove it from AutoMoDeFSM
        """Run this FSM in Argos and receive a score to compute the efficiency of the FSM"""
        scores = []
        for seed in seeds:
            if seed not in self.evaluated_instances:
                self.evaluated_instances[seed] = self.evaluate_single_run(seed)
            scores.append(self.evaluated_instances[seed])
        if use_mean:
            self.score = statistics.mean(scores)  # score / len(seeds)
        else:
            self.score = statistics.median(scores)
        return self.score

    @abstractmethod
    def mutate(self):
        pass
