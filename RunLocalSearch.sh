#!/usr/bin/env bash

#USAGE:
#./RunLocalSearch.sh job_name number_of_jobs
#job_name is mandatory and is used to find the configuration file "config_${job_name}.ini"
#number_of_jobs is not mandatory and defaults to 1

#First parameter is the job_name (config_file name without extension)
job_name=${1:?A first parameter (job_name) needs to be specified}
# second parameter is the number of instances that are needed
max=${2:-1}
# third parameter is the directory to the config file (relative from src/)
dir=${3:-'./config'}

for i in `seq 1 $max`
do
    #echo "${job_name}_${i}"
    qsub -v job_name=${job_name},count=${i},dir=${dir} LocalSearch_SubmitWithParameters.sh
    sleep 60
done
