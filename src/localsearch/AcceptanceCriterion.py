from abc import ABCMeta, abstractmethod
import scipy.stats as scistats
import numpy as np


class AcceptanceCriterion(object):
    """
    """
    __metaclass__ = ABCMeta

    def __init__(self, current_scores=None, new_scores=None, accept=None):
        """
        """
        self.current_scores = current_scores
        self.new_scores = new_scores
        self.current_outcome = None
        self.new_outcome = None
        self.name = None
        self.accept = self.mean if accept is None else getattr(self, accept)

    def mean(self):
        """
        """
        self.current_outcome = np.mean(self.current_scores)
        self.new_outcome = np.mean(self.new_scores)
        self.name = self.mean.__name__
        return self.current_outcome <= self.new_outcome

    def median(self):
        """
        """
        self.new_outcome = np.median(self.new_scores)
        self.current_outcome = np.median(self.current_scores)
        self.name = self.median.__name__
        return self.current_outcome <= self.new_outcome

    def mode(self):
        """
        """
        current_outcomes, _ = scistats.mode(self.current_scores)
        new_outcomes, _ = scistats.mode(self.new_scores)
        self.current_outcome = current_outcomes[0]
        self.new_outcome = new_outcomes[0]
        self.name = self.mode.__name__
        return self.current_outcome <= self.new_outcome

    def sum(self):
        """
        """
        self.new_outcome = np.sum(self.new_scores)
        self.current_outcome = np.sum(self.current_scores)
        self.name = self.sum.__name__
        return self.current_outcome <= self.new_outcome

    def max(self):
        """
        """
        self.new_outcome = np.max(self.new_scores)
        self.current_outcome = np.max(self.current_scores)
        self.name = self.max.__name__
        return self.current_outcome <= self.new_outcome

    def min(self):
        """
        """
        self.new_outcome = np.min(self.new_scores)
        self.current_outcome = np.min(self.current_scores)
        self.name = self.min.__name__
        return self.current_outcome <= self.new_outcome

    def t_student_test(self, confidence=0.05):
        """
        """
        _, p = scistats.ttest_ind(self.current_scores, self.new_scores)
        self.new_outcome = np.mean(self.new_scores)
        self.current_outcome = np.mean(self.current_scores)
        self.name = '{}_{}'.format(self.t_student_test.__name__, confidence)
        return self.current_outcome <= self.new_outcome and p < confidence

    def wilcoxon_test(self, confidence=0.05):
        """
        """
        _, p = scistats.wilcoxon(self.current_scores, self.new_scores)
        self.new_outcome = np.mean(self.new_scores)
        self.current_outcome = np.mean(self.current_scores)
        self.name = '{}_{}'.format(self.wilcoxon_test.__name__, confidence)
        return self.current_outcome <= self.new_outcome and p < confidence

    def metropolis_condition(self, t, random_gen):
        """
        """
        accept = self.accept()
        delta = self.new_outcome - self.current_outcome
        self.name = '{}_{}'.format(self.metropolis_condition.__name__,
                                   self.accept.__name__)
        return accept or random_gen.random() < np.exp((delta / t))

    def set_scores(self, current_scores, new_scores):
        """
        """
        self.current_scores = current_scores
        self.new_scores = new_scores
