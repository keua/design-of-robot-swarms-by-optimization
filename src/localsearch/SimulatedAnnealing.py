import copy
import json
import logging as log
import os
from datetime import datetime

import numpy as np

import execution
import localsearch.utilities as lsutl
import stats

from .AcceptanceCriterion import AcceptanceCriterion as AC
from .TerminationCriterion import DiscountTermination as DTC
from .TerminationCriterion import IterationTermination as ITC


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
        temperature_length: integer value indicating the number of 
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
            self.temperature_length = None
            self.random_seed = None
            self.acceptance_criterion = None
            self.budget = None
            self.__dict__ = data

    def __init__(self, candidate, temperature=125.00, cooling_rate=0.5,
                 final_temperature=0.0001, temperature_length=2,
                 acceptance_criterion="mean", random_seed=None, budget=5000,
                 termination_criterion=None):
        """
        """
        np.random.seed(random_seed)
        self.candidate = candidate
        self.best = candidate
        self.temperature = temperature
        self.cooling_rate = cooling_rate
        self.final_temperature = final_temperature
        self.temperature_length = temperature_length
        self.random_seed = random_seed
        self.random_gen = np.random
        self.exe = execution.ExecutorFactory.get_executor()
        self.acceptance = AC(accept=acceptance_criterion)
        self.mc = getattr(self.acceptance, "metropolis_condition")
        self.budget = budget
        self._outname = 'SA_%d' % random_seed
        self._establish_termination_criterion(termination_criterion)

    @classmethod
    def from_json(cls, data):
        """
        """
        sam = cls._SimulatedAnnealingModel(data)
        return cls(sam.candidate, sam.temperature, sam.cooling_rate,
                   sam.final_temperature, sam.temperature_length,
                   sam.acceptance_criterion, sam.random_seed, sam.budget)

    def local_search(self, snap_freq=100):
        """
        """
        self._get_candidate()
        stats.time.start_run()
        log.info('SA Started at {}'.format(stats.time.start_time))
        stats.performance.prepare_score_files(filename=self._outname)
        self.best = copy.deepcopy(self.candidate)
        temperature_length = self.temperature_length
        current_temperature = self.temperature
        while True:  # do
            log.debug('Current temperature {}'.format(current_temperature))
            # create a perturbed controller
            perturbed = self._perform_perturbation()
            # move the window
            self.exe.advance_seeds()
            # evaluate both controllers on the seed_window
            self.exe.evaluate_controller([self.candidate, perturbed])
            # Evaluating metropolis condition
            self.acceptance.set_scores(self.candidate.scores, perturbed.scores)
            mc_accept = self.mc(current_temperature, self.random_gen)
            self._update_agg_scores(perturbed)
            stats.performance.save_results(
                self.candidate, perturbed, self._outname)
            # If metropolis condition met select the new controller
            if mc_accept:
                self.candidate = perturbed
                # Evaluating acceptance criterion for global best controller
                self._evaluate_best()
            # Draw Best controller with certain frequency
            if self.tc.count % snap_freq == 0:
                self.candidate.draw('{}'.format(self.tc.count))
            # Constant temperature
            temperature_length -= 1
            self.tc.discount = 1.0
            # Applying cooling_rate
            if temperature_length == 0:
                current_temperature *= self.cooling_rate
                self.tc.discount = self.cooling_rate
                temperature_length = self.temperature_length

            if self.tc.satisfied():  # While
                break

        stats.time.end_run()
        log.info("Finished at {}".format(stats.time.end_time))
        log.info("Total time: {}".format(stats.time.elapsed_time()))
        log.info("Time in simulation: {}".format(stats.time.simulation_time))
        stats.save()
        stats.reset()

        return self.best

    def _perform_perturbation(self):
        """
        """
        perturbed = copy.deepcopy(self.candidate)
        # it is necessary to remove all evaluations from here
        perturbed.evaluated_instances.clear()
        perturbed.id = self.tc.count
        perturbed.perturb()

        return perturbed

    def _update_agg_scores(self, perturbed):
        """
        """
        log.debug('Candidate: {}, Perturbed: {}'.format(
                  self.candidate.scores, perturbed.scores))
        # Updating controllers
        self.candidate.agg_score = \
            (self.acceptance.name, self.acceptance.current_outcome)
        perturbed.agg_score = \
            (self.acceptance.name, self.acceptance.new_outcome)

    def _evaluate_best(self):
        """
        """
        log.debug('Exploring controller {}, Old controller {}'.format(
            self.acceptance.new_outcome, self.acceptance.current_outcome))
        self.acceptance.set_scores(self.best.scores, self.candidate.scores)
        if self.acceptance.accept():
            self.candidate.draw('{}'.format(self.tc.count))
            self.best = copy.deepcopy(self.candidate)
            log.info('New Best controller {}, Old controller {}'.format(
                self.acceptance.new_outcome, self.acceptance.current_outcome))

    def _get_candidate(self):
        """
        """
        if "" == self.candidate or isinstance(self.candidate, str):
            self.candidate = lsutl.get_initial_controller()
            self.exe.evaluate_controller([self.candidate])
        else:
            for key in self.candidate:
                algorithm = lsutl.get_class("localsearch.%s" % key)
                new = algorithm.from_json(self.candidate[key]).local_search()
                self.candidate = new

        log.debug('Initial candidate score %s' % str(self.candidate.agg_score))

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
