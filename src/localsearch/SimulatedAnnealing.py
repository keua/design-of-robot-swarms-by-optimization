import numpy as np
import copy
import os
import execution
import logging as log
import localsearch.utilities as ls_utl
from .TerminationCriterion import TerminationCriterion
from . import acceptance_criteria as ac
from datetime import datetime


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

    def __init__(self,
                 candidate,
                 temperature=125.00,
                 cooling_rate=0.5,
                 final_temperature=0.0001,
                 iterations_per_temperature=2,
                 acceptance_criterion=ac.mean,
                 random_seed=None):
        """
        """
        np.random.seed(random_seed)
        self.OUT_NAME = ls_utl.SCORES_DIR + f'SA_{random_seed}_best_score.csv'
        self.candidate = candidate
        self.incumbent = None
        self.temperature = temperature
        self.cooling_rate = cooling_rate
        self.final_temperature = final_temperature
        self.iterations_per_temperature = iterations_per_temperature
        self.random_seed = random_seed
        self.random_gen = np.random
        self.metropolis_condition = ac.metropolis_condition
        self.acceptance = acceptance_criterion
        self.executor = execution.get_executor()
        self.termination_criterion = TerminationCriterion(
            self.temperature, self.final_temperature, 1.0, "discount")

    def perform_local_search(self, snapshot_freq=10, extra_tc=None):
        """
        """
        i = 0
        start_time = datetime.now()
        log.warning(f'SA Started at {str(start_time)}')
        not os.path.isdir(ls_utl.SCORES_DIR) and os.mkdir(ls_utl.SCORES_DIR)
        out = open(self.OUT_NAME, "w")
        # If already evaluated do nothing else evaluate
        self.candidate.scores == float("inf") and self.candidate.evaluate()
        self.incumbent = copy.deepcopy(self.candidate)
        while True:  # do
            temperature_constant = self.iterations_per_temperature
            current_temperature = self.temperature
            self.executor.create_seeds()  # To avoid bias in certain seeds
            while True:  # do
                log.debug(f'Current temperature {current_temperature}')
                # create a perturbed controller
                perturbed = self._perform_perturbation(i)
                # move the window
                self.executor.advance_seeds()
                # evaluate both controllers on the seed_window
                self.candidate.evaluate()
                perturbed.evaluate()
                # Evaluating metropolis condition
                mc = self.metropolis_condition(self.candidate.scores,
                                               perturbed.scores,
                                               current_temperature,
                                               self.random_gen,
                                               self.acceptance)
                self._log_scores(perturbed, mc, out)
                # If metropolis condition met select the new controller
                if mc.acceptance:
                    self.candidate = perturbed
                    log.warning(f'Exploring controller {mc.perturb_outcome}' +
                                f', Old controller {mc.best_outcome}')
                    # Evaluating acceptance criterion for incumbent controller
                    self._evaluate_incumbent(i)
                # Draw Best controller with certain frequency
                i % snapshot_freq == 0 and self.candidate.draw(str(i))
                # Constant temperature
                temperature_constant -= 1
                self.termination_criterion.discount = 1.0
                # Applying cooling_rate
                if temperature_constant == 0:
                    current_temperature *= self.cooling_rate
                    self.termination_criterion.discount = self.cooling_rate
                    temperature_constant = self.iterations_per_temperature
                i += 1

                if self.termination_criterion.satisfied():  # While
                    break

            if extra_tc is None or extra_tc.satisfied():  # While
                break

        end_time = datetime.now()
        log.warning(f'Finished at {str(end_time)}')
        log.warning(f'Took {str(end_time - start_time)}')
        out.close()

        return self.incumbent

    def _perform_perturbation(self, i):
        """
        """
        perturbed = copy.deepcopy(self.candidate)
        # it is necessary to remove all evaluations from here
        perturbed.evaluated_instances.clear()
        perturbed.id = i
        perturbed.perturb()

        return perturbed

    def _log_scores(self, perturbed, criterion, file):
        """
        """
        log.debug(f'Candidate: {self.candidate.scores},' +
                  f'Perturbed: {perturbed.scores}')
        file.write(
            f'  {str(self.candidate.scores)}' +
            f', {criterion.type} = {str(criterion.best_outcome)}' +
            f', {str(perturbed.scores)}' +
            f', {criterion.type} = {str(criterion.perturb_outcome)}' +
            f', {perturbed.perturb_history[-1].__name__}' +
            f'\n')
        # Updating controllers
        self.candidate.agg_score = (criterion.type, criterion.best_outcome)
        perturbed.agg_score = (criterion.type, criterion.perturb_outcome)

    def _evaluate_incumbent(self, i):
        """
        """
        criterion = self.acceptance(self.incumbent.scores, self.candidate.scores)
        if criterion.acceptance:
            self.candidate.draw(str(i))
            self.incumbent = copy.deepcopy(self.candidate)
            log.warning(f'New incumbent {criterion.perturb_outcome}' +
                        f', Old controller {criterion.best_outcome}')
