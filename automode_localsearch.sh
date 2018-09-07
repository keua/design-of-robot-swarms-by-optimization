#!/bin/bash
#$ -N AutoMoDe_LocalSearch
#$ -l long
#$ -m eas
#$ -M jonas.kuckling@ulb.ac.be
#$ -cwd

# Submit this script on the cluster to let a single experiment of the local search be conducted.
# This script takes the following (named) parameters
# job_name
# config
# scenario
# initial
# executable

USERNAME=`whoami`
TMPDIR=/tmp/$USERNAME/LocalSearch_results_${job_name}
JOBDIR=/home/$USERNAME/AutoMoDe-LocalSearch
SOURCEDIR=$JOBDIR/src
RESULTDIR=$JOBDIR/result
# CONFIG_FILE=${config}

mkdir -p $TMPDIR
source venv/bin/activate &> $TMPDIR/output_${job_name}.txt
cd $SOURCEDIR
export PYTHONPATH=$PYTHONPATH:/home/jkuckling/AutoMoDe-LocalSearch/src/
#python3 main.py -c ${config} -r $TMPDIR -s ${scenario} -i ${initial} -exe ${executable} -j ${job_name} -t ${controller_type} &>> $TMPDIR/output_${job_name}.txt
mpiexec -n 1 python3 -m mpi4py /home/jkuckling/AutoMoDe-LocalSearch/src/main.py -c ${config} -r $TMPDIR -s ${scenario} -i ${initial} -exe ${executable} -j ${job_name} -t ${controller_type} &>> $TMPDIR/output_${job_name}.txt
RET=$?
mv $TMPDIR/* $RESULTDIR
cd $JOBDIR
rmdir -p $TMPDIR &> /dev/null

exit $RET
