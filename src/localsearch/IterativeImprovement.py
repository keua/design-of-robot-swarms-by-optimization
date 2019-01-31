from datetime import datetime
import os
import copy
import logging as log
import execution

import localsearch.utilities as ls_utl
from . import acceptance_criteria as ac
from .TerminationCriterion import IterationTermination as ITC
from .AcceptanceCriterion import AcceptanceCriterion as AC


class IterativeImprovement(object):
    """
    """
    class _IterativeImprovementModel(object):
        """
        """

        def __init__(self, data):
            """ 
            """
            self.initial_controller = None
            self.random_seed = None
            self.acceptance_criterion = None
            self.budget = None
            self.__dict__ = data

    def __init__(self, candidate, acceptance_criterion="mean", budget=5000,
                 termination_criterion=None):
        """
        The iterative improvement method, that improves upon the
        candidate controller.
        :param 
            candidate: The controller that is used to first improve from
        :return
            The best controller after the iterative improvement
        """
        self.OUT_NAME = ls_utl.SCORES_DIR + f'II_{budget}_best_score.csv'
        not os.path.isdir(ls_utl.SCORES_DIR) and os.mkdir(ls_utl.SCORES_DIR)
        self.best = candidate
        self.exe = execution.get_executor()
        self.acceptance = AC(accept=acceptance_criterion)
        self.budget = budget
        self._establish_termination_criterion(termination_criterion)

    @classmethod
    def from_json(cls, data):
        """
        """
        iim = cls._IterativeImprovementModel(data)
        return cls(iim.initial_controller, iim.acceptance_criterion, iim.budget)

    def local_search(self, snap_freq=10):
        """
        :return: The best controller after the iterative improvement
        """
        isinstance(self.best, str) and self._get_best()
        start_time = datetime.now()
        log.warning(f"Started at {str(start_time)}")
        with open(self.OUT_NAME, "w") as file:
            self.exe.create_seeds()
            self.best.evaluate()
            log.debug(f"Initial best scores {str(self.best.scores)}")
            while True:
                # move the window
                self.exe.advance_seeds()
                # create a perturbed controller
                perturbed = self._perform_perturbation()
                # evaluate both controllers on the seed_window
                self.best.evaluate()
                perturbed.evaluate()
                # Evaluate criterion
                self.acceptance.set_scores(self.best.scores, perturbed.scores)
                c_accept = self.acceptance.accept()
                # save the scores to file and update controllers
                self._log_scores(perturbed, file)

                if c_accept:
                    log.debug(perturbed.perturb_history[-1].__name__)
                    perturbed.draw(str(self.tc.count))
                    log.warning(f'New best {perturbed.agg_score}' +
                                f', Old best {self.best.agg_score}')
                    self.best = perturbed

                if self.tc.count % snap_freq == 0:
                    self.best.draw(str(self.tc.count))

                if self.tc.satisfied():  # While
                    break

            end_time = datetime.now()

        log.warning(f"Finished at {str(end_time)}")
        time_diff = end_time - start_time
        log.warning(f"Took {str(time_diff)}")

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

    def _log_scores(self, perturbed, file):
        """
        """
        self.best.agg_score = \
            (self.acceptance.name, self.acceptance.current_outcome)
        perturbed.agg_score = \
            (self.acceptance.name, self.acceptance.new_outcome)
        file.write(
            f"{str(self.best.scores)}" +
            f', {self.acceptance.name}={str(self.acceptance.current_outcome)}' +
            f", {str(perturbed.scores)}" +
            f', {self.acceptance.name}={str(self.acceptance.new_outcome)}' +
            f", {perturbed.perturb_history[-1].__name__}" +
            f"\n"
        )
        log.debug(
            f"Best score {str(self.best.scores)}" +
            f" and new score {str(perturbed.scores)}"
        )

    def _get_best(self):
        """
        """
        initial_controller = ls_utl.get_initial_controller()

        if "" == self.best or "minimal" == self.best:
            self.best = initial_controller
        else:
            self.best = initial_controller
        log.warning(f'Initial candidate score {self.best.agg_score}')

    def _establish_termination_criterion(self, termination_criterion):
        """
        """
        if termination_criterion is None:
            if self.budget is not None:
                self.tc = ITC.from_budget(self.budget,
                                        self.exe.seed_window_size,
                                        self.exe.seed_window_move)
            else:
                self.tc = ITC(0, 50)
        else:
            self.tc = termination_criterion