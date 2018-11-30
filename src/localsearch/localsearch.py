from datetime import datetime
import os
import copy
import logging
from config.configuration import Configuration
import execution
import math

from . import acceptance_criteria as ac

budget = 50000


def iterative_improvement(initial_controller):
    """
    The iterative improvement method, that improves upon the initial_controller
    :param initial_controller: The controller that is used to first improve from
    :return: The best controller after the iterative improvement
    """
    executor = execution.get_executor()
    max_improvements = math.floor(
        budget/(executor.seed_window_size + executor.seed_window_move))
    logging.warning("{}".format(max_improvements))
    best_controller = initial_controller
    acceptance = ac.mean
    start_time = datetime.now()
    logging.info("Started at " + str(start_time))
    if not os.path.isdir("scores"):
        os.mkdir("scores")
    with open("scores/best_score.csv", "w") as file:
        executor.create_seeds()
        best_controller.evaluate()
        logging.debug("Initial best scores " + str(best_controller.scores))
        for i in range(0, max_improvements):
            logging.warning("{}".format(i))
            # move the window
            executor.advance_seeds()
            # create a mutated FSM
            mutated_controller = copy.deepcopy(best_controller)
            # it is necessary to remove all evaluations from here
            mutated_controller.evaluated_instances.clear()
            mutated_controller.id = i
            mutated_controller.mutate()
            # evaluate both FSMs on the seed_window
            best_controller.evaluate()
            mutated_controller.evaluate()
            # Evaluate criterion
            criterion = \
                acceptance(best_controller.scores, mutated_controller.scores)
            # save the scores to file and update contrllers
            best_controller.agg_score = (criterion.type, criterion.best_outcome)
            mutated_controller.agg_score = (criterion.type, criterion.mut_outcome)
            file.write(
                str(best_controller.scores) +
                ", " + criterion.type + " = " + str(criterion.best_outcome) +
                ", " + str(mutated_controller.scores) +
                ", " + criterion.type + " = " + str(criterion.mut_outcome) +
                ", " + mutated_controller.mut_history[len(mutated_controller.mut_history) - 1].__name__ +
                "\n"
            )
            logging.debug(
                "Best score " + str(best_controller.scores) +
                " and new score " + str(mutated_controller.scores)
            )
            if criterion.acceptance:
                logging.debug(
                    mutated_controller.mut_history[len(
                        mutated_controller.mut_history) - 1].__name__
                )
                mutated_controller.draw(str(i))
                best_controller = mutated_controller
            if i % Configuration.instance.snapshot_frequency == 0:
                best_controller.draw(str(i))
        end_time = datetime.now()
    logging.info("Finished at " + str(end_time))
    time_diff = end_time - start_time
    logging.info("Took " + str(time_diff))
    return best_controller
