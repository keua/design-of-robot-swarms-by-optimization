from automode.architecture.abstract_architecture import AutoMoDeArchitectureABC
from abc import ABCMeta, abstractmethod
from enum import Enum
import graphviz as gv
from automode.modules.chocolate import Behavior, Condition
import random
import logging
import re


class ABCNode:
    __metaclass__ = ABCMeta

    count = 0

    class ReturnCode(Enum):
        FAIL = -1
        RUNNING = 0
        SUCCESS = 1

    def __init__(self):
        self.children = []
        self.id = ""
        ABCNode.count += 1

    def set_id(self, new_id):
        """
        Recursively sets the new id. Call this on the root node to update all ids
        :param new_id:
        :return:
        """
        self.id = new_id
        for i in range(len(self.children)):
            self.children[i].set_id(new_id + str(i))

    def set_child(self, child_node, index=-1):
        """
        Sets the node as a child to this node. If index is not specified it will be appended,
        otherwise inserted at index
        :param child_node:
        :param index:
        :return: Nothing
        """
        if index < 0:
            self.children.append(child_node)
            child_node.set_id(self.id + str(len(self.children)))
        else:
            # TODO: Check that index is not breaking anything
            self.children.insert(index, child_node)
            self.set_id(self.id)

    def remove_child(self, child_node):
        """

        :param child_node:
        :return:
        """
        self.children.remove(child_node)
        self.set_id(self.id)
        pass

    @property
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def draw(self, graph):
        pass


class RootNode(ABCNode):

    def __init__(self):
        super().__init__()

    @property
    def name(self):
        return "root"  # + str(self.id)

    def draw(self, graph):
        self.children[0].draw(graph)


class SequenceStarNode(ABCNode):

    def __init__(self):
        super().__init__()

    @property
    def name(self):
        return "sequence*_" + str(self.id)

    def draw(self, graph):
        graph.node(self.name, shape="square", label="->*")
        for child in self.children:
            graph.edge(self.name, child.name)
            child.draw(graph)


class SelectorNode(ABCNode):

    def __init__(self):
        super().__init__()

    @property
    def name(self):
        return "selector_" + str(self.id)

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
        return self.action.name + "_" + self.id

    def draw(self, graph):
        graph.node(self.name, shape="circle", label=self.caption())

    def caption(self):
        caption = self.action.name  # + "_" + self.id
        caption += self.action.get_parameter_for_caption()
        return caption


class ConditionNode(ABCNode):

    def __init__(self, condition_name):
        super().__init__()
        self.condition = Condition.get_by_name(condition_name)

    @property
    def name(self):
        return self.condition.name + "_" + self.id

    def draw(self, graph):
        graph.node(self.name, shape="diamond", label=self.caption())

    def caption(self):
        caption = self.condition.name  # + "_" + str(self.id)
        caption += self.condition.get_parameter_for_caption()
        return caption


class AbstractBehaviorTree(AutoMoDeArchitectureABC):

    """This class is used as a base class for behavior trees. It should implemenet feature for both the restricted
    (Maple) version and a less restricted version.
    """

    parameters = {"max_actions": 4,
                  "minimal_condition": "Fail",
                  "minimal_behavior": "Fail"}

    def __init__(self, minimal=False):
        self.root = RootNode()
        super().__init__(minimal=minimal)

    def draw(self, graph_name):
        graph = gv.Digraph(format='svg')
        self.root.draw(graph)
        filename = graph.render(filename='img/graph_' + graph_name, view=False)


class UnrestrictedBehaviorTree(AbstractBehaviorTree):
    """
    This is the implementation for an unrestricted BT (there are still restrictions on the number of levels and the
    number of childs, but everything else can be chosen freely)
    """

    def __init__(self, minimal=False):
        super().__init__(minimal)

    def create_minimal_controller(self):
        """
        Sets up a minimal controller. That is a BT with a single action
        """
        self.root.children.append((ActionNode(AbstractBehaviorTree.parameters["minimal_behavior"])))

    @staticmethod
    def parse_from_commandline_args(cmd_args):
        """
        Parses a unrestricted behavior tree from cmd args
        :param cmd_args:
        :return:
        """
        raise NotImplementedError

    def convert_to_commandline_args(self):
        """Converts this BT to a format that is readable by the AutoMoDe command line"""
        raise NotImplementedError

    # ******************************************************************************************************************
    # perturbation operators
    # ******************************************************************************************************************

    def perturb_reorder_subtrees(self):
        """
        :return:
        """
        raise NotImplementedError
        # TODO: select CFN with at least two children
        # TODO: select two random children
        # TODO: swap their positions

    def perturb_change_control_flow_node(self):
        """

        :return:
        """
        # TODO: select CFN
        # TODO: change type of CFN
        raise NotImplementedError

    def perturb_change_leaf_node(self):
        """

        :return:
        """
        # TODO: select leaf
        # TODO: check if it can be transformed in an action or condition
        # TODO: if both types possible, then choose one type
        # TODO: if type is chosen (or only one possible), then select random instance of that type


class RestrictedBehaviorTree(AbstractBehaviorTree):
    """
    This is the implementation of a restricted BT (just like in Maple)
    """

    def __init__(self, minimal=False):
        super().__init__(minimal)

    def create_minimal_controller(self):
        """
        Sets up a minimal controller. That is a BT with a single action and a single condition.
        """
        sequence = SequenceStarNode()
        self.root.set_child(sequence)
        sel1 = SelectorNode()
        sel1.set_child(ConditionNode(AbstractBehaviorTree.parameters["minimal_condition"]))
        sel1.set_child(ActionNode(AbstractBehaviorTree.parameters["minimal_behavior"]))
        sequence.set_child(sel1)

    @staticmethod
    def parse_from_commandline_args(cmd_args):

        # TODO: Adjust for new BT structure

        def parse_top_level_node():
            to_parse.pop(0)  # --rootnode
            top_level_type = int(to_parse.pop(0))  # 0
            behavior_tree.root.set_child(SequenceStarNode())
            to_parse.pop(0)  # --nchildsroot
            top_level_children_count = int(to_parse.pop(0))  # not really needed, iterating over subtrees should work fine

        def parse_selector_subtree():
            """
                The parsing of the parameters in this function is a very dirty fix.
                Once back from holidays, try and find a better way to handle it.
                At  the moment it just iterates over the length of the parameters and 
                reads one parameter from the parse_list.
            """
            # parse selector node
            selector_id_string = to_parse.pop(0)  # --n[]
            selector_type = int(to_parse.pop(0))  # 0
            num_conditions_string = to_parse.pop(0)  # --nc[]
            num_conditions = int(to_parse.pop(0))  # 1
            selector = SelectorNode()
            condition_label = to_parse.pop(0)  # --c[]x[]
            condition_type = int(to_parse.pop(0))
            condition_node = ConditionNode("FixedProbability")
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
            action_node = ActionNode("Stop")
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
            selector.set_child(condition_node)
            selector.set_child(action_node)
            behavior_tree.root.children[0].set_child(selector)

        #
        regex_action_node = re.compile("--a[0-9]")
        regex_no_number = re.compile("[^0-9]+")
        # create an emtpy BT
        behavior_tree = Restricted_BT()
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
        # always start with "--bt-config --nroot 3"
        args = ["--bt-config", "--nroot", "3"]
        # report the number of subtrees for the top_node
        args.extend(["--nchildroot", str(len(self.top_node.children))])  # the "rootnode" of the cmd args is in reality just the top_node
        for i in range(0, len(self.top_node.children)):
            # process the child
            num_conditions = 1
            selector = self.top_node.children[i]
            child_args = ["--n{}".format(i), "0", "--nchild{}".format(i), "{}".format(num_conditions+1)]  # we only care for exactly one condition
            for j in range(0, num_conditions):
                condition_node = selector.children[j]
                condition_id = "{}{}".format(i, j)
                condition_args = ["--n{}".format(condition_id), "6", "--c{}".format(condition_id), str(condition_node.condition.int)]
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
                    condition_args.extend(["--{}{}".format(param, condition_id), pval])
                child_args.extend(condition_args)
            action_node = selector.children[num_conditions]
            action_id = "{}{}".format(i, num_conditions)
            action_args = ["--n{}".format(action_id), "5", "--a{}".format(action_id), str(action_node.action.int)]
            for param in action_node.action.params:
                if param == "att" or param == "rep":
                    pval = "%.2f" % action_node.action.params[param]
                elif param == "rwm":
                    pval = str(action_node.action.params[param])
                else:
                    logging.error("Undefined parameter")
                    pval = 0
                action_args.extend(["--{}{}".format(param, action_id), pval])
            # Now we also need to include the success probability
            action_args.extend(["--p{}".format(action_id), "0"])
            child_args.extend(action_args)
            args.extend(child_args)
        return args

    # ******************************************************************************************************************
    # perturbation operators
    # ******************************************************************************************************************

    def perturb_add_subtree(self):
        """
        Adds a new condition/action subtree to the BT
        The new subtree will be added as a random child to the sequence* node.
        """
        # Check if maximum number of subtrees is not exceeded
        if len(self.top_node.children) >= self.parameters["max_actions"]:
            return False  # we exceeded the amount of allowed subtrees
        # Generate new subtree
        new_selector = SelectorNode()
        # Create random condition and action
        new_condition = ConditionNode(random.choice(Condition.condition_list))
        new_action = ActionNode(random.choice(Behavior.behavior_list))
        new_selector.set_child(new_condition)
        new_selector.set_child(new_action)
        # Add new node at random position
        copied_list = list(self.top_node.children)
        copied_list.append(None)
        new_position = random.choice(copied_list)
        if new_position is None:
            self.top_node.set_child(new_selector)
        else:
            self.top_node.set_child(new_selector, self.top_node.children.index(new_position))
        return True

    def perturb_remove_subtree(self):
        """
        Removes a random subtree from the BT
        """
        if len(self.top_node.children) <= 1:
            return False  # trying to remove the last subtree is forbidden
        to_remove = random.choice(self.top_node.children)
        self.top_node.remove_child(to_remove)
        return True

    def perturb_change_subtree_order(self):
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
        self.top_node.remove_child(remove_element)
        # now put it at the right position
        if remove_element == new_pos:
            self.top_node.set_child(remove_element, 0)
        else:
            put_index = self.top_node.children.index(new_pos) + 1
            self.top_node.set_child(remove_element, put_index)
        return True

    def perturb_change_action_node_behavior(self):
        """
        Perturbation for the local search of BT
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

    def perturb_change_action_node_parameters(self):
        """
        Perturbation for the local search of BT
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

    def perturb_change_condition_node_condition(self):
        """Swaps the condition of a random condition node"""
        # TODO: Check that there is at least one child to the top-node (it should be there but better check)
        # choose a random condition node
        condition_parent = random.choice(self.top_node.children)
        # choose a random condition and replace the current one (but make sure it is not the current one)
        new_condition = Condition.get_by_name(random.choice(
            [c for c in Condition.condition_list if c != condition_parent.children[0].condition.name]))
        condition_parent.children[0].condition = new_condition
        return True

    def perturb_change_condition_node_parameters(self):
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
