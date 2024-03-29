__author__ = "Keneth Ubeda, k3n3th@gmail.com"
import copy
import json
import logging as log
import os
from datetime import datetime

import numpy as np

import execution
import localsearch.utilities as lsutl
import settings
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
            self.candidate = ""
            self.temperature = 125.0
            self.cooling_rate = 0.5
            self.final_temperature = 0.0001
            self.temperature_length = 3
            self.random_seed = None
            self.acceptance_criterion = "mean"
            self.budget = 5000
            self.restart_mechanism = "temperature"
            self.restart_percentage = 0.01/100
            self.termination_criterion = None
            self.__dict__.update(data)

    def __init__(self, candidate, temperature=125.0, cooling_rate=0.5,
                 final_temperature=0.0001, temperature_length=3,
                 acceptance_criterion="mean", random_seed=None, budget=5000,
                 restart_mechanism="temperature",
                 restart_percentage=0.01/100, termination_criterion=None):
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
        self.acceptance = AC(accept=acceptance_criterion)
        self.budget = budget
        self.restart_mechanism = restart_mechanism
        self.restart_percentage = restart_percentage
        self._current_temperature = self.temperature
        self._best_temperature = (self.temperature, 0)
        self._exe = execution.ExecutorFactory.get_executor()
        self._mc = getattr(self.acceptance, "metropolis_condition")
        self._f_best_cand = 'SA_BC_{}'.format(random_seed)
        self._f_cand_pert = 'SA_CP_{}'.format(random_seed)
        self._establish_termination_criterion(termination_criterion)

    @classmethod
    def from_json(cls, data):
        """
        """
        sam = cls._SimulatedAnnealingModel(data)
        return cls(sam.candidate, sam.temperature, sam.cooling_rate,
                   sam.final_temperature, sam.temperature_length,
                   sam.acceptance_criterion, sam.random_seed, sam.budget,
                   sam.restart_mechanism, sam.restart_percentage,
                   sam.termination_criterion)

    def local_search(self, snap_freq=100):
        """
        """
        stats.time.start_run()
        stats.performance.prepare_score_files(filename=self._f_best_cand)
        stats.performance.prepare_score_files(filename=self._f_cand_pert)
        self._get_candidate()
        log.info('SA Started at {}'.format(stats.time.start_time))
        self.best = copy.deepcopy(self.candidate)
        temperature_length = self.temperature_length
        while True:  # do
            log.debug('Current temperature {}'.format(
                self._current_temperature))
            # create a perturbed controller
            perturbed = self._perform_perturbation()
            # move the window
            self._exe.advance_seeds()
            # evaluate both controllers on the seed_window
            self._exe.evaluate_controllers([self.candidate, perturbed])
            # Evaluating metropolis condition
            self.acceptance.set_scores(self.candidate.scores, perturbed.scores)
            mc_accept = self._mc(self._current_temperature, self.random_gen)
            self._update_agg_scores(perturbed)
            # Save candidate and perturbed controllers interaction
            stats.performance.save_results(
                self.candidate, perturbed, self._f_cand_pert)
            # Save temporal variable for stats purposes
            oldbest = self.best
            # If metropolis condition met select the new controller
            if mc_accept:
                self.candidate = perturbed
            # Evaluating improvement for global best controller
            oldbest = self._evaluate_improvement(mc_accept, snap_freq)
            # Save best and candidate controllers interaction
            stats.performance.save_results(
                oldbest, self.candidate, self._f_best_cand)
            # Draw Best controller with certain frequency
            if snap_freq is not None and self.tc.count % snap_freq == 0:
                self.candidate.draw('{}'.format(self.tc.count))
            # Constant temperature
            temperature_length -= 1
            self.tc.discount = 1.0
            # Applying cooling_rate
            if temperature_length == 0:
                self._current_temperature *= self.cooling_rate
                self.tc.discount = self.cooling_rate
                temperature_length = self.temperature_length
            # Check temperature percentage
            if self._restart():
                self.candidate = copy.deepcopy(self.best)
                temperature_length = self.temperature_length
                self._current_temperature = self.temperature
                log.info("Restarting score %s" % str(self.candidate.agg_score))

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
        self.candidate.agg_score, perturbed.agg_score = self.acceptance.outcomes

    def _evaluate_improvement(self, mc_accept, snap_freq):
        """
        """
        log.debug('Exploring controller {}, Old controller {}'.format(
            self.acceptance.new_outcome, self.acceptance.current_outcome))
        # Evaluate the current best in the current seeds
        self._exe.evaluate_controller(self.best)
        oldbest = self.best
        self.acceptance.improve = True
        self.acceptance.set_scores(self.best.scores, self.candidate.scores)
        accept = self.acceptance.accept()
        self.best.agg_score, self.candidate.agg_score = self.acceptance.outcomes
        if accept:
            snap_freq is not None and self.candidate.draw('{}'.format(self.tc.count))
            log.info('New Best controller {}, Old controller {}'.format(
                self.candidate.agg_score, self.best.agg_score))
            self.best = copy.deepcopy(self.candidate)
        self.acceptance.improve = False
        if mc_accept:
            d = self.best.agg_score[1] - oldbest.agg_score[1]
            if d > self._best_temperature[1]:
                self._best_temperature = (self._current_temperature, d)
        return oldbest

    def _get_candidate(self):
        """
        """
        log.info('SA Getting candidate at {}'.format(stats.time.start_time))
        if "" == self.candidate or isinstance(self.candidate, str):
            self.candidate = lsutl.get_initial_controller()
            self._exe.evaluate_controller(self.candidate)
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
                                          self._exe.seed_window_size,
                                          self._exe.seed_window_move)
            else:
                self.tc = DTC(self.temperature, self.final_temperature, 1.0)
        else:
            self.tc = termination_criterion

    def _restart(self):
        """
        """
        if self.restart_mechanism == "temperature":
            restart_temperature = self.temperature * self.restart_percentage
            return False if self._current_temperature > restart_temperature else True
        elif self.restart_mechanism == "run":
            restart_step = int(self.tc.end * self.restart_percentage)
            return True if self.tc.count + 1 == restart_step else False
        elif self.restart_mechanism == "reheat":
            restart_temperature = self.temperature * self.restart_percentage
            print(self._best_temperature, self._current_temperature, self.restart_percentage, restart_temperature) 
            if self._current_temperature <= restart_temperature:
                self.temperature = self._best_temperature[0]
                return True
        return False
