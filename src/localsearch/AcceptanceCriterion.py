from abc import ABCMeta, abstractmethod
import statistics as stats
import scipy.stats as scistats
import collections as coll
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
        self.current_outcome = stats.mean(self.current_scores)
        self.new_outcome = stats.mean(self.new_scores)
        self.name = self.mean.__name__
        return self.current_outcome <= self.new_outcome

    def median(self):
        """
        """
        self.new_outcome = stats.median(self.new_scores)
        self.current_outcome = stats.median(self.current_scores)
        self.name = self.median.__name__
        return self.current_outcome <= self.new_outcome

    def mode(self):
        """
        """
        self.new_outcome = stats.mode(self.new_scores)
        self.current_outcome = stats.mode(self.current_scores)
        self.name = self.mode.__name__
        return self.current_outcome <= self.new_outcome

    def sumc(self):
        """
        """
        self.new_outcome = sum(self.new_scores)
        self.current_outcome = sum(self.current_scores)
        self.name = self.sumc.__name__
        return self.current_outcome <= self.new_outcome

    def maxc(self):
        """
        """
        self.new_outcome = max(self.new_scores)
        self.current_outcome = max(self.current_scores)
        self.name = self.maxc.__name__
        self.current_outcome <= self.new_outcome

    def minc(self):
        """
        """
        self.new_outcome = min(self.new_scores)
        self.current_outcome = min(self.current_scores)
        self.name = self.minc.__name__
        return self.current_outcome <= self.new_outcome

    def tstudent_test(self, confidence=0.05):
        """
        """
        _, p = scistats.ttest_ind(self.current_scores, self.new_scores)
        self.new_outcome = stats.mean(self.new_scores)
        self.current_outcome = stats.mean(self.current_scores)
        self.name = f'{self.tstudent_test.__name__}_{str(confidence)}'
        return self.current_outcome <= self.new_outcome and p < confidence

    def wilcoxon_test(self, confidence=0.05):
        """
        """
        _, p = scistats.wilcoxon(self.current_scores, self.new_scores)
        self.new_outcome = stats.mean(self.new_scores)
        self.current_outcome = stats.mean(self.current_scores)
        self.name = f'{self.wilcoxon_test.__name__}_{str(confidence)}'
        return self.current_outcome <= self.new_outcome and p < confidence

    def metropolis_condition(self, t, random_gen):
        """
        """
        accept = self.accept()
        delta = self.new_outcome - self.current_outcome
        self.name = f'{self.metropolis_condition.__name__}_{self.accept.__name__}'
        return accept or random_gen.random() < np.exp((delta / t))

    def update(self, current_scores, new_scores):
        """
        """
        self.current_scores = current_scores
        self.new_scores = new_scores
