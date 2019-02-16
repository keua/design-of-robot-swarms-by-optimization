#!/usr/bin/env python3

"""
Use this script to start the local search. Run start_localsearch.py -h for more help.
"""
import os
import argparse
import logging
import json
import subprocess
<<<<<<< HEAD
import numpy as np
||||||| merged common ancestors
=======
from datetime import datetime
>>>>>>> msth-kubedaar

import settings
import configuration
from localsearch import iterative_improvement
import localsearch.utilities
from localsearch import SimulatedAnnealing as SA
from localsearch import IterativeImprovement as II


def load_experiment_file(experiment_file):
    """
    Loads the specified experiment file and returns a dictionary containing the values.
    :param experiment_file:
    :return: A dictionary containing the values defined in the experiment file
    """
    # Load the experiment file here
    with open(experiment_file, mode="r") as file:
        content = file.readlines()
    content = [x.strip() for x in content]  # Remove whitespaces
    json_content = ""
    for line in content:
        if not line.startswith("#"):  # ignore lines with # at the beginning
            json_content += "{}\n".format(line)
    logging.debug(json_content)
    data = json.loads(json_content)

    # try to get the global_config file
    global_config_file = data.pop("configuration", None)

    # Handle required and optional parameters like when parsing from sys.argv
    for setup_key in data:
        experiment_setup = data[setup_key]
        print(experiment_setup)
        if global_config_file:  # set the config file if there was a global definition
            experiment_setup["configuration"] = global_config_file
        if "repetitions" not in experiment_setup:  # default check for repetitions
            experiment_setup["repetitions"] = 1
        if "result_directory" not in experiment_setup:
            experiment_setup["result_directory"] = settings.RESULT_DEFAULT
        # TODO: Find other checks that need to be here now
        # if "budget" not in experiment_setup:
        #     experiment_setup["budget"] = BUDGET_DEFAULT
        # if "scenario" not in experiment_setup:
        #     experiment_setup["scenario"] = SCENARIO_DEFAULT

    return data
    """
    Structure of the experiment file: A set of dictionaries that describe subexperiments.
    Each subexperiment has the following information:
    job_name is the key of the dictionary for the subexperiment
    The following entries have to be in the dictionary:
        - configuration: the path to the (complete?) configuration file
        - repetitions: how often this subexperiment is repeated
        - result_directory: the directory the results are written to
    There can be more entries (basically everything that can be in the config file).
    The most likely entries are going to be:
        - scenario: the path to the scenario file
        - initial_controller: the initial controller (or file if it is read from the file)
        - architecture: BT or FSM
    """


def run_local(experiment_file):
    """
    Reads the experiments_file and performs the experiment on the local machine
    """
    experiment_setup = load_experiment_file(experiment_file)
    for setup_key in experiment_setup:  # Execute each experiment
        setup = experiment_setup[setup_key]
        for i in range(int(setup["repetitions"])):  # Execute the repetitions of an experiment
            # retrieve important information
            initial_controller = setup["initial_controller"]
            if not initial_controller == "minimal":
                initial_controller = "{}:{}".format(initial_controller,
                                                    i+1)  # add the current repetition if it is not minimal
            # TODO: only assign those that are necessary
            arguments = {
                "architecture": setup["architecture"],
                "scenario_file": setup["scenario"],
                "initial_controller": initial_controller,
                # create correct jobname
                "job_name": "{}_{}".format(setup_key, i),
                "result_directory": setup["result_directory"],
            }
<<<<<<< HEAD
            if "SimulatedAnnealing" in experiment["sls"]:
                execute_simulated_annealing(experiment)
            elif "IterativeImprovement" in experiment["sls"]:
                # execute localsearch
                # execute_localsearch(experiment)
                execute_iterative_improvement(experiment)
            logging.warning("======== Repetition %d finished ========" % i)
        logging.warning("======== Experiment %s finished ========" % setup_key)
||||||| merged common ancestors
            if "SimulatedAnnealing" in experiment["sls"]:
                execute_simulated_annealing(experiment)
            elif "IterativeImprovement" in experiment["sls"]:
                # execute localsearch
                #execute_localsearch(experiment)
                execute_iterative_improvement(experiment)
            logging.warning("======== Repetition %d finished ========" % i)
        logging.warning("======== Experiment %s finished ========" % setup_key)
=======
            # execute local search
            execute_localsearch(setup["configuration"], arguments)
>>>>>>> msth-kubedaar


def submit(experiment_file):
    """
    Reads the experiments_file and submits the experiment to the scheduling system
    """
    experiment_setup = load_experiment_file(experiment_file)
    for setup_key in experiment_setup:  # Execute each experiment
        setup = experiment_setup[setup_key]
        # Execute the repetitions of an experiment
        for i in range(0, setup["repetitions"]):
            # retrieve important information
            initial_controller = setup["initial_controller"]
            if not initial_controller == "minimal":
                initial_controller = "{}:{}".format(initial_controller,
                                                    i+1)  # add the current repetition if it is not minimal
            # TODO: only assign those that are necessary
            arguments = {
                "configuration": setup["configuration"],
                "architecture": setup["architecture"],
                "scenario_file": setup["scenario"],
                "initial_controller": initial_controller,
                # create correct jobname
                "job_name": "{}_{}".format(setup_key, i),
                "result_directory": setup["result_directory"],
<<<<<<< HEAD
                "parallel": setup["parallel"],
                "file": experiment_file
||||||| merged common ancestors
                "parallel": setup["parallel"],
=======
>>>>>>> msth-kubedaar
            }
            submit_localsearch(arguments)


def submit_localsearch(args):
    """
    Create a submission script for the cluster and submit it to the scheduling system
    :param args: A dictionary with the following keys: "config_file_name", "architecture", "path_to_scenario",
                "budget", "initial_controller", "job_name", "result_directory", "parallel"
    """
    # TODO: Make the following blob a little bit more customizable
    # TODO: Also don't write it to a real file, or at least clean the file up after execution
<<<<<<< HEAD
    submit_cmd = """
#!/bin/bash
||||||| merged common ancestors
    submit_cmd = """#!/bin/bash
=======

    config_data = configuration.load_from_file(args["configuration"])
    execution_cmd = "python3" if not config_data["parallelization"]["mode"]=="MPI" else "mpiexec -n 1 python3 -m mpi4py.futures"

    submit_cmd = """#!/bin/bash
>>>>>>> msth-kubedaar
#$ -N {job_name}
#$ -l short
#$ -m ase
#      b     Mail is sent at the beginning of the job.
#      e     Mail is sent at the end of the job.
#      a     Mail is sent when the job is aborted or rescheduled.
#      s     Mail is sent when the job is suspended.
#$ -cwd
<<<<<<< HEAD
#$ -binding linear:256
#$ -pe mpi {parallel}
||||||| merged common ancestors
=======
{parallel}
>>>>>>> msth-kubedaar

USERNAME=`whoami`
TMPDIR=/tmp/${{USERNAME}}/localsearch_results_{job_name}
JOBDIR=/home/${{USERNAME}}/masterthesis/localsearch
SOURCEDIR=${{JOBDIR}}/src
RESULTDIR=${{JOBDIR}}/result

mkdir -p ${{TMPDIR}}
source /home/${{USERNAME}}/venv/bin/activate &> $TMPDIR/output_{job_name}.txt
cd ${{SOURCEDIR}}
export PYTHONPATH=${{PYTHONPATH}}:/home/${{USERNAME}}/masterthesis/localsearch/src/

<<<<<<< HEAD
/opt/openmpi/bin/mpiexec -n 1 python3 -m mpi4py.futures automode_localsearch.py local -e {filename} &>> ${{TMPDIR}}/output_{job_name}.txt
#python3 automode_localsearch.py local -e {filename} &>> ${{TMPDIR}}/output_{job_name}.txt
||||||| merged common ancestors
mpiexec -n 1 python3 -m mpi4py /home/jkuckling/AutoMoDe-LocalSearch/src/automode_localsearch.py run -c {} -a {} -s {} -b {} -i {} -j {job_name} -r ${{TMPDIR}} &>> ${{TMPDIR}}/output_{job_name}.txt
=======
{} /home/${{USERNAME}}/masterthesis/localsearch/src/automode_localsearch.py run -c {} -a {} -s {} -i {} -j {job_name} -r ${{TMPDIR}} &>> ${{TMPDIR}}/output_{job_name}.txt
>>>>>>> msth-kubedaar

RET=$?
mv ${{TMPDIR}}/* ${{RESULTDIR}}
cd ${{JOBDIR}}
rmdir -p ${{TMPDIR}} &> /dev/null
<<<<<<< HEAD
""".format(job_name=args["job_name"] + str(np.random.randint(1, 1000)),
           parallel=args["parallel"] + 1,
           filename=args["file"])
||||||| merged common ancestors
""".format(args["config_file_name"], args["architecture"], args["path_to_scenario"], args["budget"],
           args["initial_controller"], job_name=args["job_name"])
=======
""".format(execution_cmd, args["configuration"], args["architecture"], args["scenario_file"],
           args["initial_controller"], job_name=args["job_name"],
           parallel="""#$ -pe mpi {}
#$ -binding linear:256""".format(config_data["parallelization"]["parallel"])
           if config_data["parallelization"]["mode"] == "MPI" else "")
>>>>>>> msth-kubedaar
    with open("submit_localsearch_{}.sh".format(args["job_name"]), "w") as submit_file:
        submit_file.write(submit_cmd)
    args = ["qsub", "submit_localsearch_{}.sh".format(args["job_name"])]
    qsub_process = subprocess.Popen(
        args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    (stdout, stderr) = qsub_process.communicate()
    print(stdout.decode('utf-8'))
    print(stderr.decode('utf-8'))


def create_run_directory():
    os.chdir(settings.experiment["result_directory"])
    str_time = datetime.now().strftime("%Y%m%d-%H:%M:%S")
    exp_dir = "{}_{}".format(settings.experiment["job_name"], str_time)
    os.mkdir(exp_dir)
    os.chdir(exp_dir)
    # copy the configuration file
    new_config_filename = "config_{}.json".format(settings.experiment["job_name"])
    configuration.write_settings_to_file(new_config_filename)


def execute_localsearch(configuration_file, experiment_arguments = {}):
    """
    Executes a single run of the localsearch
    :param configuration_file: A file with the complete configuration
    :param experiment_arguments: eventual additional arguments (will be saved in settings.experiment}
    """
    # load the configuration
    config_data = configuration.load_from_file(configuration_file)

    # set experiment_arguments if given
    if "experiment" in config_data:
        experiment_dict = config_data["experiment"]
    else:
        experiment_dict = {}
        config_data["experiment"] = experiment_dict
    for key in experiment_arguments:
        experiment_dict[key] = experiment_arguments[key]

    # apply the configuration
    configuration.apply(config_data)

    # create the run folder
    logging.info(config_data["experiment"]["job_name"])
    create_run_directory()

    if "sls" in config_data:
        result = execute_sls(config_data["sls"])
    else:
        # run local search
        initial_controller = localsearch.utilities.get_initial_controller()
        initial_controller.draw("initial")
        result = iterative_improvement(initial_controller)

    # save the best controller
    result.draw("final")
    best_controller = result.convert_to_commandline_args()
    logging.info(best_controller)
    with open("best_controller.txt", mode="w") as file:
        file.write(" ".join(best_controller))
    localsearch.utilities.return_to_src_directory()


def execute_sls(data):
    """
    """
<<<<<<< HEAD
    configuration.load_from_file(args["config_file_name"])
    configuration.load_from_arguments(args)
    configuration.apply()
    logging.info(args["job_name"])
    localsearch.utilities.create_directory()
    sa = SA.from_json(args["sls"]['SimulatedAnnealing'])
    new_controller = sa.local_search()
    logging.warning('Best controller score %s' % str(new_controller.agg_score))
    new_controller.draw("final")
    new_controller = new_controller.convert_to_commandline_args()
    logging.debug(new_controller)
    with open("best_controller_sa.txt", mode="w") as file:
        file.write(" ".join(new_controller))
    localsearch.utilities.return_to_src_directory()


def execute_iterative_improvement(args):
    """
    """
    configuration.load_from_file(args["config_file_name"])
    configuration.load_from_arguments(args)
    configuration.apply()
    logging.info(args["job_name"])
    localsearch.utilities.create_directory()
    ii = II.from_json(args["sls"]['IterativeImprovement'])
    new_controller = ii.local_search()
    logging.warning('Best controller score %s' % str(new_controller.agg_score))
    new_controller.draw("final")
    new_controller = new_controller.convert_to_commandline_args()
    logging.debug(new_controller)
    with open("best_controller_ii.txt", mode="w") as file:
        file.write(" ".join(new_controller))
    localsearch.utilities.return_to_src_directory()
||||||| merged common ancestors
    configuration.load_from_file(args["config_file_name"])
    configuration.load_from_arguments(args)
    configuration.apply()
    logging.info(args["job_name"])
    localsearch.utilities.create_directory()
    sa = SA.from_json(args["sls"]['SimulatedAnnealing'])
    new_controller = sa.local_search()
    logging.warning('Best controller score {}'.format(new_controller.agg_score))
    new_controller.draw("final")
    new_controller = new_controller.convert_to_commandline_args()
    logging.debug(new_controller)
    with open("best_controller_sa.txt", mode="w") as file:
        file.write(" ".join(new_controller))
    localsearch.utilities.return_to_src_directory()

def execute_iterative_improvement(args):
    """
    """
    configuration.load_from_file(args["config_file_name"])
    configuration.load_from_arguments(args)
    configuration.apply()
    logging.info(args["job_name"])
    localsearch.utilities.create_directory()
    ii = II.from_json(args["sls"]['IterativeImprovement'])
    new_controller = ii.local_search()
    logging.warning('Best controller score {}'.format(new_controller.agg_score))
    new_controller.draw("final")
    new_controller = new_controller.convert_to_commandline_args()
    logging.debug(new_controller)
    with open("best_controller_ii.txt", mode="w") as file:
        file.write(" ".join(new_controller))
    localsearch.utilities.return_to_src_directory()
=======
    for key in data:
        algorithm = localsearch.utilities.get_class("localsearch.%s" % key)
        instance = algorithm.from_json(data[key])
        logging.debug(instance.__dict__)
        controller = instance.local_search()
        logging.info('Best controller score %s' % str(controller.agg_score))
    return controller
>>>>>>> msth-kubedaar


def parse_arguments():
    """This method parses the arguments to this script"""

    def create_subparser_local():
        """
        Sets up the parser for the subcommand local.
        This subcommand will execute a whole experiment on the local machine.
        """
        parser_local = subparsers.add_parser('local', help='run an experiment locally')
        parser_local.add_argument("-e", dest="experiment_file",
                                  help="(relative) path to the experiment file")

    def create_subparser_submit():
        """
        Sets up the parser for the subcommand submit.
        This subcommand will submit a whole experiment to the scheduler.
        """
        parser_submit = subparsers.add_parser('submit',
                                              help='submit an experiment to a scheduling system')
        parser_submit.add_argument("-e", dest="experiment_file",
                                   help="(relative) path to the experiment file")

    def create_subparser_run():
        """
        Sets up the parser for the subcommand run.
        This subcommand will execute a single local search.
        """
        parser_run = subparsers.add_parser('run', help='run a single execution of the local search')
        parser_run.add_argument("-c", dest="configuration_file",
                                help="(relative) path to the configuration file (REQUIRED)")
        # additionally to the config file, the run command can also take any data
        # that would be written to settings.experiment otherwise
        # this includes:
        #   "job_name"
        #   "scenario"
        #   "architecture"
        #   "initial_controller"
        #   "result_directory"
        parser_run.add_argument('-j', '--job_name', dest="job_name", default="", required=False,
                                help="The job name, used for the results folder. (OPTIONAL)")
        # "If this is not set, one will be created from the scenario, budget and initial "
        # "controller information.")
        parser_run.add_argument('-s', '--scenario_file', dest="scenario_file", default="", required=False,
                                help="The scenario file for the improvement. "
                                     "(OPTIONAL)")
        parser_run.add_argument('-a', '--architecture', dest="architecture", default="", required=False,
                                help="The type of controller used (FSM or BT). "
                                     "(OPTIONAL)")
        parser_run.add_argument('-i', '--initial_controller', dest="initial_controller", default="", required=False,
                                help="The initial controller for the local search. "
                                     "(OPTIONAL)")
        parser_run.add_argument('-r', '--result_directory', dest="result_dir", default="", required=False,
                                help="The directory where the results of the local search algorithm are written. "
                                     "(OPTIONAL)")

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(
        title="execution", dest="execution_subcommand")
    create_subparser_local()
    create_subparser_submit()
    create_subparser_run()
    input_args = parser.parse_args()
    return input_args


def main():
    input_args = parse_arguments()
    if input_args.execution_subcommand == "local":
        run_local(input_args.experiment_file)
    elif input_args.execution_subcommand == "submit":
        submit(input_args.experiment_file)
    elif input_args.execution_subcommand == "run":
        args = {}
        if input_args.job_name:
            args["job_name"] = input_args.job_name
        if input_args.scenario_file:
            args["scenario_file"] = input_args.scenario_file
        if input_args.architecture:
            args["architecture"] = input_args.architecture
        if input_args.initial_controller:
            args["initial_controller"] = input_args.initial_controller
        if input_args.result_dir:
            args["result_directory"] = input_args.result_dir
        execute_localsearch(input_args.configuration_file, args)
    else:
        logging.error(" Could not recognize subcommand {}."
                      "Please check the help for more information"
                      .format(input_args.execution_subcommand))


if __name__ == "__main__":
    main()
