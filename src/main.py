import os
import copy
from datetime import datetime
import random
from automode.controller import FSM, BT
import shutil
import argparse
from configuration import Configuration
from automode.execution import AutoMoDeExecutor
from logging.Logger import Logger


config_file_name = "config.ini"
result_directory = "default/"
src_directory = "src/"


def run_local_search(controller):
    best = controller
    start_time = datetime.now()
    Logger.instance.log("Started at " + str(start_time))
    if not os.path.isdir("scores"):
        os.mkdir("scores")
    with open("scores/best_score.csv", "w") as file:
        seed_window = list()
        for i in range(0, Configuration.instance.seed_window_size):
            seed_window.append(random.randint(0, 2147483647))
        best.evaluate(seed_window)
        Logger.instance.log_verbose("Initial best score " + str(best.score))
        for i in range(0, Configuration.instance.max_improvements):
            # move the window
            for j in range(0, Configuration.instance.seed_window_movement):
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
            Logger.instance.log_verbose("Best score " + str(best.score) + " and new score " + str(mutated_controller.score))
            if best.score < mutated_controller.score:  # < for max
                Logger.instance.log_verbose(mutated_controller.mut_history[len(mutated_controller.mut_history) - 1].__name__)
                mutated_controller.draw(str(i))
                best = mutated_controller
            if i % Configuration.instance.snapshot_frequency == 0:
                best.draw(str(i))
        end_time = datetime.now()
    Logger.instance.log("Finished at " + str(end_time))
    time_diff = end_time - start_time
    Logger.instance.log_verbose("Took " + str(time_diff))
    return best


def load_config():
    Configuration.load_from_file(config_file_name)


def create_directory():
    global src_directory
    Logger.instance.log_debug("Directory of this file {}".format(os.path.realpath(__file__)))
    src_directory = os.path.split(os.path.realpath(__file__))[0]
    os.chdir(result_directory)
    str_time = datetime.now().strftime("%Y%m%d-%H:%M:%S")
    exp_dir = "{}_{}".format(config_file_name.split(".")[0], str_time)
    os.mkdir(exp_dir)
    os.chdir(exp_dir)
    # copy the configuration file
    new_config_filename = "config_{}.ini".format(str_time)
    shutil.copyfile("{}/{}".format(src_directory, config_file_name), "{}/{}".format(os.getcwd(), new_config_filename))


def set_parameters_fsm():
    # parameters for the evaluation
    FSM.scenario_file = Configuration.instance.path_to_scenario
    # parameters for the FSM
    FSM.parameters["max_states"] = Configuration.instance.FSM_max_states
    FSM.parameters["max_transitions"] = Configuration.instance.FSM_max_transitions
    FSM.parameters["max_transitions_per_state"] = Configuration.instance.FSM_max_transitions_per_state
    FSM.parameters["no_self_transition"] = Configuration.instance.FSM_no_self_transition
    FSM.parameters["initial_state_behavior"] = Configuration.instance.FSM_initial_state_behavior
    FSM.parameters["random_parameter_initialization"] = Configuration.instance.FSM_random_parameter_initialization


def set_parameters_bt():
    # parameters for the evaluation
    BT.scenario_file = Configuration.instance.path_to_scenario
    # parameters for the BT
    BT.parameters["max_actions"] = Configuration.instance.BT_max_actions


def set_parameters():
    # Initialize all controller types
    set_parameters_fsm()
    set_parameters_bt()


def get_controller_class():
    if Configuration.instance.controller_type == "FSM":
        return FSM
    elif Configuration.instance.controller_type == "BT":
        return BT
    else:
        Logger.instance.log_warning("WARNING: The specified type {} is not known.".format(Configuration.instance.controller_type))
        return None


def parse_input():
    global config_file_name
    global result_directory
    parser = argparse.ArgumentParser(description="Run the local search algorithm")
    parser.add_argument('-c', '--config', dest="config_file", default="config.ini",
                        help="The configuration file for the local search algorithm")
    parser.add_argument('-r', '--result_directory', dest="result_dir", default="result/",
                        help="The directory where the results of the local search algorithm are written")
    input_args = parser.parse_args()
    config_file_name = input_args.config_file
    result_directory = input_args.result_dir


def create_executor():
    executor = AutoMoDeExecutor()


def automode_localsearch():
    logger = Logger()
    parse_input()
    load_config()
    Logger.instance.log_level = Logger.LogLevel[Configuration.instance.log_level]
    create_directory()
    set_parameters()
    create_executor()
    controller_list = []
    if "from_file" in Configuration.instance.initial_controller:  # either from_file or random_from_file
        # preload the possible initial controller
        with open(Configuration.instance.initial_controller_file) as f:
            initial_count = 0
            pre_seed_window = list()
            for i in range(0, Configuration.instance.seed_window_size):
                pre_seed_window.append(random.randint(0, 2147483647))
            for line in f:
                tmp = get_controller_class().parse_from_commandline_args(line.strip().split(" "))
                tmp.draw("Vanilla_"+str(initial_count))
                tmp.evaluate(pre_seed_window)
                Logger.instance.log_verbose("Vanilla_{} scored {}".format(initial_count, tmp.score))
                controller_list.append(tmp)
                initial_count += 1
    # Run local search
    for i in range(0, Configuration.instance.num_runs):
        # generate initial FSM
        if Configuration.instance.initial_controller == "minimal":
            initial_controller = get_controller_class()()
        else:
            initial_controller = controller_list[i]
        os.mkdir("run_{}".format(i))
        os.chdir("run_{}".format(i))
        initial_controller.draw("initial")
        result = run_local_search(initial_controller)
        result.draw("final")
        Logger.instance.log(result.convert_to_commandline_args())
        os.chdir("..")


if __name__ == "__main__":
    automode_localsearch()
