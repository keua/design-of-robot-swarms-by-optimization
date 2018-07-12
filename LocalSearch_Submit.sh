#!/bin/bash
#$ -N AutoMoDe_LocalSearch
#$ -m eas
#$ -M jonas.kuckling@ulb.ac.be
#$ -cwd

USERNAME=`whoami`
TMPDIR=/tmp/$USERNAME/LocalSearch_results
JOBDIR=/home/$USERNAME/AutoMoDe-LocalSearch
SOURCEDIR=$JOBDIR/src
RESULTDIR=$JOBDIR/result

mkdir -p $TMPDIR
source venv/bin/activate &> $TMPDIR/output.txt
cd $SOURCEDIR
python3 main.py -c config_FSM.ini -r $TMPDIR &>> $TMPDIR/output.txt
RET=$?
cd $TMPDIR
mv * $RESULTDIR
cd $JOBDIR
rmdir -p $TMPDIR &> /dev/null

exit $RET
