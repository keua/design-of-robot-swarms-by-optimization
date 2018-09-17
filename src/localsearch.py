from datetime import datetime
import os
import random
import copy
from simple_logging import Logger
from configuration import Configuration


def iterative_improvement(initial_controller):
    best = initial_controller
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
            Logger.instance.log_verbose(
                "Best score " + str(best.score) + " and new score " + str(mutated_controller.score))
            if best.score < mutated_controller.score:  # < for max
                Logger.instance.log_verbose(
                    mutated_controller.mut_history[len(mutated_controller.mut_history) - 1].__name__)
                mutated_controller.draw(str(i))
                best = mutated_controller
            if i % Configuration.instance.snapshot_frequency == 0:
                best.draw(str(i))
        end_time = datetime.now()
    Logger.instance.log("Finished at " + str(end_time))
    time_diff = end_time - start_time
    Logger.instance.log_verbose("Took " + str(time_diff))
    return best
