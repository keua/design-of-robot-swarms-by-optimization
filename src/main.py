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
    # parse the paths for the executables and the scenario
    config["path_to_AutoMoDe_FSM"] = config_parser["Installation"]["path_to_AutoMoDe_FSM"]
    config["path_to_AutoMoDe_BT"] = config_parser["Installation"]["path_to_AutoMoDe_BT"]
    config["path_to_scenario"] = config_parser["Scenario"]["path_to_scenario"]
    # the configuration for running
    config["working_directory"] = config_parser["Execution"]["working_directory"]
    config["max_improvements"] = int(config_parser["Execution"]["max_improvements"])
    config["num_runs"] = int(config_parser["Execution"]["num_runs"])
    # parse the window size and movement
    config["seed_window_size"] = int(config_parser["Seed window"]["size"])
    config["seed_window_movement"] = int(config_parser["Seed window"]["movement"])
    # parse the controller configuration
    config["controller_type"] = config_parser["Controller"]["controller_type"]
    config["initial_controller"] = config_parser["Controller"]["initial_controller"]
    # parse information related to the FSM
    config["initial_FSM_file"] = config_parser["FSM"]["initial_FSM_file"]
    # parse information related to the BT
    config["BT_max_actions"] = int(config_parser["BT"]["max_actions"])
    # parse logging configuration
    config["verbose"] = config_parser["Logging"].getboolean("verbose")
    config["snapshot_frequency"] = int(config_parser["Logging"]["snapshot_frequency"])


def create_directory():
    os.chdir(config["working_directory"])
    str_time = datetime.now().strftime("%Y%m%d-%H:%M:%S")
    os.mkdir(str_time)
    os.chdir(str_time)


def set_parameters_fsm():
    FSM.path_to_automode_executable = config["path_to_AutoMoDe"]
    FSM.scenario_file = config["path_to_scenario"]


def set_parameters_bt():
    BT.path_to_automode_executable = config["path_to_AutoMoDe_BT"]
    BT.scenario_file = config["path_to_scenario"]
    BT.parameters["max_actions"] = config["BT_max_actions"]


def set_parameters():
    # TODO: Initialize all controller types
    set_parameters_fsm()
    set_parameters_bt()


def automode_localsearch():
    load_config()
    create_directory()
    set_parameters()
    controller_list = []
    if config["initial_controller"] == "from_file":
        # preload the possible initial controller
        with open(config["initial_FSM_file"]) as f:  # TODO: Load from correct file here
            initial_count = 0
            for line in f:
                tmp = FSM.parse_from_commandline_args(line.strip().split(" "))
                # tmp.draw_graph("Vanilla_"+str(initial_count))
                controller_list.append(tmp)
                initial_count += 1
    # Run local search
    # TODO: Get the right class here to run the localsearch with
    for i in range(0, config["num_runs"]):
        # generate initial FSM
        if config["initial_controller"]:
            initial_controller = BT()
        else:
            initial_controller = random.choice(controller_list)
        os.mkdir("run_{}".format(i))
        os.chdir("run_{}".format(i))
        initial_controller.draw("initial")
        result = run_local_search(initial_controller)
        result.draw("final")
        print(result.convert_to_commandline_args())
        os.chdir("..")


if __name__ == "__main__":
    automode_localsearch()
