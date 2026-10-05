#!/bin/bash

#for loop 1-50
for ens in {1..50}
do
    echo "Ensemble member ${ens}"
    # run the python script
    sbatch 6EP_flux_submit.sh ${ens}
done