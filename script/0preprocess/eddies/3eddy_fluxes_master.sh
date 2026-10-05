#!/bin/bash
var1=$1
var2=$2

#for loop 1-50
for ens in {1..50}
do
    echo "Ensemble member ${ens}"
    # run the python script
    sbatch 3eddy_fluxes.sh ${ens} ${var1} ${var2} 
    # ./1upvp.sh ${ens}
done