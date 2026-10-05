#!/bin/bash
var='eady_growth_rate'
var_name='eady_growth_rate'
model_dir='MPI_GE_CMIP6_allplev'
plev=85000 # 


for decade in {1850..2090..10}
do
    echo "submit: $decade"
    sbatch 4baroc_NAO_range_distribution_submit.sh $decade $var $var_name $model_dir $plev
done