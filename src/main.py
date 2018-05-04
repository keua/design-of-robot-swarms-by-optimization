import configparser
import os
import copy
from datetime import datetime
import random
from automode.controller import FSM, BT

config = {}


def run_local_search(fsm):
    best = initial_FSM
    if config["verbose"]:
        start_time = datetime.now()
        print("Started at " + str(start_time))
    if not os.path.isdir("scores"):
        os.mkdir("scores")
    with open("scores/best_score.csv", "w") as file:
        seed_window = list()
        for i in range(0, config["seed_window_size"]):
            seed_window.append(random.randint(0, 2147483647))
        best.evaluate(seed_window)
        for i in range(0, config["max_improvements"]):
            # move the window
            for j in range(0, config["seed_window_movement"]):
                seed_window.pop(0)
                seed_window.append(random.randint(0, 2147483647))
            # create a mutated FSM
            FSM2 = copy.deepcopy(best)
            # it is necessary to remove all evaluations from here
            FSM2.evaluated_instances.clear()
            FSM2.id = i
            FSM2.mutate()
            # evaluate both FSMs on the seed_window
            best.evaluate(seed_window)
            FSM2.evaluate(seed_window)
            # save the scores to file
            file.write(str(best.score) + ", " + str(FSM2.score) + ", " +
                       FSM2.mut_history[len(FSM2.mut_history) - 1].__name__ + "\n")
            if config["verbose"]:
                print("Best score " + str(best.score) + " and new score " + str(FSM2.score))
            if best.score < FSM2.score:  # < for max
                if config["verbose"]:
                    print(FSM2.mut_history[len(FSM2.mut_history) - 1].__name__)
                    FSM2.draw(str(i))
                best = FSM2
            if i % config["snapshot_frequency"] == 0:
                best.draw(str(i))
        end_time = datetime.now()
    if config["verbose"]:
        print("Finished at " + str(end_time))
        time_diff = end_time - start_time
        print("Took " + str(time_diff))
    return best


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
    # TODO: Set paths for every executable type
    FSM.path_to_automode_executable = config["path_to_AutoMoDe"]
    FSM.scenario_file = config["path_to_scenario"]
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