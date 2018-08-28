from automode.controller.AutoMoDeControllerABC import AutoMoDeControllerABC
from abc import ABCMeta, abstractmethod
from enum import Enum
import graphviz as gv
from automode.modules.chocolate import Behavior, Condition
import random
from logging.Logger import Logger
import re


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
        def draw(self, graph):
            pass

    class RootNode(ABCNode):

        def name(self):
            return "Root_" + str(self.id)

        def draw(self, graph):
            self.children[0].draw(graph)

    class SequenceStarNode(ABCNode):

        @property
        def name(self):
            return "Sequence*_" + str(self.id)

        def draw(self, graph):
            graph.node(self.name, shape="square", label="->*")
            for child in self.children:
                graph.edge(self.name, child.name)
                child.draw(graph)

    class SelectorNode(ABCNode):

        @property
        def name(self):
            return "Selector_" + str(self.id)

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

        def draw(self, graph):
            graph.node(self.name, shape="diamond", label=self.caption())

        def caption(self):
            caption = self.condition.name + "_" + str(self.id)
            caption += self.condition.get_parameter_for_caption()
            return caption

    parameters = {"max_actions": 4}

    def __init__(self):        
        self.root = BT.RootNode()
        super().__init__()


    def create_minimal_controller(self):
        sequence = BT.SequenceStarNode()
        self.root.children.append(sequence)
        sel1 = BT.SelectorNode()
        sel1.children.append(BT.ConditionNode("FixedProbability"))
        sel1.children.append(BT.ActionNode("Exploration"))
        sequence.children.append(sel1)

    def draw(self, graph_name):
        graph = gv.Digraph(format='svg')
        self.root.draw(graph)
        filename = graph.render(filename='img/graph_' + graph_name, view=False)

    @staticmethod
    def parse_from_commandline_args(cmd_args):

        def parse_top_level_node():
            to_parse.pop(0)  # --rootnode
            top_level_type = int(to_parse.pop(0))  # 0
            behavior_tree.root.children.append(BT.SequenceStarNode())
            to_parse.pop(0)  # --nchildsroot
            top_level_children_count = int(to_parse.pop(0))  # not really needed, iterating over subtrees should work fine

        def parse_selector_subtree():
            '''
                The parsing of the parameters in this function is a very dirty fix.
                Once back from holidays, try and find a better way to handle it.
                At  the moment it just iterates over the length of the parameters and 
                reads one parameter from the parse_list.
            '''
            # parse selector node
            selector_id_string = to_parse.pop(0)  # --n[]
            selector_type = int(to_parse.pop(0))  # 0
            num_conditions_string = to_parse.pop(0)  # --nc[]
            num_conditions = int(to_parse.pop(0))  # 1
            selector = BT.SelectorNode()
            condition_label = to_parse.pop(0)  # --c[]x[]
            condition_type = int(to_parse.pop(0))
            condition_node = BT.ConditionNode("FixedProbability")
            condition_node.condition = Condition.get_by_id(condition_type)
            # TODO: FIX: parse condition parameters
            for condition_param in condition_node.condition.params:
                param_string = to_parse.pop(0)  # param identifier
                param_name = regex_no_number.match(param_string.split("--")[1]).group()
                if isinstance(condition_node.condition.params[param_name], int):
                    param_val = int(to_parse.pop(0))
                else:
                    param_val = float(to_parse.pop(0))
                condition_node.condition.params[param_name] = param_val
            action_label = to_parse.pop(0)  # --a[]
            action_type = int(to_parse.pop(0))
            action_node = BT.ActionNode("Stop")
            action_node.action = Behavior.get_by_id(action_type)
            # TODO: FIX: parse action parameters
            for action_param in action_node.action.params:
                param_string = to_parse.pop(0)  # param identifier
                param_name = regex_no_number.match(param_string.split("--")[1]).group()
                if param_name == "rwm":
                    param_val = int(to_parse.pop(0))
                else:
                    param_val = float(to_parse.pop(0))
                action_node.action.params[param_name] = param_val
            selector.children.append(condition_node)
            selector.children.append(action_node)
            behavior_tree.root.children[0].children.append(selector)

        #
        regex_action_node = re.compile("--a[0-9]")
        regex_no_number = re.compile("[^0-9]+")
        # create an emtpy BT
        behavior_tree = BT()
        behavior_tree.root.children.clear()  # could also clear the root node, but the root node is invariant
        # prepare the arguments
        to_parse = list(cmd_args)
        # parse the initial information
        parse_top_level_node()
        # parse the selector subtrees
        while to_parse:
            parse_selector_subtree()
        return behavior_tree

    def convert_to_commandline_args(self):
        """Converts this BT to a format that is readable by the AutoMoDe command line"""
        # always start with "--bt-config --rootnode 0"
        args = ["--bt-config", "--rootnode", "0"]
        # report the number of subtrees for the top_node
        args.extend(["--nchildsroot", str(len(self.top_node.children))])  # the "rootnode" of the cmd args is in reality just the top_node
        for i in range(0, len(self.top_node.children)):
            # process the child
            num_conditions = 1
            selector = self.top_node.children[i]
            child_args = ["--n{}".format(i), "0", "--nc{}".format(i), "{}".format(num_conditions)]  # we only care for exactly one condition
            for j in range(0, num_conditions):
                condition_node = selector.children[j]
                condition_args = ["--c{}x{}".format(i, j), str(condition_node.condition.int)]
                for param in condition_node.condition.params:
                    c = condition_node.condition.name
                    if c == "BlackFloor" or c == "GrayFloor" or c == "WhiteFloor" or c == "FixedProbability":
                        if param == "p":
                            pval = "%.2f" % condition_node.condition.params[param]
                    if c == "NeighborsCount" or c == "InvertedNeighborsCount":
                        if param == "w":
                            pval = "%.2f" % condition_node.condition.params[param]
                        if param == "p":
                            pval = str(condition_node.condition.params[param])
                    condition_args.extend(["--{}{}x{}".format(param, i, j), pval])
                child_args.extend(condition_args)
            action_node = selector.children[num_conditions]
            action_args = ["--a{}".format(i), str(action_node.action.int)]
            for param in action_node.action.params:
                if param == "att" or param == "rep":
                    pval = "%.2f" % action_node.action.params[param]
                elif param == "rwm":
                    pval = str(action_node.action.params[param])
                else:
                    Logger.instance.log_error("Undefined parameter")
                    pval = 0
                action_args.extend(["--{}{}".format(param, i), pval])
            child_args.extend(action_args)
            args.extend(child_args)
        return args

    # ******************************************************************************************************************
    # Mutation operators
    # ******************************************************************************************************************

    def mut_add_subtree(self):
        """
        Adds a new condition/action subtree to the BT
        The new subtree will be added as a random child to the sequence* node.
        """
        # Check if maximum number of subtrees is not exceeded
        if len(self.top_node.children) >= self.parameters["max_actions"]:
            return False  # we exceeded the amount of allowed subtrees
        # Generate new subtree
        new_selector = BT.SelectorNode()
        # Create random condition and action
        new_condition = BT.ConditionNode(random.choice(Condition.condition_list))
        new_action = BT.ActionNode(random.choice(Behavior.behavior_list))
        new_selector.children.append(new_condition)
        new_selector.children.append(new_action)
        # Add new node at random position
        copied_list = list(self.top_node.children)
        copied_list.append(None)
        new_position = random.choice(copied_list)
        if new_position is None:
            self.top_node.children.append(new_selector)
        else:
            self.top_node.children.insert(self.top_node.children.index(new_position), new_selector)
        return True

    def mut_remove_subtree(self):
        """
        Removes a random subtree from the BT
        """
        if len(self.top_node.children) <= 1:
            return False  # trying to remove the last subtree is forbidden
        to_remove = random.choice(self.top_node.children)
        self.top_node.children.remove(to_remove)
        return True

    def mut_change_subtree_order(self):
        """
        Selects one subtree and moves it to a new position
        """
        if len(self.top_node.children) <= 1:
            return False  # moving the only child has no effect
        # Select the child to be moved
        (old_pos, new_pos) = random.sample(self.top_node.children, 2)
        # Take the element after old_pos and move it to the after new_pos (which cannot be the same as old_pos)
        # If the element to be moved is the one at new_pos (it would have to be moved after itself),
        # move it to the beginning instead
        #
        # First remove the element
        remove_index = self.top_node.children.index(old_pos) + 1
        if remove_index >= len(self.top_node.children):
            remove_index -= len(self.top_node.children)
        remove_element = self.top_node.children[remove_index]
        self.top_node.children.remove(remove_element)
        # now put it at the right position
        if remove_element == new_pos:
            self.top_node.children.insert(0, remove_element)
        else:
            put_index = self.top_node.children.index(new_pos) + 1
            self.top_node.children.insert(put_index, remove_element)
        return True

    def mut_change_action_node_behavior(self):
        """
        Mutation for the local search of BT
        Changes a random behavior module in the BT
        TODO: More documentation
        :return:
        """
        # Check that there is at least one child to the top-node (it should be there; but better check)
        if len(self.top_node.children) < 1:
            return False
        # get the selector nodes that have an action node as child
        action_parent = random.choice(self.top_node.children)
        # get a random behavior from all possible behaviors (but make sure it is not the same behavior)
        new_behavior = Behavior.get_by_name(random.choice(
            [b for b in Behavior.behavior_list if b != action_parent.children[1].action.name]))  # b is just the name
        action_parent.children[1].action = new_behavior
        return True

    def mut_change_action_node_parameters(self):
        """
        Mutation for the local search of BT
        TODO: More documentation
        """
        # Check that there is at least one child to the top-node (it should be there; but better check)
        if len(self.top_node.children) < 1:
            return False
        # get the selector nodes that have an action node as child
        possible_action_parents = list(self.top_node.children)
        while possible_action_parents:
            selector = random.choice(possible_action_parents)  # choose on selector at random
            possible_action_parents.remove(selector)
            behavior = selector.children[1].action  # get the behavior from the action node
            keys = list(behavior.params.keys())
            if keys:
                param = random.choice(keys)  # choose a random parameter
                behavior.params[param] = Behavior.random_parameter(behavior.name + "." + param)
                return True
        # There was no state that had a changeable parameter
        return False

    def mut_change_condition_node_condition(self):
        """Swaps the condition of a random condition node"""
        # TODO: Check that there is at least one child to the top-node (it should be there but better check)
        # choose a random condition node
        condition_parent = random.choice(self.top_node.children)
        # choose a random condition and replace the current one (but make sure it is not the current one)
        new_condition = Condition.get_by_name(random.choice(
            [c for c in Condition.condition_list if c != condition_parent.children[0].condition.name]))
        condition_parent.children[0].condition = new_condition
        return True

    def mut_change_condition_node_parameters(self):
        """Changes a single parameter for one of the conditions"""
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
