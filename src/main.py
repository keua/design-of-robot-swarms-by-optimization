import configparser
import os
from _datetime import datetime
import random
from AutoModeFSM import FSM

config = {}


def run_local_search(fsm):
    return fsm


def load_config():
    global config
    config_parser = configparser.ConfigParser()
    config_parser.read("config.ini")
    config["path_to_AutoMoDe"] = config_parser["AutoMoDe-Installation"]["path_to_AutoMoDe"]
    config["path_to_scenario"] = config_parser["Scenario"]["path_to_scenario"]
    config["seed_window_size"] = int(config_parser["Seed window"]["size"])
    config["seed_window_movement"] = int(config_parser["Seed window"]["movement"])
    config["working_directory"] = config_parser["Execution"]["working_directory"]
    config["max_improvements"] = int(config_parser["Execution"]["max_improvements"])
    config["initial_FSM_empty"] = config_parser["Execution"].getboolean("initial_FSM_empty")
    config["initial_FSM_file"] = config_parser["Execution"]["initial_FSM_file"]
    config["num_runs"] = int(config_parser["Execution"]["num_runs"])
    config["verbose"] = config_parser["Logging"].getboolean("verbose")
    config["snapshot_frequency"] = int(config_parser["Logging"]["snapshot_frequency"])


if __name__ == "__main__":
    load_config()
    os.chdir(config["working_directory"])
    str_time = datetime.now().strftime("%Y%m%d-%H:%M:%S")
    os.mkdir(str_time)
    os.chdir(str_time)
    # TODO: Set pathes for every executalbe type
    FSM.automode_path = config["path_to_AutoMoDe"]
    FSM.scenario = config["path_to_scenario"]
    fsm_list = []
    if not config["initial_FSM_empty"]:
        # preload the possible initial controller
        with open(config["initial_FSM_file"]) as f:
            initial_count = 0
            for line in f:
                tmp = FSM.parse_from_commandline_args(line.strip().split(" "))
                # tmp.draw_graph("Vanilla_"+str(initial_count))
                fsm_list.append(tmp)
                initial_count += 1
    # Run local search
    for i in range(0, config["num_runs"]):
        # generate initial FSM
        if config["initial_FSM_empty"]:
            initial_FSM = FSM()
        else:
            initial_FSM = random.choice(fsm_list)
        os.mkdir("run_{}".format(i))
        os.chdir("run_{}".format(i))
        initial_FSM.draw("initial")
        result = run_local_search(initial_FSM)
        result.draw("final")

        print(result.convert_to_commandline_args())
        os.chdir("..")