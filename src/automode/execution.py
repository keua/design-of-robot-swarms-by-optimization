import statistics
# import mpi4py.futures
from configuration import Configuration
import subprocess
from logging.Logger import Logger


class AutoMoDeExecutor:

    instance = None

    def __init__(self):
        # TODO: Configure this
        self.score_aggregation = statistics.mean  # this can be any function to get a single data point out of
        self.use_mpi = False

        self.path_to_AutoMoDe_executable = Configuration.instance.path_to_AutoMoDe
        self.scenario_file = Configuration.instance.path_to_scenario
        # if self.use_mpi:
        #     self.mpi_pool = mpi4py.futures.MPIPoolExecutor()

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
        scores = []
        # prepare the set of seeds that need to be evaluated
        evaluate_seeds = []
        for seed in seeds:
            if (seed not in controller.evaluated_instances) or reevaluate_seeds:
                evaluate_seeds.append(seed)
        # evaluate the controller on the set of seeds
        if self.use_mpi:
            pass
        else:
            for seed in evaluate_seeds:
                self.execute_controller(controller, seed)
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
        Logger.instance.log_debug("Evaluating BT " + " on seed " + str(seed))
        # prepare the command line
        args = [self.path_to_AutoMoDe_executable, "-n", "-c", self.scenario_file, "--seed", str(seed)]
        args.extend(controller.convert_to_commandline_args())
        Logger.instance.log_debug(args)
        # Run and capture output
        p = subprocess.Popen(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        (stdout, stderr) = p.communicate()
        # Analyse result
        output = stdout.decode('utf-8')
        lines = output.splitlines()
        try:
            Logger.instance.log_debug(lines[len(lines) - 1])
            score = float(lines[len(lines) - 1].split(" ")[1])
        except:
            score = -1  # Just to be sure
            Logger.instance.log_error("Args: " + str(args))
            Logger.instance.log_error("Stderr: " + stderr.decode('utf-8'))
            Logger.instance.log_error("Stdout: " + stdout.decode('utf-8'))
            raise
        controller.evaluated_instances[seed] = score
        Logger.instance.log_verbose("Controller {} on seed {} returned score: {}".format(
            "", seed, controller.evaluated_instances[seed]))

