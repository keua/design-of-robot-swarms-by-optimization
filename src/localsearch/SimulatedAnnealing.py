import numpy as np
import copy
import os
import json
import execution
import logging as log
import localsearch.utilities as ls_utl
from .TerminationCriterion import DiscountTermination as DTC
from .TerminationCriterion import IterationTermination as ITC
from .AcceptanceCriterion import AcceptanceCriterion as AC
from datetime import datetime
from localsearch import iterative_improvement as ii


class SimulatedAnnealing(object):
    """
    Simulated Annealing (SA) algorithm implementation for stochastic local
    search. Specifically we are looking for the best controller that optimize
    the performance of a robot swarm on a specific task.
    The SA algorithm is inspired in the real annealing process of metal, in
    which atoms of metals move freely with respect to each other at high
    temperatures. But as the temperature goes down the atoms start to get
    ordered and forms crystal depends on cooling rate. In the optimization
    context the SA is an algorithm that allow us to escape from local optima
    into global optima for its capacity of accepting worse solutions with 
    certain probability when the computational temperature is high.
    This algorithm poses a set of parameters that can changed according to the
    needs of the problem. The parameters are: initial temperature, cooling rate,
    final temperature and the number of iterations to keep the same temperature.


    Attributes:
        candidate: candidate controller to start the local search.
        temperature: float value indicating the temperature to start the
        annealing process.
        cooling_rate: float value indicating the decreasing rate of temperature 
        in time.
        final_temperature: float value indicating the end of the annealing 
        process.
        iterations_per_temperature: integer value indicating the number of 
        iterations during the cooling process in which the same temperature
        will be used.
        random_seed: integer value to initialize the random generator.
        termination_criterion: indicates when the algorithm will stop.
    """

    class _SimulatedAnnealingModel(object):
        """
        """

        def __init__(self, data):
            """ 
            """
            self.candidate = None
            self.temperature = None
            self.cooling_rate = None
            self.final_temperature = None
            self.iterations_per_temperature = None
            self.random_seed = None
            self.acceptance_criterion = None
            self.budget = None
            self.__dict__ = data

    def __init__(self, candidate, temperature=125.00, cooling_rate=0.5,
                 final_temperature=0.0001, iterations_per_temperature=2,
                 acceptance_criterion="mean", random_seed=None, budget=5000,
                 termination_criterion=None):
        """
        """
        np.random.seed(random_seed)
        self.OUT_NAME = ls_utl.SCORES_DIR + 'SA_%d_best_score.csv' % random_seed
        not os.path.isdir(ls_utl.SCORES_DIR) and os.mkdir(ls_utl.SCORES_DIR)
        self.candidate = candidate
        self.incumbent = None
        self.temperature = temperature
        self.cooling_rate = cooling_rate
        self.final_temperature = final_temperature
        self.iterations_per_temperature = iterations_per_temperature
        self.random_seed = random_seed
        self.random_gen = np.random
        self.exe = execution.get_executor()
        self.acceptance = AC(accept=acceptance_criterion)
        self.mc = getattr(self.acceptance, "metropolis_condition")
        self.budget = budget
        self._establish_termination_criterion(termination_criterion)

    @classmethod
    def from_json(cls, data):
        """
        """
        sam = cls._SimulatedAnnealingModel(data)
        return cls(sam.candidate, sam.temperature, sam.cooling_rate,
                   sam.final_temperature, sam.iterations_per_temperature,
                   sam.acceptance_criterion, sam.random_seed, sam.budget)

    def local_search(self, snap_freq=10):
        """
        """
        # isinstance(self.candidate, str) and
        self._get_candidate()
        start_time = datetime.now()
        log.warning('SA Started at {}'.format(start_time))
        out = open(self.OUT_NAME, "w")
        # If already evaluated do nothing else evaluate
        self.candidate.scores == float("inf") and self.candidate.evaluate()
        self.incumbent = copy.deepcopy(self.candidate)
        temperature_constant = self.iterations_per_temperature
        current_temperature = self.temperature
        self.exe.create_seeds()  # To avoid bias in certain seeds
        while True:  # do
            log.debug('Current temperature {}'.format(current_temperature))
            # create a perturbed controller
            perturbed = self._perform_perturbation()
            # move the window
            self.exe.advance_seeds()
            # evaluate both controllers on the seed_window
            not self.tc.count == 0 and self.candidate.evaluate()
            perturbed.evaluate()
            # Evaluating metropolis condition
            self.acceptance.set_scores(self.candidate.scores, perturbed.scores)
            mc_accept = self.mc(current_temperature, self.random_gen)
            self._log_scores(perturbed, out)
            # If metropolis condition met select the new controller
            if mc_accept:
                self.candidate = perturbed
                # Evaluating acceptance criterion for incumbent controller
                self._evaluate_incumbent()
            # Draw Best controller with certain frequency
            if self.tc.count % snap_freq == 0:
                self.candidate.draw(str(self.tc.count))
            # Constant temperature
            temperature_constant -= 1
            self.tc.discount = 1.0
            # Applying cooling_rate
            if temperature_constant == 0:
                current_temperature *= self.cooling_rate
                self.tc.discount = self.cooling_rate
                temperature_constant = self.iterations_per_temperature

            if self.tc.satisfied():  # While
                break

        end_time = datetime.now()
        log.warning('Finished at {}'.format(end_time))
        log.warning('Took {}'.format(end_time - start_time))
        out.close()

        return self.incumbent

    def _perform_perturbation(self):
        """
        """
        perturbed = copy.deepcopy(self.candidate)
        # it is necessary to remove all evaluations from here
        perturbed.evaluated_instances.clear()
        perturbed.id = self.tc.count
        perturbed.perturb()

        return perturbed

    def _log_scores(self, perturbed, file):
        """
        """
        log.debug('Candidate: {}, Perturbed: {}'.format(
                  self.candidate.scores, perturbed.scores))
        file.write('{}, {}={}, {}, {}={}, {} \n'.format(
            self.candidate.scores,
            self.acceptance.name, self.acceptance.current_outcome,
            perturbed.scores,
            self.acceptance.name, self.acceptance.new_outcome,
            perturbed.perturb_history[-1].__name__)
        )
        # Updating controllers
        self.candidate.agg_score = \
            (self.acceptance.name, self.acceptance.current_outcome)
        perturbed.agg_score = \
            (self.acceptance.name, self.acceptance.new_outcome)

    def _evaluate_incumbent(self):
        """
        """
        log.warning('Exploring controller {}, Old controller {}'.format(
            self.acceptance.new_outcome, self.acceptance.current_outcome))
        self.acceptance.set_scores(
            self.incumbent.scores, self.candidate.scores)
        if self.acceptance.accept():
            self.candidate.draw(str(self.tc.count))
            self.incumbent = copy.deepcopy(self.candidate)
            log.warning('New incumbent {}, Old controller {}'.format(
                self.acceptance.new_outcome, self.acceptance.current_outcome))

    def _get_candidate(self):
        """
        """
        initial_controller = ls_utl.get_initial_controller()

        if "" == self.candidate or "minimal" == self.candidate:
            self.candidate = initial_controller
        else:
            for key in self.candidate:
                algorithm = ls_utl.get_class("localsearch.%s" % key)
                new = algorithm.from_json(self.candidate[key]).local_search()
                self.candidate = new

        log.warning('Initial candidate score {}'.
                    format(self.candidate.agg_score))

    def _establish_termination_criterion(self, termination_criterion):
        """
        """
        if termination_criterion is None:
            if self.budget is not None:
                self.tc = ITC.from_budget(self.budget,
                                          self.exe.seed_window_size,
                                          self.exe.seed_window_move)
            else:
                self.tc = DTC(self.temperature, self.final_temperature, 1.0)
        else:
            self.tc = termination_criterion
