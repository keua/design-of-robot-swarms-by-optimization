from abc import ABCMeta, abstractmethod
import random
import logging

import execution


class AutoMoDeArchitectureABC:
    __metaclass__ = ABCMeta

    def __init__(self, minimal=False):
        self.scores = []  # this will be a list of tuples (seed, score)
        self.agg_score = ("type", float("inf"))  # the aggregated score with respect to the fitness function, useful for short debugging
        # parameters used to keep track of the local search
        self.perturb_history = []  # a list of all applied operators -> TODO: transform this into a list of strings
        self.evaluated_instances = {}  # a dictionary with keys of seeds and entries are the scores
        self.executor = execution.get_executor()  # the executor, don't know if it really is needed here

        if minimal:
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

    def evaluate(self):
        """Run this FSM in Argos and receive a score to compute the efficiency of the FSM"""
        return self.executor.evaluate_controller(self)

    def get_perturbation_operators(self):
        """Returns all methods that start with perturb_ indicating that they are indeed perturbation operators."""
        method_names = [method_name for method_name in dir(self)
                        if callable(getattr(self, method_name)) and method_name.startswith("perturb_")]
        methods = [getattr(self, x) for x in method_names]
        return methods

    def perturb(self):
        """
        Apply a random perturbation operator to this controller.

        In order for this to work, all possible perturbation operators need to start with perturb_
        """
        perturbation_operators = self.get_perturbation_operators()
        while perturbation_operators:
            perturbation_operator = random.choice(perturbation_operators)
            # execute perturbation
            result = perturbation_operator()
            # remove operator from list so it is not chosen again if it failed
            perturbation_operators.remove(perturbation_operator)
            if result:
                self.perturb_history.append(perturbation_operator)
                return
        # We cannot apply any operator -> how can this even happen?
        logging.error("A critical error appeared. We cannot apply any perturbation at his point.")
