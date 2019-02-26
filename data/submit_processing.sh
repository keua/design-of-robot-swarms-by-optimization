#!/bin/bash
#$ -N results_processing
#$ -l short
#$ -m ase
#      b     Mail is sent at the beginning of the job.
#      e     Mail is sent at the end of the job.
#      a     Mail is sent when the job is aborted or rescheduled.
#      s     Mail is sent when the job is suspended.
#$ -cwd
#$ -binding linear:256
#$ -pe mpi 300

USERNAME=`whoami`
TMPDIR=/tmp/$USERNAME/localsearch_results_summary
JOBDIR=/home/$USERNAME/masterthesis/localsearch
SOURCEDIR=$JOBDIR/data
RESULTDIR=$JOBDIR/data

mkdir -p $TMPDIR
source /home/$USERNAME/venv/bin/activate &> $TMPDIR/results_processing.txt
cd $SOURCEDIR
export PYTHONPATH=$PYTHONPATH:/home/$USERNAME/masterthesis/localsearch/data/

mpiexec -n 1 python3 -m mpi4py.futures /home/$USERNAME/masterthesis/localsearch/data/process_results.py -r $TMPDIR &>> $TMPDIR/results_processing.txt

RET=$?
mv $TMPDIR/* $RESULTDIR
cd $JOBDIR
rmdir -p $TMPDIR &> /dev/null

# qsub -o /tmp/results_processing.o -e /tmp/results_processing.e process.sh
