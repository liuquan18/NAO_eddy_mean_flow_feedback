#!/bin/bash

# Define the variable
var=$1

# Define the path to the files
path=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6/${var}_daily_std

# Loop through the files and rename them
for member in $(seq 1 50); do
    member_id="r${member}i1p1f1"
    files=$(find $path/$member_id -type f -name "${var}_day_MPI-ESM1-2-LR_${member_id}_gn_*.nc")
    
    for file in $files; do
        new_file=$(echo $file | sed "s/_ano.nc/.nc/")
        mv "$file" "$new_file"
        echo "Renamed $file to $new_file"
    done
        echo "Renamed $file to $new_file"
done
