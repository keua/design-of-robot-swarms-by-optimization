from automode.controller.AutoMoDeControllerABC import AutoMoDeControllerABC
from abc import ABCMeta, abstractmethod
from enum import Enum


class BT(AutoMoDeControllerABC):

    class ABCNode:
        __metaclass__ = ABCMeta

        class ReturnCode(Enum):
            FAIL = -1
            RUNNING = 0
            SUCCESS = 1

        def __init__(self):
            self.children = []

        @abstractmethod
        def tick(self):
            pass

        @abstractmethod
        def draw(self):
            pass

    class RootNode(ABCNode):

        def tick(self):
            self.children[0].tick()

        def draw(self):
            pass

    class SequenceStarNode(ABCNode):

        def tick(self):
            for child in self.children:
                return_value = child.tick()
                if not return_value == BT.ABCNode.ReturnCode.SUCCESS:
                    # TODO: Last ticked child
                    return return_value
            return BT.ABCNode.ReturnCode.SUCCESS

        def draw(self):
            pass

    class SelectorNode(ABCNode):

        def tick(self):
            pass

        def draw(self):
            pass

    def __init__(self):
        super().__init__()

    def draw(self):
        pass

    @staticmethod
    def parse_from_commandline_args(cmd_args):
        pass

    def convert_to_commandline_args(self):
        pass

    def evaluate_single_run(self, seed):
        pass

    def mutate(self):
        pass
