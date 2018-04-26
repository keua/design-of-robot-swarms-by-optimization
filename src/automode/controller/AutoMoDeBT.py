from automode.controller.AutoMoDeControllerABC import AutoMoDeControllerABC
from abc import ABCMeta, abstractmethod
from enum import Enum
import graphviz as gv
from automode.modules.AutoModeChocolate import Behavior, Condition


class BT(AutoMoDeControllerABC):

    class ABCNode:
        __metaclass__ = ABCMeta

        count = 0

        class ReturnCode(Enum):
            FAIL = -1
            RUNNING = 0
            SUCCESS = 1

        def __init__(self):
            self.children = []
            self.id = BT.ABCNode.count
            BT.ABCNode.count += 1

        @property
        @abstractmethod
        def name(self):
            pass

        @abstractmethod
        def tick(self):
            pass

        @abstractmethod
        def draw(self, graph):
            pass

    class RootNode(ABCNode):

        def name(self):
            return "Root_" + str(self.id)

        def tick(self):
            self.children[0].tick()

        def draw(self, graph):
            self.children[0].draw(graph)

    class SequenceStarNode(ABCNode):

        @property
        def name(self):
            return "Sequence*_" + str(self.id)

        def tick(self):
            for child in self.children:
                return_value = child.tick()
                if not return_value == BT.ABCNode.ReturnCode.SUCCESS:
                    # TODO: Last ticked child
                    return return_value
            return BT.ABCNode.ReturnCode.SUCCESS

        def draw(self, graph):
            graph.node(self.name, shape="square", label= "->*")
            for child in self.children:
                graph.edge(self.name, child.name)
                child.draw(graph)

    class SelectorNode(ABCNode):

        @property
        def name(self):
            return "Selector_" + str(self.id)

        def tick(self):
            pass

        def draw(self, graph):
            graph.node(self.name, shape="square", label="?")
            for child in self.children:
                graph.edge(self.name, child.name)
                child.draw(graph)

    class ActionNode(ABCNode):

        def __init__(self, behavior_name):
            super().__init__()
            self.action = Behavior.get_by_name(behavior_name)

        @property
        def name(self):
            return self.action.name + "_" + str(self.id)

        def tick(self):
            pass

        def draw(self, graph):
            graph.node(self.name, shape="circle", label=self.caption())

        def caption(self):
            tmp = self.action.name + "_" + str(self.id)
            if self.action.params:
                tmp = tmp + "\n("
                first = True
                for key, value in self.action.params.items():
                    if not first:
                        tmp = tmp + ", "
                    first = False
                    tmp = tmp + key + ": " + str(value)
                tmp = tmp + ")"
            return tmp

    class ConditionNode(ABCNode):

        def __init__(self, condition_name):
            super().__init__()
            self.condition = Condition.get_by_name(condition_name)

        @property
        def name(self):
            return self.condition.name + "_" + str(self.id)

        def tick(self):
            pass

        def draw(self, graph):
            graph.node(self.name, shape="diamond", label=self.caption())

        def caption(self):
            tmp = self.condition.name + "_" + str(self.id)
            if self.condition.params:
                tmp = tmp + "\n("
                first = True
                for key, value in self.condition.params.items():
                    if not first:
                        tmp = tmp + ", "
                    first = False
                    tmp = tmp + key + ": " + str(value)
                tmp = tmp + ")"
            return tmp

    def __init__(self):
        super().__init__()
        self.root = BT.RootNode()
        sequence = BT.SequenceStarNode()
        self.root.children.append(sequence)
        sel1 = BT.SelectorNode()
        sel1.children.append(BT.ConditionNode("FixedProbability"))
        sel1.children.append(BT.ActionNode("Stop"))
        sequence.children.append(sel1)

    def draw(self, graph_name):
        graph = gv.Digraph(format='svg')
        self.root.draw(graph)
        filename = graph.render(filename='img/graph_' + graph_name, view=False)

    @staticmethod
    def parse_from_commandline_args(cmd_args):
        pass

    def convert_to_commandline_args(self):
        pass

    def evaluate_single_run(self, seed):
        pass

    def mutate(self):
        pass
