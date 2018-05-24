import configparser
import os
import copy
from datetime import datetime
import random
from automode.controller import FSM, BT

config = {}


def run_local_search(controller):
    best = controller
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
            mutated_controller = copy.deepcopy(best)
            # it is necessary to remove all evaluations from here
            mutated_controller.evaluated_instances.clear()
            mutated_controller.id = i
            mutated_controller.mutate()
            # evaluate both FSMs on the seed_window
            best.evaluate(seed_window)
            mutated_controller.evaluate(seed_window)
            # save the scores to file
            file.write(str(best.score) + ", " + str(mutated_controller.score) + ", " +
                       mutated_controller.mut_history[len(mutated_controller.mut_history) - 1].__name__ + "\n")
            if config["verbose"]:
                print("Best score " + str(best.score) + " and new score " + str(mutated_controller.score))
            if best.score <= mutated_controller.score:  # < for max
                if config["verbose"]:
                    print(mutated_controller.mut_history[len(mutated_controller.mut_history) - 1].__name__)
                    mutated_controller.draw(str(i))
                best = mutated_controller
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
    config["path_to_AutoMoDe_BT"] = config_parser["AutoMoDe_BT-Installation"]["path_to_AutoMoDe"]


def create_directory():
    os.chdir(config["working_directory"])
    str_time = datetime.now().strftime("%Y%m%d-%H:%M:%S")
    os.mkdir(str_time)
    os.chdir(str_time)


def set_executable_paths():
    # TODO: Set paths for every executable type
    FSM.path_to_automode_executable = config["path_to_AutoMoDe"]
    FSM.scenario_file = config["path_to_scenario"]

    BT.path_to_automode_executable = config["path_to_AutoMoDe_BT"]
    BT.scenario_file = config["path_to_scenario"]


def automode_localsearch():
    load_config()
    create_directory()
    set_executable_paths()
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
            initial_controller = BT()
        else:
            initial_controller = random.choice(fsm_list)
        os.mkdir("run_{}".format(i))
        os.chdir("run_{}".format(i))
        initial_controller.draw("initial")
        result = run_local_search(initial_controller)
        result.draw("final")
        print(result.convert_to_commandline_args())
        os.chdir("..")


if __name__ == "__main__":
    automode_localsearch()
