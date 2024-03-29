from automode.modules.chocolate import Behavior, Condition
import random
import graphviz as gv
import logging
import re
from automode.architecture.abstract_architecture import AutoMoDeArchitectureABC
import settings

# TODO: Write documentation for methods and classes


class State:
    count = 0

    def __init__(self, behavior):
        self.behavior = behavior
        self.id = State.count
        self.ext_id = self.id  # the ext_id is used to identify this state for any external program
        State.count += 1

    def convert_to_AutoMoDe_commandline_args(self):
        """Converts this state to a format that is readable by the AutoMoDe command line"""
        args = ["--s" + str(self.ext_id), str(self.behavior.int)]
        for param in self.behavior.params:
            # TODO: Find better handling
            if param == "att" or param == "rep":
                pval = "%.2f" % self.behavior.params[param]
            elif param == "rwm":
                pval = str(self.behavior.params[param])
            else:
                logging.error("Undefined parameter")
                pval = 0
            args.extend(["--" + param + str(self.ext_id), pval])
        return args

    @property
    def name(self):
        """Returns an identifier for this state, made up by its behavior and id"""
        return self.behavior.name + "_" + str(self.id)

    def caption(self):
        """Returns a caption for the state that can be used to represent the state in graphviz"""
        caption = self.behavior.name + "_" + str(self.id)
        caption += self.behavior.get_parameter_for_caption()
        return caption


class Transition:
    count = 0

    def __init__(self, from_state, to_state, condition):
        self.from_state = from_state
        self.to_state = to_state
        self.condition = condition
        self.id = Transition.count
        self.ext_id = self.id  # the ext_id is used to identify this transition for any external program
        Transition.count += 1

    def convert_to_AutoMoDe_commandline_args(self):
        """Converts this transition to a format that is readable by the AutoMoDe command line"""
        t_id = str(self.from_state.ext_id) + "x" + str(self.ext_id)
        if self.from_state.ext_id < self.to_state.ext_id:
            # This has to do with the issue of GetPossibleDestinationBehaviors in AutoMoDe
            args = ["--n" + t_id, str(self.to_state.ext_id - 1)]
        else:
            args = ["--n" + t_id, str(self.to_state.ext_id)]
        args.extend(["--c" + t_id, str(self.condition.int)])
        for param in self.condition.params:
            c = self.condition.name
            if c == "BlackFloor" or c == "GrayFloor" or c == "WhiteFloor" or c == "FixedProbability":
                if param == "p":
                    pval = "%.2f" % self.condition.params[param]
            if c == "NeighborsCount" or c == "InvertedNeighborsCount":
                if param == "w":
                    pval = "%.2f" % self.condition.params[param]
                if param == "p":
                    pval = str(self.condition.params[param])
            args.extend(["--" + param + str(t_id), pval])
        return args

    @property
    def name(self):
        """Returns an identifier for this state, made up by its behavior and id"""
        return self.condition.name + "_" + str(self.id)

    def caption(self):
        """Returns a caption for the state that can be used to represent the state in graphviz"""
        caption = self.condition.name + "_" + str(self.id)
        caption += self.condition.get_parameter_for_caption()
        return caption


class FSM(AutoMoDeArchitectureABC):
    """A finite state machine"""

    # FSM implementation

    def __init__(self, minimal=False):
        self.initial_state = None
        self.states = []
        self.transitions = []
        super().__init__(minimal=minimal)

        # used to find articulation points, find better place then here
        self.aputils_time = 0

    def create_minimal_controller(self):
        """
        Sets up a minimal controller. That is a FSM with a single state and no transitions.
        """
        # The empty FSM
        minimal_behavior = Behavior.get_by_name(settings.controller["minimal_behavior"])
        self.initial_state = State(minimal_behavior)
        self.states = [self.initial_state]
        self.transitions = []

    def draw(self, graph_name):
        """Draw the graph representation of the FSM with graphviz"""
        graph = gv.Digraph(format='svg')
        for s in self.states:
            if s == self.initial_state:
                graph.node(s.name, shape="doublecircle", label=s.caption())
            else:
                graph.node(s.name, shape="circle", label=s.caption())
        for t in self.transitions:
            graph.node(t.name, shape="diamond", label=t.caption())
            graph.edge(t.from_state.name, t.name)
            graph.edge(t.name, t.to_state.name)
        filename = graph.render(filename='img/graph_' + graph_name, view=False)

    @staticmethod
    def parse_from_commandline_args(cmd_args):
        """This is the invert of convert_to_commandline_args"""

        def parse_number_of_states():
            """Used so that transitions can immediately point to the states they need"""
            number_of_states = int(to_parse.pop(0))  # this the number of states
            # Create an according number of states
            for i in range(0, number_of_states):
                s = State(stop_behavior)
                s.ext_id = i
                finite_state_machine.states.append(s)
            return number_of_states

        def parse_state():
            state_number = int(token.split("--s")[1])  # take only the number
            state_behavior_id = int(to_parse.pop(0))
            # get the state
            state = [s for s in finite_state_machine.states if s.ext_id == state_number][0]
            # set the correct behavior
            state.behavior = Behavior.get_by_id(state_behavior_id)
            if number_of_states > 1:  # HOTFIX: if there is only one state there is no number of transitions
                # TODO: Find better solution than this hotfix
                # pop until we read --nstatenumber
                tmp = to_parse.pop(0)
                number_of_transitions_delimiter = "--n" + str(state_number)
                # TODO: Improve parsing of parameters and try to add some error handling
                while tmp != number_of_transitions_delimiter:
                    # parse current attribute
                    regex_no_number = re.compile("[^0-9]+")
                    param_name = regex_no_number.match(tmp.split("--")[1]).group()
                    if param_name == "rwm":
                        param_val = int(to_parse.pop(0))
                    else:
                        param_val = float(to_parse.pop(0))
                    state.behavior.params[param_name] = param_val
                    tmp = to_parse.pop(0)
                number_of_transitions = int(to_parse.pop(0))

        def parse_transition():
            transition_id = [int(x) for x in token.split("--n")[1].split("x")]
            from_state = [s for s in finite_state_machine.states if s.ext_id == transition_id[0]][0]
            # to_state = [s for s in finite_state_machine.states if s.ext_id == transition_ids[1]][0]
            transition_ext_id = transition_id[1]
            to_state_id = int(to_parse.pop(0))
            if to_state_id < from_state.ext_id:
                to_state = [s for s in finite_state_machine.states if s.ext_id == to_state_id][0]
            else:  # self-reference not allowed
                to_state = [s for s in finite_state_machine.states if s.ext_id == to_state_id + 1][0]
            condition_count = to_parse.pop(0)
            transition_condition_id = int(to_parse.pop(0))
            # Create transition
            t = Transition(from_state, to_state, Condition.get_by_id(transition_condition_id))
            t.ext_id = transition_ext_id
            finite_state_machine.transitions.append(t)
            re_string = "--[a-z]{}x{}".format(from_state.ext_id, t.ext_id)
            param_regex = re.compile(re_string)
            # TODO: Improve parsing of parameters and try to add some error handling
            while to_parse and param_regex.match(to_parse[0]):
                param_name = to_parse.pop(0)
                regex_no_number = re.compile("[^0-9]+")
                param_name = regex_no_number.match(param_name.split("--")[1]).group()
                if isinstance(t.condition.params[param_name], int):
                    param_val = int(to_parse.pop(0))
                else:
                    param_val = float(to_parse.pop(0))
                logging.debug("{}: {}".format(param_name, param_val))
                t.condition.params[param_name] = param_val

        # Setting up a completely empty FSM
        finite_state_machine = FSM()
        finite_state_machine.states.clear()
        # prepare the arguments
        to_parse = list(cmd_args)
        stop_behavior = Behavior.get_by_name("stop")
        while to_parse:
            token = to_parse.pop(0)
            if token == "--nstates":
                number_of_states = parse_number_of_states()
            elif "--s" in token:
                # token contains the string for a state
                parse_state()
            elif "--n" in token and "x" in token:  # TODO: Use better check (regex?)
                # token contains the string for a transition
                parse_transition()
        finite_state_machine.initial_state = [s for s in finite_state_machine.states if s.ext_id == 0][0]
        return finite_state_machine

    def convert_to_commandline_args(self):
        """Converts this FSM to a format that is readable by the AutoMoDe command line"""
        self.initial_state.ext_id = 0
        counter = 1
        for state in [s for s in self.states if s != self.initial_state]:
            state.ext_id = counter
            counter += 1
        args = ["--fsm-config", "--nstates", str(len(self.states))]
        # first send the initial state as this has to be state 0
        args.extend(self.initial_state.convert_to_AutoMoDe_commandline_args())
        # Handle the transitions from the initial state
        outgoing_transitions = [t for t in self.transitions if t.from_state == self.initial_state]
        if len(outgoing_transitions) > 0:
            counter = 0
            args.extend(["--n" + str(self.initial_state.ext_id), str(len(outgoing_transitions))])
            for transition in outgoing_transitions:
                transition.ext_id = counter
                counter += 1
                args.extend(transition.convert_to_AutoMoDe_commandline_args())
        # convert the other states
        for state in [s for s in self.states if s != self.initial_state]:
            args.extend(state.convert_to_AutoMoDe_commandline_args())
            # handle the outgoing transitions for this state
            outgoing_transitions = [t for t in self.transitions if t.from_state == state]
            if len(outgoing_transitions) > 0:
                counter = 0
                args.extend(["--n" + str(state.ext_id), str(len(outgoing_transitions))])
                for transition in outgoing_transitions:
                    transition.ext_id = counter
                    counter += 1
                    args.extend(transition.convert_to_AutoMoDe_commandline_args())
        return args

    # ******************************************************************************************************************
    # perturbation operators
    # ******************************************************************************************************************

    def perturb_change_initial_state(self):
        """Changes the initial state of the FSM.
        It is not allowed to keep the same initial state and the new initial state is chosen uniformly at random
        from all possible states.
        If no state is a possible candidate  (that is the FSM only has one state) it will return False."""
        # possible states are all states except for the initial state
        other_states = [x for x in self.states if x != self.initial_state]
        # if we can't choose any state, then report this operation as non-applicable
        if not other_states:
            return False
        # choose a new initial state
        self.initial_state = random.choice(other_states)
        return True

    def perturb_add_state(self):
        """Adds a new state to the FSM.
        It will not exceed the maximum number of states. In case that there is no space for a new state it will
        return False. Every added state will contain one ingoing and one outgoing edge."""
        if len(self.states) >= settings.FSM["max_states"]:
            return False  # we exceeded the amount of allowed states
        # create a new state with a random behavior
        new_behavior = Behavior.get_by_name(random.choice(Behavior.behavior_list))
        s = State(new_behavior)
        possible_states = list(self.states)  # create a transition from an already existing state
        s_in = random.choice(self.states)  # create a transition to an already existing state
        if settings.FSM["self_transition"]:
            possible_states.append(s)  # possible_states is now every state
            s_in = random.choice(list(self.states).append(s))  # draw again to determine from all possible_states now
        while possible_states:
            s_out = random.choice(possible_states)
            possible_states.remove(s_out)
            if len([t for t in self.transitions if t.from_state == s_out]) < settings.FSM["max_transitions_per_state"]:
                ingoing = Transition(s_out, s,
                                         Condition.get_by_name(random.choice(Condition.condition_list)))
                outgoing = Transition(s, s_in,
                                          Condition.get_by_name(random.choice(Condition.condition_list)))
                # add the state and transitions to the FSM
                self.states.append(s)
                self.transitions.append(ingoing)
                self.transitions.append(outgoing)
                return True
        return False

    def perturb_remove_state(self):
        """Removes a state from the FSM.
        Doesn't remove the last state (returns False if there is only one state). Also removes all transitions to and
        from the removed state. Will not remove a state that is an articulation point or that would delete the last
        in- or outgoing edges for another state. If there are only exactly two states then the non-initial state will be
        deleted nevertheless."""
        # If there is only one state (or even less for some reason), then report this operation as non-applicable
        if len(self.states) <= 1:
            return False
        # don't choose the initial state to be removed
        states = [s for s in self.states if s != self.initial_state]
        # check for every state if it is safe to remove it from the FSM
        removable = []
        if len(self.states) == 2:
            # allow removing of the other state
            removable.append(states[0])
        for s in states:
            is_removable = True
            # Check if s is an articulation point or would delete all in- or outgoing edges for another edge
            if self._check_if_articulation_point(s):
                is_removable = False
            # Check if this removes all in- or outgoing edges for s
            for t in [u for u in self.transitions if u.from_state == s or u.to_state == s]:
                if t.from_state == s:
                    # there is no other transition going to the same state but not starting in s
                    if not [u for u in self.transitions if u.from_state != s and u.to_state == t.to_state]:
                        is_removable = False
                else:
                    # there is no other transition going to s but from a different starting state
                    if not [u for u in self.transitions if u.to_state != s and u.from_state == t.from_state]:
                        is_removable = False
            if is_removable:
                removable.append(s)
        # if there is no state that is safe to remove, then report this operation as non-applicable
        if not removable:
            return False
        # choose one state that is safe to remove
        s = random.choice(removable)
        # remove all edges that use this state
        for t in list(self.transitions):
            if (t.from_state == s) or (t.to_state == s):
                self.transitions.remove(t)
        # remove the state
        self.states.remove(s)
        return True

    def perturb_change_state_behavior(self):
        """Swaps the behavior a random state with a new random behavior.
        The new behavior will not be the same as the replaced behavior."""
        # choose a random state
        s = random.choice(self.states)
        # get a random behavior from all possible behaviors (but make sure it is not the same behavior)
        new_behavior = Behavior.get_by_name(random.choice(
            [b for b in Behavior.behavior_list if b != s.behavior.name]))  # b is just the name
        # set the new behavior
        s.behavior = new_behavior
        return True

    def perturb_change_state_behavior_parameters(self):
        """Changes a single random parameter of the behavior of a random state.
        The parameter is chosen randomly in its range."""
        possible_states = list(self.states)
        while possible_states:
            s = random.choice(possible_states)
            possible_states.remove(s)
            b = s.behavior
            keys = list(b.params.keys())
            if keys:
                param = random.choice(keys)
                b.params[param] = Behavior.random_parameter(b.name + "." + param)
                return True
        # There was no state that had a changeable parameter
        return False

    def perturb_add_transition(self):
        """Adds a transition to the FSM"""
        if len(self.transitions) >= settings.FSM["max_transitions"]:
            return False  # already all transitions used
        # choose a random state where the new transition should start
        possible_states = list(self.states)
        while possible_states:
            start = random.choice(possible_states)
            possible_states.remove(start)
            # Check for this states that they don't exceed max transitions per state
            if len([t for t in self.transitions if t.from_state == start]) < settings.FSM["max_transitions_per_state"]:
                # the end state needs to be different from the starting state
                other_states = [s for s in self.states if s != start]
                # there must be at least another state
                if other_states:
                    # choose the endpoint at random
                    end = random.choice(other_states)
                    # Choose random condition
                    t = Transition(start, end, Condition.get_by_name(random.choice(Condition.condition_list)))
                    # add the new transition to the FSM
                    self.transitions.append(t)
                    return True
        # All states were tried but no one succeeded
        return False

    def perturb_remove_transition(self):
        """Removes a transition from the FSM"""
        possible_transitions = \
            [t for t in self.transitions
             # there is at least one other transition from the starting state
             if [u for u in self.transitions if (t.from_state == u.from_state) and t != u]
             # there is at least one other transition to the end state
             and [u for u in self.transitions if (t.to_state == u.to_state) and t != u]]
        # if there is no transition that can be chosen report this operation as non-applicable
        if not possible_transitions:
            return False
        # choose one transition at random
        t = random.choice(possible_transitions)
        # remove the transition from
        self.transitions.remove(t)
        return True

    def perturb_change_transition_begin(self):
        """Changes the starting state of a random transition"""
        possible_transitions = \
            [t for t in self.transitions
             if [u for u in self.transitions if t.from_state == u.from_state and t != u]]
        while possible_transitions:
            t = random.choice(possible_transitions)
            possible_transitions.remove(t)
            possible_states = [s for s in self.states if s != t.to_state and s != t.from_state]
            while possible_states:
                new_start = random.choice(possible_states)
                possible_states.remove(new_start)
                if len([t for t in self.transitions if t.from_state==new_start]) < settings.FSM["max_transitions_per_state"]:
                    t.from_state = new_start
                    return True
        return False

    def perturb_change_transition_end(self):
        """Changes the end node of a random transition"""
        possible_transitions = \
            [t for t in self.transitions
             if [u for u in self.transitions if t.to_state == u.to_state and t != u]]
        if not possible_transitions:
            return False  # We cannot choose any transition
        t = random.choice(possible_transitions)
        possible_states = [s for s in self.states if s != t.from_state and s != t.to_state]
        if not possible_states:
            return False  # no state to point to
        t.to_state = random.choice(possible_states)
        return True

    def perturb_change_transition_condition(self):
        """Swaps the condition of a random transition"""
        # if no transition exists then report this operation as non-applicable
        if not self.transitions:
            return False
        # choose a random transition
        t = random.choice(self.transitions)
        # choose a random condition and replace the current one (but make sure it is not the current one)
        new_condition = Condition.get_by_name(random.choice(
            [c for c in Condition.condition_list if c != t.condition.name]))
        t.condition = new_condition
        return True

    def perturb_change_transition_condition_parameters(self):
        # TODO: Retry, but not urgently since all transitions have at least a probability parameter
        """Changes a random parameter of the condition of a random transition"""
        if len(self.transitions) == 0:
            return False  # there is no transition to change
        t = random.choice(self.transitions)
        c = t.condition
        keys = list(c.params.keys())
        if not keys:
            return False
        param = random.choice(keys)
        c.params[param] = Condition.random_parameter(c.name + "." + param)
        return True

    # ******************************************************************************************************************
    # Utility functions
    # ******************************************************************************************************************

    def APUtil(self, u, visited, ap, parent, low, disc):
        '''A recursive function that find articulation points
            	using DFS traversal
            	u --> The vertex to be visited next
            	visited[] --> keeps tract of visited vertices
            	disc[] --> Stores discovery times of visited vertices
            	parent[] --> Stores parent vertices in DFS tree
            	ap[] --> Store articulation points'''
        # Count of children in current node
        children = 0

        # Mark the current node as visited
        visited[u] = True

        # Initialize discovery time and low value
        disc[u] = self.aputils_time
        low[u] = self.aputils_time
        self.aputils_time += 1

        adjacent_vertices = [s for s in self.states if
                             [t for t in self.transitions if t.from_state == u and t.to_state == s]]
        # Recur for all the vertices adjacent to this vertex
        for v in adjacent_vertices:
            # If v is not visited yet, then make it a child of u
            # in DFS tree and recur for it
            if visited[v] == False:
                parent[v] = u
                children += 1
                self.APUtil(v, visited, ap, parent, low, disc)

                # Check if the subtree rooted with v has a connection to
                # one of the ancestors of u
                low[u] = min(low[u], low[v])

                # u is an articulation point in following cases
                # (1) u is root of DFS tree and has two or more chilren.
                if parent[u] == -1 and children > 1:
                    ap[u] = True

                # (2) If u is not root and low value of one of its child is more
                # than discovery value of u.
                if parent[u] != -1 and low[v] >= disc[u]:
                    ap[u] = True

            # Update low value of u for parent function calls
            elif v != parent[u]:
                low[u] = min(low[u], disc[v])

    def _check_if_articulation_point(self, state):
        # Mark all the vertices as not visited
        # and Initialize parent and visited,
        # and ap(articulation point) arrays
        visited = {}
        disc = {}
        low = {}
        parent = {}
        ap = {}  # To store articulation points
        for s in self.states:
            visited[s] = False
            disc[s] = float("Inf")
            low[s] = float("Inf")
            parent[s] = None
            ap[s] = False
        self.aputils_time = 0
        # Call the recursive helper function
        # to find articulation points
        # in DFS tree rooted with vertex 'i'
        for i in self.states:
            if not visited[i]:
                self.APUtil(i, visited, ap, parent, low, disc)
        return ap[state]
