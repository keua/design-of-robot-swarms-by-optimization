import copy
import logging
import math

import stats

import localsearch.acceptance_criteria as ac
import settings
import execution

budget = 50000
snapshot_frequency = 1


def iterative_improvement(initial_controller):
    """
    The iterative improvement method, that improves upon the initial_controller
    :param initial_controller: The controller that is used to first improve from
    :return: The best controller after the iterative improvement
    """
    executor = execution.ExecutorFactory.get_executor()
    max_improvements = math.floor(
        budget/(settings.seed_window_size + settings.seed_window_movement))
    logging.info("number of iterations: {}".format(max_improvements))
    best_controller = initial_controller
    acceptance = ac.mean
    stats.time.start_run()
    logging.info("Started at {}".format(stats.time.start_time))
    stats.performance.prepare_score_files()
    print(settings.architecture)
    best_controller.evaluate(executor)
    logging.debug("Initial best scores {}".format(best_controller.scores))
    for i in range(0, max_improvements):
        logging.debug("Iteration {}".format(i))
        # move the window
        executor.advance_seeds()
        # create a perturbed controller
        perturbed_controller = copy.deepcopy(best_controller)
        # it is necessary to remove all evaluations from here
        perturbed_controller.evaluated_instances.clear()
        perturbed_controller.id = i
        perturbed_controller.perturb()
        # evaluate both FSMs on the seed_window
        best_controller.evaluate(executor)
        perturbed_controller.evaluate(executor)
        # Evaluate criterion
        criterion = acceptance(best_controller.scores, perturbed_controller.scores)
        # save the scores to file and update controllers
        best_controller.agg_score = (criterion.type, criterion.best_outcome)
        perturbed_controller.agg_score = (criterion.type, criterion.perturb_outcome)
        logging.info("Best score {} and new score {}".format(best_controller.agg_score, perturbed_controller.agg_score))
        stats.performance.save_results(best_controller, perturbed_controller)
        if criterion.accepted:
            logging.debug(perturbed_controller.perturb_history[len(perturbed_controller.perturb_history) - 1].__name__)
            perturbed_controller.draw(str(i))
            best_controller = perturbed_controller
        if i % snapshot_frequency == 0:
            best_controller.draw(str(i))
    stats.time.end_run()
    logging.info("Finished at {}".format(stats.time.end_time))
    logging.warning("Total time: {}".format(stats.time.elapsed_time()))
    logging.warning("Time in simulation: {}".format(stats.time.simulation_time))
    stats.save()
    stats.reset()
    return best_controller
