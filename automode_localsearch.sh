#!/bin/bash
#$ -N AutoMoDe_LocalSearch
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
source venv/bin/activate &> $TMPDIR/output_${job_name}_${count}.txt
cd $SOURCEDIR
python3 main.py -c ${config} -r $TMPDIR -s ${scenario} -i ${initial} -exe ${executable} &>> $TMPDIR/output_${job_name}_${count}.txt
RET=$?
mv $TMPDIR/* $RESULTDIR
cd $JOBDIR
rmdir -p $TMPDIR &> /dev/null

exit $RET
