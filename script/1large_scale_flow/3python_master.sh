#!/bin/bash


file=$1 # python file to run

for ens in {1..50}
do
    echo "Ensemble member ${ens}"
    # run the python script
    sbatch 3python_submit.sh $file ${ens}
done