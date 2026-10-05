#!/bin/bash

var1=$1
var2=$2
plev=$3
suffix=$4
# var1=Fdiv_p_transient
# var2=Fdiv_p_steady


#for loop 1-50
for ens in {1..50}
do
    echo "Ensemble member ${ens}"
    # run the python script
    sbatch transient_steady_sum.sh ${ens} ${var1} ${var2} ${plev} ${suffix}
    # ./1upvp.sh ${ens}
done