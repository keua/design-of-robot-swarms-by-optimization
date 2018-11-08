#!/usr/bin/env python3

import argparse
import subprocess


# Set up these variables for your use
user_mail = "jonas.kuckling@ulb.ac.be"


def prepare_submission_script(identifier, config_file):

    def prepare_preamble():
        return """#!/bin/bash
#$ -N {job_name}
#$ -l {queue_type}
#$ -m eas
#$ -M {mail}
#$ -cwd"""

    def prepare_mpi_preamble():
        return """# Lines for MPI
#$ -pe mpi {num_parallel_jobs}
#$ -binding linear:256"""

    def prepare_constants():
        return """USERNAME=`whoami`
TMPDIR=/tmp/$USERNAME/LocalSearch_results_{identifier}
JOBDIR=/home/$USERNAME/AutoMoDe-LocalSearch  # TODO: Find our own position
SOURCEDIR=$JOBDIR/src
RESULTDIR=$JOBDIR/result  # TODO: Use value set in config file here
CMD={cmd}"""

    def prepare_workdir_setup():
        return """mkdir -p $TMPDIR"""

    def prepare_python_setup():
        return """source venv/bin/activate &> $TMPDIR/output_${job_name}.txt
cd $SOURCEDIR
export PYTHONPATH=$PYTHONPATH:/home/jkuckling/AutoMoDe-LocalSearch/src/"""

    def prepare_results_retrieval():
        return """mv $TMPDIR/* $RESULTDIR
cd $JOBDIR
rmdir -p $TMPDIR &> /dev/null"""

    def prepare_cmd():
        # TODO: Check for MPI
        return """python3 main.py"""
        # mpiexec -n 1 python3 -m mpi4py /home/jkuckling/AutoMoDe-LocalSearch/src/main.py

    def prepare_args():
        return ("-c {config_file} -r TMPDIR -s {scenario_file} -i {initial_controller} -exe {executable}"
                "-j {identifier} -t {controller_type}")

    def prepare_output_file():
        return "$TMPDIR/output-{job_name}.txt"

    statements = {  # used for creating the file
        "preamble": prepare_preamble(),
        "MPI_preamble": prepare_mpi_preamble(),
        "constants": prepare_constants(),
        "workdir_setup": prepare_workdir_setup(),
        "python_setup": prepare_python_setup(),
        "prepared_args": prepare_args(),
        "prepared_out": prepare_output_file(),
        "results_retrieval": prepare_results_retrieval(),
    }

    data = {  # used for filling the blanks in the statements
        "cmd": prepare_cmd(),
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
    raw_script = """{preamble}
{MPI_preamble}

{constants}

{workdir_setup}
{python_setup}
$CMD {prepared_args} &>> {prepared_out}
RET=$?
{results_retrieval}
exit $RET
"""

    # setup execution decisions
    raw_script = raw_script.format(**statements)
    # fill the data
    script = raw_script.format(**data)
    print(script)
    return script


def submit_task(identifier, config_file):
    script = prepare_submission_script(identifier, config_file)
    p = subprocess.Popen("qsub -v PATH", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, close_fds=True)
    (child_stdout, child_stdin) = (p.stdout, p.stdin)
    child_stdin.write(script)
    child_stdin.close()
    print('Job sent')
    print(child_stdout.read())


def localsearch_irace():
    pass


def localsearch_random():
    pass


def localsearch_minimal():
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the local search algorithm")
    parser.add_argument('-c', '--config', dest="config_file", required=True,
                        help="The configuration file for the local search algorithm")

    # Weird and optional parameters
    parser.add_argument('-c0', '--count0', dest="initial_counter_value", default="0", required=False,
                        help="The initial counter for the starting the local search. Use this if you want to rerun "
                             "single experiments.")

    input_args = parser.parse_args()
    # Configuration.instance.config_file_name = input_args.config_file
    prepare_submission_script(1, input_args.config_file)
