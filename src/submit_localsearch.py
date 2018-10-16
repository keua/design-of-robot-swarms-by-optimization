#!/usr/bin/env python3

import argparse
from config.configuration import Configuration


# Set up these variables for your use
user_mail = "jonas.kuckling@ulb.ac.be"


def prepare_submission_script(identifier, config_file):

    def prepare_mpi():
        return """# Lines for MPI
#$ -pe mpi {num_parallel_jobs}
#$ -binding linear:256"""

    def prepare_cmd():
        # TODO: Check for MPI
        return """python3 main.py
#mpiexec -n 1 python3 -m mpi4py /home/jkuckling/AutoMoDe-LocalSearch/src/main.py"""

    def prepare_args():
        return ("-c {config_file} -r TMPDIR -s {scenario_file} -i {initial_controller} -exe {executable}"
                "-j {identifier} -t {controller_type}")

    def prepare_output_file():
        return "$TMPDIR/output-{job_name}.txt"

    dummy_data = {  # used for the first replacement, adding mpi, cmd and args
        "MPI_setup": prepare_mpi(),
        "prepared_cmd": prepare_cmd(),
        "prepared_args": prepare_args(),
        "prepared_out": prepare_output_file(),
        "identifier": "{identifier}",
        "job_name": "{job_name}",
        "queue_type": "{queue_type}",
        "mail": "{mail}",
        "num_parallel_jobs": "{num_parallel_jobs}",
        "config_file": "{config_file}",
        "scenario_file": "{scenario_file}",
        "initial_controller": "{initial_controller}",
        "executable": "{executable}",
        "controller_type": "{controller_type}",
    }

    data = {
        "identifier": identifier,
        "job_name": "AutoMoDe-LocalSearch-{}".format(identifier),
        "queue_type": "long",
        "mail": user_mail,
        "num_parallel_jobs": 0,  # TODO: Get value
        "config_file": config_file,
        "scenario_file": config_file,  # TODO: Get value
        "initial_controller": "empty",  # TODO: Get value
        "executable": "automode_main",  # TODO: Get value
        "controller_type": "FSM",  # TODO: Get value
    }
    raw_script = """#!/bin/bash
#$ -N {job_name}
#$ -l {queue_type}
#$ -m eas
#$ -M {mail}
#$ -cwd
{MPI_setup}

USERNAME=`whoami`
TMPDIR=/tmp/$USERNAME/LocalSearch_results_${identifier}
JOBDIR=/home/$USERNAME/AutoMoDe-LocalSearch
SOURCEDIR=$JOBDIR/src
RESULTDIR=$JOBDIR/result
CMD={prepared_cmd}


mkdir -p $TMPDIR
source venv/bin/activate &> $TMPDIR/output_${job_name}.txt
cd $SOURCEDIR
export PYTHONPATH=$PYTHONPATH:/home/jkuckling/AutoMoDe-LocalSearch/src/
$CMD {prepared_args} &>> {prepared_out}
RET=$?
mv $TMPDIR/* $RESULTDIR
cd $JOBDIR
rmdir -p $TMPDIR &> /dev/null

exit $RET
"""

    # setup execution decisions
    raw_script = raw_script.format(**dummy_data)
    # fill the data
    script = raw_script.format(**data)
    print(script)
    return script


def submit_task():
    pass


def localsearch_irace():
    pass


def localsearch_random():
    pass


def localsearch_minimal():
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the local search algorithm")
    parser.add_argument('-c', '--config', dest="config_file", default="config.ini",
                        help="The configuration file for the local search algorithm")
    input_args = parser.parse_args()
    # Configuration.instance.config_file_name = input_args.config_file
    prepare_submission_script(1, input_args.config_file)
