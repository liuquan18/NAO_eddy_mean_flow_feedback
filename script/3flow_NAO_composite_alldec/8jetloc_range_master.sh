#!/bin/bash
var='ua'
var_name='ua'
model_dir='MPI_GE_CMIP6_allplev'
plev=25000 # 


for decade in {1850..2090..10}
do
    echo "submit: $decade"
    sbatch 8jetloc_NAO_range_distribution_submit.sh $decade $var $var_name $model_dir $plev
done