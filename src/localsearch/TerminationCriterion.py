__author__ = "Keneth Ubeda, k3n3th@gmail.com"
import math
import time as tm
from abc import ABCMeta, abstractmethod


class TerminationCriterion(object):
    """
    """
    __metaclass__ = ABCMeta

    def __init__(self, start, end):
        """
        """
        self.start = start
        self.end = end
        self.count = 0
        self.status = False

    @abstractmethod
    def satisfied(self):
        raise NotImplementedError("Subclass must implement abstract method")


class TimeTermination(TerminationCriterion):
    """
    """

    def satisfied(self):
        self.count += 1
        self.status = tm.time() > self.start + self.end * 60
        return self.status


class DiscountTermination(TerminationCriterion):
    """
    """

    def __init__(self, start, end, discount):
        """
        """
        super().__init__(start, end)
        self.discount = discount

    def satisfied(self):
        self.count += 1
        self.start *= self.discount
        self.status = self.start < self.end
        return self.status


class IterationTermination(TerminationCriterion):
    """
    """
    @classmethod
    def from_budget(cls, budget, window_size, window_move):
        return cls(0, math.floor(budget / (window_size + window_move)))

    def satisfied(self):
        self.start += 1
        self.count += 1
        self.status = self.start >= self.end
        return self.status

