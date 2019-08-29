#!/usr/bin/env python3
__author__ = "Jonas Kuckling, jonas.kuckling@ulb.ac.be, Keneth Ubeda, k3n3th@gmail.com"
"""
Use this script to start the local search. Run start_localsearch.py -h for more help.
"""
import os
import argparse
import logging
import json
import subprocess
from datetime import datetime

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
            # execute local search
            execute_localsearch(setup["configuration"], arguments)


def submit(experiment_file, cluster="majorana"):
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
                "job_name": "{}_{}".format(setup_key, i) if cluster == "majorana" else setup_key,
                "result_directory": setup["result_directory"],
                "repetitions" : setup["repetitions"]
            }
            if cluster == "majorana" :
                submit_localsearch(arguments)
            elif cluster == "hydra":
                submit_localsearch_hydra(arguments)
                break


def submit_localsearch(args):
    """
    Create a submission script for the cluster and submit it to the scheduling system
    :param args: A dictionary with the following keys: "config_file_name", "architecture", "path_to_scenario",
                "budget", "initial_controller", "job_name", "result_directory", "parallel"
    """
    # TODO: Make the following blob a little bit more customizable
    # TODO: Also don't write it to a real file, or at least clean the file up after execution

    config_data = configuration.load_from_file(args["configuration"])
    configuration.update_dirs(config_data)
    configuration.update_path_experiment(args, config_data)
    execution_cmd = "python3" if not config_data["parallelization"]["mode"]=="MPI" else "mpiexec -n 1 python3 -m mpi4py.futures"

    submit_cmd = """#!/bin/bash
#$ -N {job_name}
#$ -l long
#$ -m ase
#      b     Mail is sent at the beginning of the job.
#      e     Mail is sent at the end of the job.
#      a     Mail is sent when the job is aborted or rescheduled.
#      s     Mail is sent when the job is suspended.
#$ -cwd
{parallel}

USERNAME=`whoami`
TMPDIR=/tmp/${{USERNAME}}/localsearch_results_{job_name}
JOBDIR=/home/${{USERNAME}}/masterthesis/localsearch
SOURCEDIR=${{JOBDIR}}/src
RESULTDIR={result_dir}

mkdir -p ${{TMPDIR}}
source /home/${{USERNAME}}/venv/bin/activate &> $TMPDIR/output_{job_name}.txt
cd ${{SOURCEDIR}}
export PYTHONPATH=${{PYTHONPATH}}:/home/${{USERNAME}}/masterthesis/localsearch/src/

{} /home/${{USERNAME}}/masterthesis/localsearch/src/automode_localsearch.py run -c {} -a {} -s {} -i {} -j {job_name} -r ${{TMPDIR}} &>> ${{TMPDIR}}/output_{job_name}.txt

RET=$?
mv ${{TMPDIR}}/* ${{RESULTDIR}}
cd ${{JOBDIR}}
rmdir -p ${{TMPDIR}} &> /dev/null
""".format(execution_cmd, args["configuration"], args["architecture"], args["scenario_file"],
           args["initial_controller"], job_name=args["job_name"],
           parallel="""#$ -pe mpi {}
#$ -binding linear:256""".format(config_data["parallelization"]["parallel"])
           if config_data["parallelization"]["mode"] == "MPI" else "",
           result_dir=args["result_directory"])
    filename = "submit_localsearch_{}.sh".format(args["job_name"])
    with open(filename, "w") as submit_file:
        submit_file.write(submit_cmd)
    args = ["qsub", "-o", "/tmp/{}.{}".format(args["job_name"],".o"),
            "-e" , "/tmp/{}.{}".format(args["job_name"],".e"),
            filename]
    qsub_process = subprocess.Popen(
        args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    (stdout, stderr) = qsub_process.communicate()
    print(stdout.decode('utf-8'))
    print(stderr.decode('utf-8'))
    os.remove(filename)

def submit_localsearch_hydra(args):
    """
    Create a submission script for the cluster and submit it to the scheduling 
    system
    :param args: A dictionary with the following keys: "config_file_name",
                 "architecture", "path_to_scenario", "budget",
                  "initial_controller", "job_name", "result_directory",
                  "parallel"
    """
    config_data = configuration.load_from_file(args["configuration"])
    configuration.update_dirs(config_data)
    configuration.update_path_experiment(args, config_data)
    walltime = "00:45:00"
    steps = config_data["execution"]["budget"] / \
        (config_data["execution"]["seed_window_size"] +
        config_data["execution"]["seed_window_movement"])
    if steps >= 1250 and steps  < 2100:
        walltime = "02:00:00"
    elif steps  >= 2100 and steps  < 4200:
        walltime = "04:00:00"
    elif steps >= 4200 and steps < 8400:
        walltime = "10:00:00"
    elif steps >= 8400 :
        walltime = "16:00:00"
    execution_cmd = "mpiexec -n 1 python3 -m mpi4py.futures"

    submit_cmd = \
"""#!/bin/bash
#PBS -t 0-{repetitions}
#PBS -N {job_name}

  # send mail notification (optional)
  #   a        when job is aborted
  #   b        when job begins
  #   e        when job ends
  #   M        your e-mail address (should always be specified)
#PBS -m e
#PBS -M kubedaar@ulb.ac.be

  # requested running time (required!)
#PBS -l walltime={walltime}
  # specification (required!)
  #   nodes=   number of nodes; 1 for serial; 1 or more for parallel
  #   ppn=     number of processors per node; 1 for serial;
  #   mem=     memory required
  #   ib       request infiniband
#PBS -l nodes=1:intel:ppn={parallel}


  # redirect standard output (-o) and error (-e) (optional)
  # if omitted, the name of the job (specified by -N) or
  # a generic name (name of the script followed by .o or .e and 
  # job number) will be used
#PBS -o {result_dir}/stdout_{job_name}_$PBS_ARRAYID.$PBS_JOBID
#PBS -e {result_dir}/stderr_{job_name}_$PBS_ARRAYID.$PBS_JOBID


  # go to the (current) working directory (optional, if this is the
  # directory where you submitted the job)
cd $PBS_O_WORKDIR

export PYTHONPATH=${{PYTHONPATH}}:${{VSC_HOME}}/localsearch/src/

  # load the environment
module purge
module load Python/3.6.6-intel-2018b
module load mpi4py/3.0.1-intel-2018b-Python-3.6.6

echo submit directory: $PWD
echo jobid: $PBS_JOBID
echo hostname: $HOSTNAME
date
echo ---Start Job ---
{} ${{VSC_HOME}}/localsearch/src/automode_localsearch.py run -c {} -a {} -s {} -i {} -j {job_name}_${{PBS_ARRAYID}} -r {result_dir}
echo ----End Job ----
date

""".format( execution_cmd, args["configuration"], args["architecture"],
            args["scenario_file"], args["initial_controller"],
            job_name=args["job_name"],
            parallel=config_data["parallelization"]["parallel"],
            result_dir=args["result_directory"],
            walltime=walltime,
            repetitions=args["repetitions"] )
    filename = "submit_localsearch_{}.pbs".format(args["job_name"])
    with open(filename, "w") as submit_file:
        submit_file.write(submit_cmd)
    args = ["qsub", filename]
    qsub_process = subprocess.Popen(
       args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    (stdout, stderr) = qsub_process.communicate()
    print(stdout.decode('utf-8'))
    print(stderr.decode('utf-8'))
    os.remove(filename)

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
    configuration.update_dirs(config_data)
    configuration.update_path_automode(config_data)

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
    localsearch.utilities.return_to_src_directory(settings.cwd["dir"])


def execute_sls(data):
    """
    """
    seed_idx = int(settings.experiment["job_name"].split("_")[-1])
    snap_freq = settings.logging["snapshot_frequency"]
    seed = settings.random["seed_pool"][seed_idx]
    budget = settings.execution["budget"]
    for key in data:
        data[key]["budget"] = budget
        data[key]["random_seed"] = seed
        algorithm = localsearch.utilities.get_class("localsearch.%s" % key)
        instance = algorithm.from_json(data[key])
        logging.debug(instance.__dict__)
        controller = instance.local_search(snap_freq)
        logging.info('Best controller score %s' % str(controller.agg_score))
    return controller


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

    def create_subparser_submit_hydra():
        """
        Sets up the parser for the subcommand submit.
        This subcommand will submit a whole experiment to the scheduler.
        """
        parser_submit = subparsers.add_parser('submit-hydra',
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
    create_subparser_submit_hydra()
    create_subparser_run()
    input_args = parser.parse_args()
    return input_args


def main():
    input_args = parse_arguments()
    if input_args.execution_subcommand == "local":
        run_local(input_args.experiment_file)
    elif input_args.execution_subcommand == "submit":
        submit(input_args.experiment_file)
    elif input_args.execution_subcommand == "submit-hydra":
        submit(input_args.experiment_file, "hydra")
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
