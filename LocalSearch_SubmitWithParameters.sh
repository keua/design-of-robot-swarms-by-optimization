#!/bin/bash
#$ -N AutoMoDe_LocalSearch
#$ -m eas
#$ -M jonas.kuckling@ulb.ac.be
#$ -cwd

USERNAME=`whoami`
TMPDIR=/tmp/$USERNAME/LocalSearch_results_${job_name}_${count}
JOBDIR=/home/$USERNAME/AutoMoDe-LocalSearch
SOURCEDIR=$JOBDIR/src
RESULTDIR=$JOBDIR/result
CONFIG_FILE=config_${job_name}.ini
# CONFIG_FILE=config_BT_for.ini

mkdir -p $TMPDIR
source venv/bin/activate &> $TMPDIR/output_${job_name}_${count}.txt
cd $SOURCEDIR
python3 main.py -c $CONFIG_FILE -r $TMPDIR &>> $TMPDIR/output_${job_name}_${count}.txt
RET=$?
mv $TMPDIR/* $RESULTDIR
cd $JOBDIR
rmdir -p $TMPDIR &> /dev/null

exit $RET
