#!/bin/bash
decade=$1 # 1850, node
var=$2

echo "Node number: $SLURM_NODEID"
echo "Decade ${decade} for variable ${var}"


base_path=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6/${var}_daily/
to_path=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6/${var}_monthly_ensmean/
mkdir -p $to_path

file_name=*${decade}*.nc
out_name=${var}_monmean_ensmean_${decade}05_$((${decade}+9))09.nc


# Save the find command output to first_ens_list
first_ens_list=($(find -L $base_path -name $file_name -print))


cdo -O -P 5 -ensmean -apply,ymonmean [ ${first_ens_list[@]} ] $to_path${out_name}
# cdo -O -P 5 -ensmean -apply,yearmean [ ${first_ens_list[@]} ] $to_path${out_name}
