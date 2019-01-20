import numpy as np
import copy
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
        controller_candidate: candidate controller to start the local search.
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
                 controller_candidate=ls_utl.get_initial_controller(),
                 temperature=125.00,
                 cooling_rate=0.05,
                 final_temperature=0.00001,
                 iterations_per_temperature=10,
                 random_seed=None):
        """
        """
        self.controller_candidate = controller_candidate
        self.temperature = temperature
        self.cooling_rate = cooling_rate
        self.final_temperature = final_temperature
        self.iterations_per_temperature = iterations_per_temperature
        self.random_seed = random_seed
        self.termination_criterion = TerminationCriterion(
            self.temperature, self.final_temperature,
            self.cooling_rate, "discount")
        self.random_gen = np.random.seed(self.random_seed)
        self.metropolis_condition = ac.metropolis_condition
        self.executor = execution.get_executor()

    def perform_local_search(self, extra_tc=None):
        """
        """
        i = 0
        start_time = datetime.now()
        log.info(f'Started at {str(start_time)}')
        while True:
            temperature_constant = self.iterations_per_temperature
            current_temperature = self.temperature
            self.executor.create_seeds()  # Why?
            self.controller_candidate.evaluate()  # Why?
            while not self.termination_criterion.satisfied():
                # create a perturbed controller
                perturbed_controller = self._perform_perturbation(i)
                # evaluate both controllers on the seed_window
                self.controller_candidate.evaluate()
                perturbed_controller.evaluate()
                # Evaluating criterion
                criterion = \
                    self.metropolis_condition(self.controller_candidate.scores,
                                              perturbed_controller.scores,
                                              current_temperature,
                                              self.random_gen)
                # Updating controllers
                self.controller_candidate.agg_score = \
                    (criterion.type, criterion.best_outcome)
                perturbed_controller.agg_score = \
                    (criterion.type, criterion.perturb_outcome)
                log.debug(f'Candidate: {self.controller_candidate.scores},' +
                          f'Perturbed: {perturbed_controller.scores}')

                if criterion.acceptance:
                    perturbed_controller.draw(str(i))
                    self.controller_candidate = perturbed_controller

                # Applying cooling_rate
                if temperature_constant == 0:
                    current_temperature *= self.cooling_rate
                    temperature_constant = self.iterations_per_temperature
                temperature_constant -= 1
                i += 1
            if extra_tc is None or extra_tc.satisfied():
                break
        end_time = datetime.now()
        log.info(f'Finished at {str(end_time)}')
        log.info(f'Took {str(end_time - start_time)}')

        return self.controller_candidate

    def _perform_perturbation(self, i):
        """
        """
        perturbed_controller = copy.deepcopy(self.controller_candidate)
        # it is necessary to remove all evaluations from here
        perturbed_controller.evaluated_instances.clear()
        perturbed_controller.id = i
        perturbed_controller.perturb()

        return perturbed_controller
