#!/bin/bash
var='steady_eddy_heat_d2y2'
var_name='eddy_heat_d2y2'
model_dir='MPI_GE_CMIP6_allplev'
plev=85000 # 


for decade in {1850..2090..10}
do
    echo "submit: $decade"
    sbatch 9steady_d2y2_NAO_range_distribution_submit.sh $decade $var $var_name $model_dir $plev
done