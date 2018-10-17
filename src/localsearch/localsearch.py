from datetime import datetime
import os
import copy
import logging
from config.configuration import Configuration
from execution import ExecutorFactory

budget = 0


def iterative_improvement(initial_controller):
    """
    The iterative improvement method, that improves upon the initial_controller
    :param initial_controller: The controller that is used to first improve from
    :return: The best controller after the iterative improvement
    """
    best = initial_controller
    start_time = datetime.now()
    logging.info("Started at " + str(start_time))
    if not os.path.isdir("scores"):
        os.mkdir("scores")
    with open("scores/best_score.csv", "w") as file:
        executor = ExecutorFactory.get_executor()
        executor.create_seeds()
        best.evaluate()
        logging.debug("Initial best score " + str(best.score))
        for i in range(0, Configuration.instance.max_improvements):
            # move the window
            executor.advance_seeds()
            # create a mutated FSM
            mutated_controller = copy.deepcopy(best)
            # it is necessary to remove all evaluations from here
            mutated_controller.evaluated_instances.clear()
            mutated_controller.id = i
            mutated_controller.mutate()
            # evaluate both FSMs on the seed_window
            best.evaluate()
            mutated_controller.evaluate()
            # save the scores to file
            file.write(str(best.score) + ", " + str(mutated_controller.score) + ", " +
                       mutated_controller.mut_history[len(mutated_controller.mut_history) - 1].__name__ + "\n")
            logging.debug(
                "Best score " + str(best.score) + " and new score " + str(mutated_controller.score))
            if best.score < mutated_controller.score:  # < for max
                logging.debug(
                    mutated_controller.mut_history[len(mutated_controller.mut_history) - 1].__name__)
                mutated_controller.draw(str(i))
                best = mutated_controller
            if i % Configuration.instance.snapshot_frequency == 0:
                best.draw(str(i))
        end_time = datetime.now()
    logging.info("Finished at " + str(end_time))
    time_diff = end_time - start_time
    logging.info("Took " + str(time_diff))
    return best
