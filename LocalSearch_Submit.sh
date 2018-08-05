#!/bin/bash
#$ -N AutoMoDe_LocalSearch
#$ -m eas
#$ -M jonas.kuckling@ulb.ac.be
#$ -cwd

# THIS FILE IS DEPRECATED!
# RATHER USE RunLocalSearch.sh!
# Only use this file if you are sure that only one process is started.
# Even then, this script will not be updated anymore and might not behave properly.

USERNAME=`whoami`
TMPDIR=/tmp/$USERNAME/LocalSearch_results
JOBDIR=/home/$USERNAME/AutoMoDe-LocalSearch
SOURCEDIR=$JOBDIR/src
RESULTDIR=$JOBDIR/result
CONFIG_FILE=config_BT_for.ini

mkdir -p $TMPDIR
source venv/bin/activate &> $TMPDIR/output.txt
cd $SOURCEDIR
python3 main.py -c $CONFIG_FILE -r $TMPDIR &>> $TMPDIR/output.txt
RET=$?
mv $TMPDIR/* $RESULTDIR
cd $JOBDIR
rmdir -p $TMPDIR &> /dev/null

exit $RET
