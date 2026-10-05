#!/bin/bash
#for loop 1-50
for ens in {1..50}
do
    echo "Ensemble member ${ens} "
    # run the python script
    sbatch 1.3wave_break_allisen_alldec_run.sh ${ens}
done