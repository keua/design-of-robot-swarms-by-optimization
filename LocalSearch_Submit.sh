#!/bin/bash
#$ -N FSM_LocalSearch
#$ -m eas
#$ -M jonas.kuckling@ulb.ac.be
#$ -cwd

USERNAME=`whoami`
TMPDIR=/tmp/$USERNAME/LocalSearch_results
JOBDIR=/home/$USERNAME/LocalSearch_AutoMoDe

mkdir -p $TMPDIR
source $JOBDIR/venv/bin/activate &> $TMPDIR/output.txt
python3 $JOBDIR/src/main.py &>> $TMPDIR/output.txt
RET=$?
mv $TMPDIR $JOBDIR
cd $JOBDIR
rmdir -p $TMPDIR &> /dev/null

exit $RET
