#!/bin/bash
var1=$1
var2=$2
suffix=$3

#for loop 1-50
for ens in {1..50}
do
    echo "Ensemble member ${ens}"
    # run the python script
    sbatch flux_variability.sh ${ens} ${var1} ${var2} ${suffix}
    # ./1upvp.sh ${ens}
done