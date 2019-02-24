#!/bin/sh

# Arguments
budget=$1

files5k=( "experiments/kubedaar/for_ii_mean_5k.json" )

files20k=( "experiments/kubedaar/for_ii_mean_20k.json" )

files50k=(  )

# Activate virutal environment
source /home/kubedaar/venv/bin/activate
# Go to source folder
cd /home/kubedaar/masterthesis/localsearch/src
# Submit experiment files
case $budget in
    "5k")
            files=( "${files5k[@]}" )
            ;;
    "20k")
            files=( "${files20k[@]}" )
            ;;
    "50k")
            files=( "${files50k[@]}" )
            ;;
esac
for i in "${files[@]}"
do
   : 
   # Submit $i file
    python3 automode_localsearch.py submit -e $i
done
