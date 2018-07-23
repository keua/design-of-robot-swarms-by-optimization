import configparser


class Configuration:

    instance = None

    def __init__(self):
        self.path_to_AutoMoDe = "/tmp/"
        self.path_to_scenario = "/tmp/"
        self.working_directory = "/tmp/"
        self.max_improvements = 0
        self.num_runs = 0
        self.seed_window_size = 0
        self.seed_window_movement = 0
        self.controller_type = "None"
        self.initial_controller = "None"
        self.initial_FSM_file = "/tmp/"
        self.FSM_max_states = 0
        self.FSM_max_transitions = 0
        self.FSM_max_transitions_per_state = 0
        self.FSM_no_self_transition = True
        self.FSM_initial_state_behavior = "None"
        self.FSM_random_parameter_initialization = True
        self.verbose = False
        self.snapshot_frequency = 1
        Configuration.instance = self

    @staticmethod
    def load_from_file(config_file_name):

        # TODO: Add checks to values

        def load_execution_configuration():
            # parse the paths for the executables and the scenario
            config.path_to_AutoMoDe = config_parser["Installation"]["path_to_AutoMoDe"]
            config.path_to_scenario = config_parser["Scenario"]["path_to_scenario"]

        def load_run_configuration():
            # the configuration for running
            config.working_directory = config_parser["Execution"]["working_directory"]
            config.max_improvements = int(config_parser["Execution"]["max_improvements"])
            config.num_runs = int(config_parser["Execution"]["num_runs"])
            # parse the window size and movement
            config.seed_window_size = int(config_parser["Seed window"]["size"])
            config.seed_window_movement = int(config_parser["Seed window"]["movement"])

        def load_controller_configuration():
            # parse the controller configuration
            config.controller_type = config_parser["Controller"]["controller_type"]
            config.initial_controller = config_parser["Controller"]["initial_controller"]
            if config.initial_controller not in ["minimal"]:
                print("Unrecognized configuration for initial_controller: {}".format(config.initial_controller))
            # parse information related to the FSM
            config.initial_FSM_file = config_parser["FSM"]["initial_FSM_file"]
            config.FSM_max_states = int(config_parser["FSM"]["max_states"])
            config.FSM_max_transitions = float(config_parser["FSM"]["max_transitions"])
            config.FSM_max_transitions_per_state = int(config_parser["FSM"]["max_transitions_per_state"])
            config.FSM_no_self_transition = config_parser["FSM"].getboolean("no_self_transition")
            config.FSM_initial_state_behavior = config_parser["FSM"]["initial_state_behavior"]
            config.FSM_random_parameter_initialization = config_parser["FSM"].getboolean(
                "random_parameter_initialization")
            # parse information related to the BT
            config.BT_max_actions = int(config_parser["BT"]["max_actions"])

        config = Configuration()
        config_parser = configparser.ConfigParser()
        config_parser.read(config_file_name)
        load_execution_configuration()
        load_run_configuration()
        load_controller_configuration()
        # parse logging configuration
        config.verbose = config_parser["Logging"].getboolean("verbose")
        config.snapshot_frequency = int(config_parser["Logging"]["snapshot_frequency"])

