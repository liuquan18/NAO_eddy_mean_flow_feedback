#!/bin/bash

var=$1
simulation=$2 #'vco2_4xco2_land', 'vco2_4xco2_ocean'
#for loop 1-50

# run the python script
sbatch vco2_landocean_split_merge_decade_allplev.sh ${var} ${simulation}
