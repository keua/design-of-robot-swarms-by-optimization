import subprocess
import logging
import random
from abc import ABCMeta, abstractmethod

# from mpi4py.futures import MPIPoolExecutor

import stats
import settings


class AutoMoDeExecutor:
    """
    Abstract executor class that defines many useful methods.
    Override to implement the details on how the evaluation is distributed.
    """

    __metaclass__ = ABCMeta

    def __init__(self, path_to_AutoMoDe_executable="/path/to/AutoMoDe/",
                 scenario_file="/path/to/scenario"):
        self.path_to_AutoMoDe_executable = path_to_AutoMoDe_executable
        self.scenario_file = scenario_file

        self.seed_window_size = settings.seed_window_size
        self.seed_window_move = settings.seed_window_movement
        self.create_seeds()

    def create_seeds(self):
        """
        Creates a list of self.seed_window_size seeds
        """
        self.seeds = random.sample(range(2147483647), self.seed_window_size)

    def advance_seeds(self):
        """
        Moves the self.seeds by self.seed_window_move seeds.
        """
        for _ in range(0, self.seed_window_move):
            self.seeds.pop(0)
            self.seeds.append(random.randint(0, 2147483647))

    def prepare_seeds(self, controller, reevaluate_seeds):
        """
        Prepares the seeds that need to be evaluated
        :param controller: The controller instance to be evaluated
        :param reevaluate_seeds: boolean indicating if all seeds should be reevaluated or if all results may be used
        :return: a list of seeds that still need to be evaluated
        """
        # prepare the set of seeds that need to be evaluated
        evaluate_seeds = []
        for seed in self.seeds:
            if (seed not in controller.evaluated_instances) or reevaluate_seeds:
                evaluate_seeds.append(seed)
        return evaluate_seeds

    @abstractmethod
    def evaluate_controller(self, controller, reevaluate_seeds=False):
        """
        Evaluate this controller on the current seed set
        :param controller: the controller to be evaluated
        :param reevaluate_seeds:
        :return:
        """
        pass

    def execute_controller(self, controller, seed):
        """
        Executes the supplied controller on the supplied seed.
        :param controller: The controller to be executed
        :param seed: The seed with which the controller is executed
        :return: The score of controller with the given seed (which is also saved in the controller)
        """
        # print("Evaluating BT " + str(self.id) + " on seed " + str(seed))
        logging.debug("Evaluating controller on seed {}".format(seed))
        # prepare the command line
        args = [self.path_to_AutoMoDe_executable, "-n", "-c", self.scenario_file, "--seed", str(seed)]
        args.extend(controller.convert_to_commandline_args())
        logging.debug(args)
        # Run and capture output
        stats.time.start_simulation()
        p = subprocess.Popen(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        (stdout, stderr) = p.communicate()
        stats.time.end_simulation()
        # Analyse result
        output = stdout.decode('utf-8')
        lines = output.splitlines()
        try:
            logging.debug(lines[len(lines) - 1])
            score = float(lines[len(lines) - 1].split(" ")[1])
        except:
            score = -1  # Just to be sure
            logging.error("arguments: {}".format(args))
            logging.error("stderr: {}".format(stderr.decode('utf-8')))
            logging.error("stdout: {}".format(stdout.decode('utf-8')))
            raise
        logging.debug("Controller {} on seed {} returned score: {}".format("", seed, score))
        return seed, score


class SequentialExecutor(AutoMoDeExecutor):
    """
    An implementation of the abstract class AutoMoDeExecutor that runs all instances sequentially
    """

    def evaluate_controller(self, controller, reevaluate_seeds=False):
        evaluate_seeds = self.prepare_seeds(controller, reevaluate_seeds)
        # evaluate the controller on the set of seeds
        for seed in evaluate_seeds:
            _, score = self.execute_controller(controller, seed)
            controller.evaluated_instances[seed] = score
        # return the score
        scores = []
        for seed in self.seeds:
            scores.append(controller.evaluated_instances[seed])
        return scores
