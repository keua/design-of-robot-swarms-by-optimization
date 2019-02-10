from abc import ABCMeta, abstractmethod

import numpy as np
import scipy.stats as scistats


class AcceptanceCriterion(object):
    """
    """

    def __init__(self, accept=None, strict=False, maximize=True):
        """
        """
        self.current_scores = None
        self.new_scores = None
        self.current_outcome = None
        self.new_outcome = None
        self.accept = self.mean if accept is None else getattr(self, accept)
        self.strict = strict
        self.maximize = maximize
        self.name = self.accept.__name__

    def mean(self):
        """
        """
        self.current_outcome = np.mean(self.current_scores)
        self.new_outcome = np.mean(self.new_scores)
        self.name = self.mean.__name__
        return self._op(self.current_outcome, self.new_outcome)

    def median(self):
        """
        """
        self.new_outcome = np.median(self.new_scores)
        self.current_outcome = np.median(self.current_scores)
        self.name = self.median.__name__
        return self._op(self.current_outcome, self.new_outcome)

    def mode(self):
        """
        """
        current_outcomes, _ = scistats.mode(self.current_scores)
        new_outcomes, _ = scistats.mode(self.new_scores)
        self.current_outcome = current_outcomes[0]
        self.new_outcome = new_outcomes[0]
        self.name = self.mode.__name__
        return self._op(self.current_outcome, self.new_outcome)

    def sum(self):
        """
        """
        self.new_outcome = np.sum(self.new_scores)
        self.current_outcome = np.sum(self.current_scores)
        self.name = self.sum.__name__
        return self._op(self.current_outcome, self.new_outcome)

    def max(self):
        """
        """
        self.new_outcome = np.max(self.new_scores)
        self.current_outcome = np.max(self.current_scores)
        self.name = self.max.__name__
        return self._op(self.current_outcome, self.new_outcome)

    def min(self):
        """
        """
        self.new_outcome = np.min(self.new_scores)
        self.current_outcome = np.min(self.current_scores)
        self.name = self.min.__name__
        return self._op(self.current_outcome, self.new_outcome)

    def t_student_test(self, confidence=0.05):
        """
        """
        _, p = scistats.ttest_ind(self.current_scores, self.new_scores)
        accept = self.mean()
        self.name = '{}_{}'.format(self.t_student_test.__name__, confidence)
        test = p < confidence
        return (accept and test) or (not accept and not test)

    def wilcoxon_test(self, confidence=0.05):
        """
        """
        _, p = scistats.wilcoxon(self.current_scores, self.new_scores)
        accept = self.mean()
        self.name = '{}_{}'.format(self.wilcoxon_test.__name__, confidence)
        test = p < confidence
        return (accept and test) or (not accept and not test)

    def metropolis_condition(self, t, random_gen):
        """
        """
        accept = self.accept()
        delta = self.new_outcome - self.current_outcome
        self.name = '{}_{}'.format(
            self.metropolis_condition.__name__, self.accept.__name__)
        return accept or random_gen.random() < np.exp((delta / t))

    def set_scores(self, current_scores, new_scores):
        """
        """
        self.current_scores = current_scores
        self.new_scores = new_scores

    @property
    def strict(self):
        return self._strict

    @strict.setter
    def strict(self, strict):
        self._strict = strict
        self._op = np.less if self._strict else np.less_equal

    @property
    def maximize(self):
        return self._maximize

    @maximize.setter
    def maximize(self, maximize):
        self._maximize = maximize
        if self.strict and self._maximize:
            self._op = np.less
        elif not self.strict and self._maximize:
            self._op = np.less_equal
        elif self.strict and not self._maximize:
            self._op = np.greater
        elif not self.strict and not self._maximize:
            self._op = np.greater_equal
