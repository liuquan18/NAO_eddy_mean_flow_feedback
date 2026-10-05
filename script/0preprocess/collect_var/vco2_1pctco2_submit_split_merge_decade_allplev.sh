#!/bin/bash

var=$1
#for loop 1-50
for ens in {01..48}
do
    echo "Ensemble member ${ens}"
    # run the python script
    sbatch vco2_1pctco2_split_merge_decade_allplev.sh ${ens} ${var}
done