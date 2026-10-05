#!/bin/bash

for var in u geopoth t v q
do
    simulation=vco2_4xco2_land

    echo "Processing variable: ${var}, simulation: ${simulation}"
    # run the python script
    sbatch vco2_land_slab_ocean_split_merge_decade_allplev.sh ${var} ${simulation}
done