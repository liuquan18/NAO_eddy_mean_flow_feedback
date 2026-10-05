#!/bin/bash

var=$1
for dec in {1850..2090..10}
do
    echo "Decade ${dec}"
    # run the python script
    sbatch monmean_ensmean.sh ${dec} ${var}
done