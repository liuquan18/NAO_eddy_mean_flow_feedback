#!/bin/bash
var='zg_hat'
var_name='zg'
model_dir='MPI_GE_CMIP6_allplev'
plev=50000 # 


for decade in {1850..2090..10}
do
    echo "submit: $decade"
    sbatch 5blocking_NAO_range_distribution_submit.sh $decade $var $var_name $model_dir $plev
done