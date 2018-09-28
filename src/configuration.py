import configparser
from simple_logging import Logger


class Configuration:

    instance = None

    def __init__(self):
        # Settings passed from the terminal
        self.path_to_scenario = "/tmp/"
        self.config_file_name = "config.ini"
        self.src_directory = "src/"
        self.result_directory = "default/"
        self.initial_controller = "None"
        self.job_name = "default"
        self.controller_type = "None"
        # Settings read from the file
        self.max_improvements = 0
        self.num_runs = 0
        self.MPI = False
        self.seed_window_size = 0
        self.seed_window_movement = 0
        self.controller_minimal_behavior = "None"
        self.controller_minimal_condition = "None"
        self.random_parameter_initialization = True
        self.FSM_path_to_AutoMoDe = "/tmp/"
        self.FSM_max_states = 0
        self.FSM_max_transitions = 0
        self.FSM_max_transitions_per_state = 0
        self.FSM_no_self_transition = True
        self.BT_path_to_AutoMoDe = "/tmp/"
        self.BT_max_actions = 0
        self.snapshot_frequency = 0
        self.log_level = "INFO"
        Configuration.instance = self

    @staticmethod
    def load_from_file(config_file_name):

        """
        Sets the files from the specified file.
        :param config_file_name: The file containing the configuration. If a path is given, it needs to be relative
        to the src/ folder.
        """

        # TODO: Add checks to values

        def load_run_configuration():
            # the configuration for running
            config.max_improvements = int(config_parser["Execution"]["max_improvements"])
            config.num_runs = int(config_parser["Execution"]["num_runs"])
            config.MPI = config_parser["Execution"].getboolean("use_mpi")
            # parse the window size and movement
            config.seed_window_size = int(config_parser["Seed window"]["size"])
            config.seed_window_movement = int(config_parser["Seed window"]["movement"])

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

        if Configuration.instance is None:
            config = Configuration()  # only create a new object if it hasn't been created yet
        else:
            config = Configuration.instance

        config_parser = configparser.ConfigParser()
        config_parser.read(config_file_name)
        load_run_configuration()
        load_controller_configuration()
        # parse logging configuration
        config.snapshot_frequency = int(config_parser["Logging"]["snapshot_frequency"])
        config.log_level = config_parser["Logging"]["log_level"]

