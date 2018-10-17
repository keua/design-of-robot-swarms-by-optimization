import configparser


class Configuration:

    def __init__(self):
        # Default Values
        self.default_path_to_scenario = "/tmp/scenario"
        self.default_budget = 0
        self.default_result_directory = "/tmp/result"
        # Execution
        self.seed_window_size = 0
        self.seed_window_movement = 0
        # Controller
        self.controller_minimal_behavior = "None"
        self.controller_minimal_condition = "None"
        self.random_parameter_initialization = True
        # FSM
        self.FSM_path_to_AutoMoDe = "/tmp/FSM_AutoMoDe"
        self.FSM_max_states = 0
        self.FSM_max_transitions = 0
        self.FSM_max_transitions_per_state = 0
        self.FSM_no_self_transition = True
        # BT
        self.BT_path_to_AutoMoDe = "/tmp/BT_AutoMoDe"
        self.BT_max_actions = 0
        # Logging
        self.snapshot_frequency = 0
        self.log_level = "INFO"
        Configuration.instance = self

    @staticmethod
    def load_from_file(config_file_name):

        """
        Sets the files from the specified file.
        :param config_file_name: The file containing the configuration. If a path is given, it needs to be relative
        to the src/ folder.
        :return: a config object containing all necessary information. This object is not thought for persistence
        """

        # TODO: Add checks to values

        def load_default_values():
            config.default_path_to_scenario = config_parser["Default Values"]["path_to_scenario"]
            config.default_result_directory = config_parser["Default Values"]["result_directory"]
            config.default_budget = int(config_parser["Default Values"]["budget"])

        def load_run_configuration():
            # parse the window size and movement
            config.seed_window_size = int(config_parser["Execution"]["seed_window_size"])
            config.seed_window_movement = int(config_parser["Execution"]["seed_window_movement"])

        def load_controller_configuration():
            # parse the controller configuration
            config.controller_minimal_behavior = config_parser["Controller"]["minimal_behavior"]
            config.controller_minimal_condition = config_parser["Controller"]["minimal_condition"]
            config.random_parameter_initialization = config_parser["Controller"].getboolean(
                "random_parameter_initialization")
            # parse information related to the FSM
            config.FSM_path_to_AutoMoDe = config_parser["FSM"]["path_to_AutoMoDe"]
            config.FSM_max_states = int(config_parser["FSM"]["max_states"])
            config.FSM_max_transitions = float(config_parser["FSM"]["max_transitions"])
            config.FSM_max_transitions_per_state = int(config_parser["FSM"]["max_transitions_per_state"])
            config.FSM_no_self_transition = config_parser["FSM"].getboolean("no_self_transition")
            # parse information related to the BT
            config.BT_path_to_AutoMoDe = config_parser["BT"]["path_to_AutoMoDe"]
            config.BT_max_actions = int(config_parser["BT"]["max_actions"])

        config = Configuration()
        config_parser = configparser.ConfigParser()
        config_parser.read(config_file_name)
        load_default_values()
        load_run_configuration()
        load_controller_configuration()
        # parse logging configuration
        config.snapshot_frequency = int(config_parser["Logging"]["snapshot_frequency"])
        config.log_level = config_parser["Logging"]["log_level"]
        return config

