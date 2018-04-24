import random
from AutoModeABC import ABCBehavior, ABCCondition


class Behavior (ABCBehavior):

    def __init__(self, name):
        self.name = name
        self.params = Behavior.get_parameters_for_behavior(name)

    @staticmethod
    def get_by_name(name):
        """Returns a new instance of the specified behavior"""
        return Behavior(name)

    @staticmethod
    def get_by_id(b_id):
        b_name = "Failure"
        if b_id == 0:
            b_name = "Exploration"
        elif b_id == 1:
            b_name = "Stop"
        elif b_id == 2:
            b_name = "Phototaxis"
        elif b_id == 3:
            b_name = "AntiPhototaxis"
        elif b_id == 4:
            b_name = "Attraction"
        elif b_id == 5:
            b_name = "Repulsion"
        else:
            print("Unknown id " + str(b_id) + " for a behavior.")
        return Behavior(b_name)

    @staticmethod
    def get_parameters_for_behavior(name):
        """Returns a list of names of the parameters that can be used to alter the behavior"""
        if name == "AntiPhototaxis":
            return {}
        elif name == "Attraction":
            return {"att": Behavior.random_parameter("Attraction.att")}  # real value in [1,5]
        elif name == "Exploration":
            return {"rwm": Behavior.random_parameter("Exploration.rwm")}  # Boundaries {1,2,...,100} all integers
        elif name == "Phototaxis":
            return {}
        elif name == "Stop":
            return {}
        elif name == "Repulsion":
            return {"rep": Behavior.random_parameter("Repulsion.rep")}  # real value in [1,5]
        # elif name == "":
        #    return {}
        return {}

    @staticmethod
    def random_parameter(name):
        """Returns a random uniform value for the given parameter.
        To allow identification when different parameter spaces are used for the same parameter name it must be fully
        quantified (that is [behavior].[parameter])"""
        splits = name.split(".")
        b = splits[0]
        p = splits[1]
        if p == "att":
            return random.uniform(1, 5)
        if p == "rwm":
            return random.randint(0, 100)
        if p == "rep":
            return random.uniform(1, 5)
        print("Invalid combination of condition and parameter " + name)
        return 0

    @property
    def int(self):
        """Returns an integer value according to the internal representation of AutoMoDe"""
        if self.name == "Exploration":
            return 0
        elif self.name == "Stop":
            return 1
        elif self.name == "Phototaxis":
            return 2
        elif self.name == "AntiPhototaxis":
            return 3
        elif self.name == "Attraction":
            return 4
        elif self.name == "Repulsion":
            return 5
        print("Unknown name " + self.name + " for a behavior.")
        return -1

    """This list contains all possible behaviors that exist in AutoMoDe Chocolate"""
    behavior_list = ["AntiPhototaxis", "Attraction", "Exploration", "Phototaxis", "Stop", "Repulsion"]


class Condition (ABCCondition):

    def __init__(self, name):
        self.name = name
        self.params = Condition.get_parameters_for_condition(name)

    @staticmethod
    def get_by_name(name):
        """Returns a new instance of the specified condition"""
        return Condition(name)

    @staticmethod
    def get_by_id(t_id):
        t_name = "Failure"
        if t_id == 0:
            t_name = "BlackFloor"
        elif t_id == 1:
            t_name = "GrayFloor"
        elif t_id == 2:
            t_name = "WhiteFloor"
        elif t_id == 3:
            t_name = "NeighborsCount"
        elif t_id == 4:
            t_name = "InvertedNeighborsCount"
        elif t_id == 5:
            t_name = "FixedProbability"
        else:
            print("Unknown id " + str(t_id) + " for a behavior.")
        return Condition(t_name)

    @staticmethod
    def get_parameters_for_condition(name):
        """Returns a list of names of the parameters that can be used to alter the condition"""
        if name == "BlackFloor":
            return {"p": Condition.random_parameter("BlackFloor.p")}  # probably between 0 and 1
        elif name == "FixedProbability":
            return {"p": Condition.random_parameter("FixedProbability.p")}  # probably between 0 and 1
        elif name == "GrayFloor":
            return {"p": Condition.random_parameter("GrayFloor.p")}  # probably between 0 and 1
        elif name == "InvertedNeighborsCount":
            return {"w": Condition.random_parameter("InvertedNeighborsCount.w"),  # real value in [0,20]
                    "p": Condition.random_parameter("InvertedNeighborsCount.p")}  # integer in {1, 2, ..., 10}
        elif name == "NeighborsCount":
            return {"w": Condition.random_parameter("NeighborsCount.w"),  # real value in [0,20]
                    "p": Condition.random_parameter("NeighborsCount.p")}  # integer in {1, 2, ..., 10}
        elif name == "WhiteFloor":
            return {"p": Condition.random_parameter("WhiteFloor.p")}  # probably between 0 and 1
        return {}

    @staticmethod
    def random_parameter(name):
        """Returns a random uniform value for the given parameter.
        To allow identification when different parameter spaces are used for the same parameter name it must be fully
        quantified (that is [condition].[parameter])"""
        splits = name.split(".")
        c = splits[0]
        p = splits[1]
        if c == "BlackFloor" or c == "GrayFloor" or c == "WhiteFloor" or c == "FixedProbability":
            if p == "p":
                return random.uniform(0, 1)
            print("Invalid parameter " + p + " for condition " + c)
        if c == "NeighborsCount" or c == "InvertedNeighborsCount":
            if p == "w":
                return random.uniform(0, 20)
            if p == "p":
                return random.randint(1, 10)
            print("Invalid parameter " + p + " for condition " + c)
        print("Invalid combination of condition and parameter " + name)
        return 0

    @property
    def int(self):
        """Returns an integer value according to the internal representation of AutoMoDe"""
        if self.name == "BlackFloor":
            return 0
        elif self.name == "GrayFloor":
            return 1
        elif self.name == "WhiteFloor":
            return 2
        elif self.name == "NeighborsCount":
            return 3
        elif self.name == "InvertedNeighborsCount":
            return 4
        elif self.name == "FixedProbability":
            return 5
        print("Unknown name " + self.name + " for a condition")
        return -1

    """This list contains all possible conditions that exist in AutoMoDe Chocolate"""
    condition_list = ["BlackFloor", "FixedProbability", "GrayFloor", "InvertedNeighborsCount", "NeighborsCount",
                      "WhiteFloor"]
