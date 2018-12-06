import subprocess
import logging
from mpi4py.futures import MPIPoolExecutor
import execution
import random


class AutoMoDeExecutor:

    def __init__(self):

        self.path_to_AutoMoDe_executable = "/tmp/"
        self.scenario_file = "/tmp/"

        self.architecture = "undefined"

        self.seed_window_size = 0
        self.seed_window_move = 0
        self.seeds = list()
        self.create_seeds()

    def create_seeds(self):
        """
        Creates a list of self.seed_window_size seeds
        """
        self.seeds = list()
        for i in range(0, self.seed_window_size):
            self.seeds.append(random.randint(0, 2147483647))

    def advance_seeds(self):
        """
        Moves the self.seeds by self.seed_window_move seeds.
        """
        for i in range(0, self.seed_window_move):
            self.seeds.pop(0)
            self.seeds.append(random.randint(0, 2147483647))

    def evaluate_controller(self, controller, reevaluate_seeds=False):
        """
        Evaluates a controller on a set of seeds
        :param controller: The controller to be evaluated
        :param seeds: The set of seeds that are evaluated
        :param reevaluate_seeds: Indicates if already evaluated seeds are evaluated again. False by default.
        :return: An aggregate of the scores for each seed
        """

        def sequential_execution():
            for s in evaluate_seeds:
                self.execute_controller(controller, s)

        def parallel_execution():
            # execute the parallel_automode.R script
            pass
            # TODO: Fix this to not use so much memory or run for ever
            with MPIPoolExecutor(max_workers=5) as executor:
                for s in evaluate_seeds:
                    future = executor.submit(self.execute_controller, controller, s)
                    future.add_done_callback(parallel_execution_done)

        def parallel_execution_done(future):
            if future.exception() is not None:
                raise future.exception()
            seed, score = future.result()
            controller.evaluated_instances[seed] = score

        scores = []
        # prepare the set of seeds that need to be evaluated
        evaluate_seeds = []
        for seed in self.seeds:
            if (seed not in controller.evaluated_instances) or reevaluate_seeds:
                evaluate_seeds.append(seed)
        # evaluate the controller on the set of seeds
        if execution.mpi_enabled:
            parallel_execution()
        else:
            sequential_execution()
        # return the score
        for seed in self.seeds:
            scores.append(controller.evaluated_instances[seed])
        controller.scores = scores
        return controller.scores

    def execute_controller(self, controller, seed):
        """
        Executes the supplied controller on the supplied seed.
        :param controller: The controller to be executed
        :param seed: The seed with which the controller is executed
        :return: The score of controller with the given seed (which is also saved in the controller)
        """
        # print("Evaluating BT " + str(self.id) + " on seed " + str(seed))
        logging.debug("Evaluating controller " + " on seed " + str(seed))
        # prepare the command line
        args = [self.path_to_AutoMoDe_executable, "-n", "-c", self.scenario_file, "--seed", str(seed)]
        args.extend(controller.convert_to_commandline_args())
        logging.debug(args)
        # Run and capture output
        p = subprocess.Popen(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        (stdout, stderr) = p.communicate()
        # Analyse result
        output = stdout.decode('utf-8')
        lines = output.splitlines()
        try:
            logging.debug(lines[len(lines) - 1])
            score = float(lines[len(lines) - 1].split(" ")[1])
        except:
            score = -1  # Just to be sure
            logging.error("Args: " + str(args))
            logging.error("Stderr: " + stderr.decode('utf-8'))
            logging.error("Stdout: " + stdout.decode('utf-8'))
            raise
        controller.evaluated_instances[seed] = score
        logging.debug("Controller {} on seed {} returned score: {}".format(
            "", seed, controller.evaluated_instances[seed]))
        return seed, score
