
import time as tm


class TerminationCriterion(object):
    """
    """

    def __init__(self, start=tm.time(), end=15, discount=None, criterion="time"):
        """
        """
        self.criterion = criterion
        self.start = start
        self.end = end
        self.discount = discount

    def satisfied(self):
        """
        """
        if self.criterion == "time":
            return tm.time() > self.start + self.end * 60
        elif self.criterion == "discount":
            self.start *= self.discount
            return self.start < self.end
        elif self.criterion == "iteration":
            self.start += 1
            return self.start < self.end
