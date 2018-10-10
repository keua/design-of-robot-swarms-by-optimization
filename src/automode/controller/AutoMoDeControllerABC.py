from abc import ABCMeta, abstractmethod
from execution import AutoMoDeExecutor
import random
from config import configuration
from logging.simple_logging import SimpleLogger

class AutoMoDeControllerABC:
    __metaclass__ = ABCMeta

    def __init__(self):
        self.score = float("inf")
        # parameters used to keep track of the local search
        self.mut_history = []
        self.evaluated_instances = {}

        if configuration.Configuration.instance.initial_controller == "minimal":
            self.create_minimal_controller()

        self.id = -1

    @abstractmethod
    def create_minimal_controller(self):
        pass

    @abstractmethod
    def draw(self, graph_name):
        pass

    @staticmethod
    @abstractmethod
    def parse_from_commandline_args(cmd_args):
        pass

    @abstractmethod
    def convert_to_commandline_args(self):
        pass

    def evaluate(self, seeds):
        """Run this FSM in Argos and receive a score to compute the efficiency of the FSM"""
        return AutoMoDeExecutor.instance.evaluate_controller(self, seeds)

    def get_mutation_operators(self):
        """Returns all methods that start with mut_ indicating that they are indeed mutation operators."""
        method_names = [method_name for method_name in dir(self) if callable(getattr(self, method_name)) and method_name.startswith("mut_")]
        methods = [getattr(self, x) for x in method_names]
        return methods

    def mutate(self):
        """
        Apply a random mutation operator to this controller.

        In order for this to work, all possible mutation operators need to start with mut_
        """
        mutation_operators = self.get_mutation_operators()
        while mutation_operators:
            mutation_operator = random.choice(mutation_operators)
            # execute mutation
            result = mutation_operator()
            # remove operator from list so it is not chosen again if it failed
            mutation_operators.remove(mutation_operator)
            if result:
                self.mut_history.append(mutation_operator)
                return
        # We cannot apply any operator -> how can this even happen?
        SimpleLogger.instance.log_error("A critical error appeared. We cannot apply any mutation at his point.")
