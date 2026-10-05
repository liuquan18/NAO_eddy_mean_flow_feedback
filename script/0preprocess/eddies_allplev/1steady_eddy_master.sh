#!/bin/bash
var=$1


#for loop 1-50
for ens in {1..50}
do
    echo "Ensemble member ${ens}"
    # run the python script
    sbatch 1steady_eddy.sh ${ens} ${var}
    # ./1upvp.sh ${ens}
done