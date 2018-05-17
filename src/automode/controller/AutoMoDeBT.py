from automode.controller.AutoMoDeControllerABC import AutoMoDeControllerABC
from abc import ABCMeta, abstractmethod
from enum import Enum
import graphviz as gv
from automode.modules.chocolate import Behavior, Condition
import subprocess
import random


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
            graph.node(self.name, shape="square", label="->*")
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
            caption = self.action.name + "_" + str(self.id)
            caption += self.action.get_parameter_for_caption()
            return caption

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
            caption = self.condition.name + "_" + str(self.id)
            caption += self.condition.get_parameter_for_caption()
            return caption

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
        return 1
        """Run a single evaluation in Argos"""
        # print("Evaluating BT " + str(self.id) + " on seed " + str(seed))
        # prepare the command line
        args = [self.path_to_automode_executable, "-n", "-c", self.scenario_file, "--seed", str(seed), "--bt-config"]
        args.extend(self.convert_to_commandline_args())
        # Run and capture output
        p = subprocess.Popen(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        (stdout, stderr) = p.communicate()
        # Analyse result
        output = stdout.decode('utf-8')
        lines = output.splitlines()
        try:
            return float(lines[len(lines) - 1].split(" ")[1])
        except:
            print(args)
            print(stderr.decode('utf-8'))
            print(stdout.decode('utf-8'))
            raise

    # ******************************************************************************************************************
    # Mutation operators
    # ******************************************************************************************************************

    def mut_add_subtree(self):
        """
        Adds a new condition/action subtree to the BT
        The new subtree will be added as a random child to the sequence* node.
        """
        # TODO: Check if maximum number of subtrees is not exceeded
        # TODO: Get the parameters
        # if len(self.top_node.children) >= self.parameters["max_states"]:
        #    return False  # we exceeded the amount of allowed subtrees
        # TODO: Generate new subtree
        new_selector = BT.SelectorNode()
        # TODO: Set random condition and action
        new_condition = BT.ConditionNode("BlackFloor")
        new_action = BT.ActionNode("Stop")
        new_selector.children.append(new_condition)
        new_selector.children.append(new_action)
        # TODO: Add to random location
        self.top_node.children.append(new_selector)
        return True

    def mut_remove_subtree(self):
        """Removes a random subtree from the BT"""
        if len(self.top_node.children) <= 1:
            return False  # trying to remove the last subtree is forbidden
        to_remove = random.choice(self.top_node.children)
        self.top_node.children.remove(to_remove)
        return True

    def mut_change_subtree_order(self):
        """Selects one subtree and moves it to a new position"""
        if len(self.top_node.children) <= 1:
            return False  # moving the only child has no effect
        # TODO: Select the child to be moved
        to_move = random.choice(self.top_node.children)
        possible_locations = [x for x in range(0, len(self.top_node.children)) if self.top_node.children[x] != to_move]
        # TODO: Move subtree
        return True

    def mut_change_action_behavior(self):
        # TODO: Check that there is at least one child to the top-node (it should be there but better check)
        action_parent = random.choice(self.top_node.children)
        # get a random behavior from all possible behaviors (but make sure it is not the same behavior)
        new_behavior = Behavior.get_by_name(random.choice(
            [b for b in Behavior.behavior_list if b != action_parent.children[1].action.name]))  # b is just the name
        action_parent.children[1].action = new_behavior
        return True

    def mut_change_state_behavior_parameters(self):
        # TODO: Check that there is at least one child to the top-node (it should be there but better check)
        possible_action_parents = list(self.top_node.children)
        while possible_action_parents:
            s = random.choice(possible_action_parents)
            possible_action_parents.remove(s)
            b = s.children[1].action
            keys = list(b.params.keys())
            if keys:
                param = random.choice(keys)
                b.params[param] = Behavior.random_parameter(b.name + "." + param)
                return True
        # There was no state that had a changeable parameter
        return False

    def mut_change_transition_condition(self):
        """Swaps the condition of a random condition node"""
        # TODO: Check that there is at least one child to the top-node (it should be there but better check)
        # choose a random condition node
        condition_parent = random.choice(self.top_node.children)
        # choose a random condition and replace the current one (but make sure it is not the current one)
        new_condition = Condition.get_by_name(random.choice(
            [c for c in Condition.condition_list if c != condition_parent.children[0].condition.name]))
        condition_parent.children[0].condition = new_condition
        return True

    def mut_change_transition_condition_parameters(self):
        # TODO: Check that there is at least one child to the top-node (it should be there but better check)
        possible_condition_parents = list(self.top_node.children)
        while possible_condition_parents:
            s = random.choice(possible_condition_parents)
            possible_condition_parents.remove(s)
            c = s.children[0].condition
            keys = list(c.params.keys())
            if keys:
                param = random.choice(keys)
                c.params[param] = Condition.random_parameter(c.name + "." + param)
                return True
        # There was no state that had a changeable parameter
        return False

    # ******************************************************************************************************************
    # Utility functions
    # ******************************************************************************************************************

    @property
    def top_node(self):
        return self.root.children[0]
