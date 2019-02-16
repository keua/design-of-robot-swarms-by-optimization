"""
This module allows access to a number of variables that are read from the configuration.py module

DON'T SET THESE VARIABLES BY YOURSELF!
TODO: Look up best practices and follow them
"""

# default values for the settings
ARCHITECTURE_DEFAULT = "undefined architecture"

SCENARIO_DEFAULT = "/path/to/scenario/missing.argos"
BUDGET_DEFAULT = -1
RESULT_DEFAULT = "/tmp/AutoMoDe-LocalSearch/results/"

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

PARALLEL_DEFAULT = -1
PARALLELIZATION_DEFAULT = "NoParallelization"
