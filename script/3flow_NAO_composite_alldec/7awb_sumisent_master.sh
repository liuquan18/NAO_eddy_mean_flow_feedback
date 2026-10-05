#!/bin/bash
var='wb_anticyclonic_allisen'
var_name='smooth_pv'
model_dir='MPI_GE_CMIP6'
plev=None # 


for decade in {1850..2090..10}
do
    echo "submit: $decade"
    sbatch 7awb_NAO_range_distribution_submit.sh $decade $var $var_name $model_dir $plev
done