#!/bin/bash
eddy=$1
#for loop 1-50
for ens in {1..50}
do
    echo "Ensemble member ${ens}"
    # run the python script
    sbatch 4Ex.sh ${ens} $eddy

done