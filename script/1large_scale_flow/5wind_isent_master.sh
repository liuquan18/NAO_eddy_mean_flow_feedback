#!/bin/bash

var=$1
#for loop 1-50
for ens in {1..50}
do
    echo "Ensemble member ${ens}"
    # run the python script
    sbatch 5wind_isent_submit.sh ${ens} ${var}
done