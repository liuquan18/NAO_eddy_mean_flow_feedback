#!/bin/bash

var=$1
#for loop 1-50
for ens in {1..50}
do
    echo "Ensemble member ${ens}"
    # run the python script
    sbatch split_merge_decade_var_hat_allplev.sh ${ens} ${var}
done