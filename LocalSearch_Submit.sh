#!/bin/bash
#$ -N FSM_LocalSearch
#$ -m eas
#$ -M jonas.kuckling@ulb.ac.be
#$ -cwd

USERNAME=`whoami`
TMPDIR=/tmp/$USERNAME/LocalSearch_results
JOBDIR=/home/$USERNAME/AutoMoDe-LocalSearch

mkdir -p $TMPDIR
mv $JOBDIR $TMPDIR
cd $TMPDIR
source venv/bin/activate &> $TMPDIR/output.txt
cd src/
python3 main.py -c config-FSM.ini &>> $TMPDIR/output.txt
RET=$?
mv $TMPDIR $JOBDIR
cd $JOBDIR
rmdir -p $TMPDIR &> /dev/null

exit $RET
