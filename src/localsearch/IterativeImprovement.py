import copy
import logging as log
import os
from datetime import datetime

import execution
import localsearch.utilities as lsutl
import settings
import stats

from . import acceptance_criteria as ac
from .AcceptanceCriterion import AcceptanceCriterion as AC
from .TerminationCriterion import IterationTermination as ITC


class IterativeImprovement(object):
    """
    """
    class _IterativeImprovementModel(object):
        """
        """

        def __init__(self, data):
            """
            """
            self.initial_controller = ""
            self.random_seed = None
            self.acceptance_criterion = "mean"
            self.budget = 5000
            self.termination_criterion = None
            self.__dict__.update(data)

    def __init__(self, candidate, acceptance_criterion, budget, random_seed,
                 termination_criterion):
        """
        The iterative improvement method, that improves upon the
        candidate controller.
        :param
            candidate: The controller that is used to first improve from
        :return
            The best controller after the iterative improvement
        """
        self.best = candidate
        self.acceptance = AC(accept=acceptance_criterion, improve=True)
        self.budget = budget
        self._exe = execution.ExecutorFactory.get_executor()
        self._outname = 'II_{}'.format(random_seed)
        self._establish_termination_criterion(termination_criterion)

    @classmethod
    def from_json(cls, data):
        """
        """
        iim = cls._IterativeImprovementModel(data)
        return cls(iim.initial_controller, iim.acceptance_criterion, iim.budget,
                   iim.random_seed, iim.termination_criterion)

    def local_search(self, snap_freq=100):
        """
        :return: The best controller after the iterative improvement
        """
        self.best = lsutl.get_initial_controller()
        log.debug('Initial candidate score {}'.format(self.best.agg_score))
        stats.time.start_run()
        log.info("Started at {}".format(stats.time.start_time))
        stats.performance.prepare_score_files(filename=self._outname)
        self._exe.evaluate_controller(self.best)
        log.debug("Initial best scores {}".format(self.best.scores))
        while True:
            # move the window
            self._exe.advance_seeds()
            # create a perturbed controller
            perturbed = self._perform_perturbation()
            # evaluate both controllers on the seed_window
            self._exe.evaluate_controllers([self.best, perturbed])
            # Evaluate criterion
            self.acceptance.set_scores(self.best.scores, perturbed.scores)
            accept = self.acceptance.accept()
            # save the scores to file and update controllers
            self._update_agg_scores(perturbed)
            stats.performance.save_results(self.best, perturbed, self._outname)
            if accept:
                log.debug(perturbed.perturb_history[-1])
                perturbed.draw('{}'.format(self.tc.count))
                log.info('New best {}, Old best {}'.format(
                    perturbed.agg_score, self.best.agg_score))
                self.best = perturbed

            if self.tc.count % snap_freq == 0:
                self.best.draw('{}'.format(self.tc.count))

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
        perturbed = copy.deepcopy(self.best)
        # it is necessary to remove all evaluations from here
        perturbed.evaluated_instances.clear()
        perturbed.id = self.tc.count
        perturbed.perturb()

        return perturbed

    def _update_agg_scores(self, perturbed):
        """
        """
        log.debug("Best scores {} and perturbed scores {}".
                  format(self.best.scores, perturbed.scores))
        self.best.agg_score, perturbed.agg_scores = self.acceptance.outcomes

    def _establish_termination_criterion(self, termination_criterion):
        """
        """
        if termination_criterion is None:
            if self.budget is not None:
                self.tc = ITC.from_budget(self.budget,
                                          self._exe.seed_window_size,
                                          self._exe.seed_window_move)
            else:
                self.tc = ITC(0, 50)
        else:
            self.tc = termination_criterion
