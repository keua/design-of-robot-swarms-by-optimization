import statistics
import subprocess
from simple_logging.simple_logging import SimpleLogger
from mpi4py.futures import MPIPoolExecutor


class AutoMoDeExecutor:

    instance = None

    def __init__(self):
        # TODO: Configure this
        self.score_aggregation = statistics.mean  # this can be any function to get a single data point out of
        self.use_mpi = False

        self.path_to_AutoMoDe_executable = "/tmp/"
        self.scenario_file = "/tmp/"

        # Singleton
        AutoMoDeExecutor.instance = self

    def evaluate_controller(self, controller, seeds, reevaluate_seeds=False):
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
        for seed in seeds:
            if (seed not in controller.evaluated_instances) or reevaluate_seeds:
                evaluate_seeds.append(seed)
        # evaluate the controller on the set of seeds
        if self.use_mpi:
            parallel_execution()
        else:
            sequential_execution()
        # return the score
        for seed in seeds:
            scores.append(controller.evaluated_instances[seed])
        controller.score = self.score_aggregation(scores)
        return controller.score

    def execute_controller(self, controller, seed):
        """
        Executes the supplied controller on the supplied seed.
        :param controller: The controller to be executed
        :param seed: The seed with which the controller is executed
        :return: The score of controller with the given seed (which is also saved in the controller)
        """
        # print("Evaluating BT " + str(self.id) + " on seed " + str(seed))
        SimpleLogger.instance.log_debug("Evaluating BT " + " on seed " + str(seed))
        # prepare the command line
        args = [self.path_to_AutoMoDe_executable, "-n", "-c", self.scenario_file, "--seed", str(seed)]
        args.extend(controller.convert_to_commandline_args())
        SimpleLogger.instance.log_debug(args)
        # Run and capture output
        p = subprocess.Popen(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        (stdout, stderr) = p.communicate()
        # Analyse result
        output = stdout.decode('utf-8')
        lines = output.splitlines()
        try:
            SimpleLogger.instance.log_debug(lines[len(lines) - 1])
            score = float(lines[len(lines) - 1].split(" ")[1])
        except:
            score = -1  # Just to be sure
            SimpleLogger.instance.log_error("Args: " + str(args))
            SimpleLogger.instance.log_error("Stderr: " + stderr.decode('utf-8'))
            SimpleLogger.instance.log_error("Stdout: " + stdout.decode('utf-8'))
            raise
        controller.evaluated_instances[seed] = score
        SimpleLogger.instance.log_verbose("Controller {} on seed {} returned score: {}".format(
            "", seed, controller.evaluated_instances[seed]))
        return seed, score
