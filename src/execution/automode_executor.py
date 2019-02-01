import subprocess
import logging
import random
from abc import ABCMeta, abstractmethod

import stats
import settings


class ExecutorFactory:
    """
    A factory class to get the correct executor to submit the controllers to.
    """

    @staticmethod
    def get_executor():
        """
        Returns an instance of the executor that should be used.
        :return:
        """
        if settings.parallelization == "sequential":
            return SequentialExecutor()
        if settings.parallelization == "multiprocessing":
            return MultiProcessingExecutor()
        if settings.parallelization == "MPI":
            return MPIExecutor()
        return None


class AutoMoDeExecutor:
    """
    Abstract class for "executors".
    When created it sets up everything necessary for execution.
    Subclass and implement this class to define the way in which the execution is distributed.
    """

    __metaclass__ = ABCMeta

    def __init__(self):
        if settings.architecture == "BT":
            self.path_to_AutoMoDe_executable = settings.BT_path_to_AutoMoDe
        elif settings.architecture == "FSM":
            self.path_to_AutoMoDe_executable = settings.FSM_path_to_AutoMoDe
        else:
            logging.warning("Unknown architecture {}".format(settings.architecture))
            self.path_to_AutoMoDe_executable = "/path/to/AutoMoDe"
        self.scenario_file = settings.path_to_scenario

        self.seed_window_size = settings.seed_window_size
        self.seed_window_move = settings.seed_window_movement
        self.seeds = []
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

    def evaluate_controller(self, controller, reevaluate_seeds=False):
        """
        Evaluate this controller on the current seed set.
        This function will return the set of scores, but will also already have set everything on the controller.
        That means specifically that you don't need set the controller.scores with whatever this method returns.
        :param controller: the controller to be evaluated
        :param reevaluate_seeds:
        :return: the list of scores,
        """
        evaluate_seeds = self.prepare_seeds(controller, reevaluate_seeds)
        self._evaluate(controller, evaluate_seeds)  # returns the evaluated scores, but we don't care
        scores = []
        for seed in self.seeds:
            scores.append(controller.evaluated_instances[seed])
        controller.scores = scores
        return None

    @abstractmethod
    def _evaluate(self, controller, seeds):
        """
        Evaluate a controller on the supplied set of seeds.
        Override this to implement how exactly it is handled.
        :param controller: The controller that should be evaluated
        :param seeds: The set of seeds that need to be evaluated
        :return: a list of scores, achieved on the instances
        """

    def execute_controller(self, controller_args, seed):
        """
        Executes the supplied controller on the supplied seed.
        :param controller_args: The controller to be executed, already in command line format
        :param seed: The seed with which the controller is executed
        :return: The score of controller with the given seed (which is also saved in the controller)
        """
        # print("Evaluating BT " + str(self.id) + " on seed " + str(seed))
        logging.debug("Evaluating controller on seed {}".format(seed))
        # prepare the command line
        args = [self.path_to_AutoMoDe_executable, "-n", "-c", self.scenario_file, "--seed", str(seed)]
        args.extend(controller_args)
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

    def _evaluate(self, controller, seeds):
        # evaluate the controller on the set of seeds
        controller_args = controller.convert_to_commandline_args()
        scores = []
        for seed in seeds:
            _, score = self.execute_controller(controller_args, seed)
            controller.evaluated_instances[seed] = score
            scores.append(score)
        return scores


class MultiProcessingExecutor(AutoMoDeExecutor):
    """
    An implementation of the abstract class AutoMoDeExecutor that runs all instances using the multiprocessing module
    """

    def _evaluate(self, controller, seeds):
        import multiprocessing
        results = []
        cmd = controller.convert_to_commandline_args()
        pool = multiprocessing.Pool(processes=settings.parallel)
        for s in seeds:
            results.append(pool.apply_async(
                self.execute_controller,
                (cmd, s,)))
        pool.close()
        pool.join()
        scores = []
        for r in results:
            seed, score = r.get()
            controller.evaluated_instances[seed] = score
            scores.append(score)
        return scores


class MPIExecutor(AutoMoDeExecutor):
    """
    An implementation of the abstract class AutoMoDeExecutor that runs all instances using the mpi4py package
    """

    def _evaluate(self, controller, seeds):
        import mpi4py.futures
        results = []
        cmd = controller.convert_to_commandline_args()
        pool = mpi4py.futures.MPIPoolExecutor(max_workers=settings.parallel)
        for s in seeds:
            results.append(pool.submit(
                self.execute_controller,
                *(cmd, s)))
        pool.shutdown(wait=True)
        scores = []
        for future in results:
            if future.exception() is not None:
                raise future.exception()
            seed, score = future.result()
            controller.evaluated_instances[seed] = score
            scores.append(score)
        return scores
