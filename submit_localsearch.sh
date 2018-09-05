#!/usr/bin/env bash

#CUSTOMIZE
AutoMoDe_FSM=/home/jkuckling/AutoMoDe-FSM/bin/automode_main
AutoMoDe_BT=/home/jkuckling/AutoMoDe-BT/bin/automode_main_bt

#USAGE:
#./RunLocalSearch.sh job_name number_of_jobs
#job_name is mandatory and is used to find the configuration file "config_${job_name}.ini"
#number_of_jobs is not mandatory and defaults to 1

# TODO: Improve checks here

#First parameter is the job_name
job_name=${1:?A first parameter (job_name) needs to be specified}
# fourth parameter is the type of controller (FSM or BT)
controller_type=${2:?The controller type needs to be specified}
# third parameter is the number of instances that are needed
num_instances=${3:-1}
# fourth parameter is the path to the config file (relative from src/)
config=${4:-'./config/config.ini'}
# fifth parameter is the path to the controller file
controller_file=${5:-'empty'}
# sixth parameter is the path to the scenario file
scenario_file={6:-'missing_scenario.argos'}

#get the correct version of AutoMoDe
if [ ${controller_type} = 'FSM' ]
then
    automode=${AutoMoDe_FSM}
elif [ ${controller_type} = 'BT' ]
then
    automode=${AutoMoDe_BT}
fi
echo ${automode}
for i in `seq 1 ${num_instances}`
do
    # if a controller_file was supplied, read the ith controller from it
    if [ ${controller_file} !=  'empty' ]
    then
        controller="$(sed "${i}q;d" ${controller_file})"
    else
        controller=""
    fi
    job_id=${job_name}_${i}
    # submit the job
    qsub -v job_name=${job_id},config=${config},scenario=${scenario_file},initial=${controller},executable=${automode} automode_localsearch.sh
    sleep 60
done
