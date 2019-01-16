"""
This module allows access to a number of variables that are read from the configuration.py module

DON'T SET THESE VARIABLES BY YOURSELF!
TODO: Look up best practices and follow them
"""

# default values for the settings
ARCHITECTURE_DEFAULT = "undefined architecture"

SCENARIO_DEFAULT = "/path/to/scenario/missing.argos"
BUDGET_DEFAULT = -1
RESULT_DEFAULT = "/path/to/results/"

SEED_SIZE_DEFAULT = -1
SEED_MOVE_DEFAULT = -1

MINIMAL_BEHAVIOR_DEFAULT = "undefined behavior"
MINIMAL_CONDITION_DEFAULT = "undefined condition"
RANDOM_PARAMETER_DEFAULT = False

FSM_AUTOMODE_DEFAULT = "/path/to/AutoMoDe/bin/automode"
FSM_MAX_STATES_DEFAULT = -1
FSM_MAX_TRANSITIONS_DEFAULT = -1
FSM_MAX_TRANSITIONS_PER_STATE_DEFAULT = -1
FSM_SELF_TRANSITION_DEFAULT = True

BT_AUTOMODE_DEFAULT = "/path/to/AutoMoDe/bin/automode_bt"
BT_MAX_ACTIONS_DEFAULT = -1

SNAPSHOT_FREQUENCY_DEFAULT = -1
LOG_LEVEL_DEFAULT = "NOTHING"

JOB_NAME_DEFAULT = ""


architecture = ""
job_name = ""
initial_controller = ""
config_file_name = ""

path_to_scenario = ""
budget = 1
result_directory = ""

seed_window_size = 0
seed_window_movement = 0

minimal_behavior = ""
minimal_condition = ""
random_parameter_initialization = False

FSM_path_to_AutoMoDe = ""
FSM_max_states = 0
FSM_max_transitions = 0
FSM_max_transitions_per_state = 0
FSM_no_self_transition = True  # TODO: Refactor this setting to positive

BT_path_to_AutoMoDe = ""
BT_max_actions = 0

snapshot_frequency = 0
log_level = ""
