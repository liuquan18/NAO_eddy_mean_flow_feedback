#!/bin/bash

# Loop over variables
# for var in u geopoth t
for var in v q
do
    # Loop over simulations
    for simulation in vco2_4xco2_land vco2_4xco2_ocean vco2_4xco2_all
    do
        echo "Processing variable: ${var}, simulation: ${simulation}"
        # run the python script
        sbatch vco2_landocean_split_merge_decade_allplev.sh ${var} ${simulation}
    done
done