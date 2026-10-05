#!/bin/bash
#SBATCH --job-name=ensmean
#SBATCH --time=01:00:00
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem=200G
#SBATCH --mail-type=FAIL
#SBATCH --account=mh0033
#SBATCH --output=ensmean.%j.out

module load cdo/2.5.0-gcc-11.2.0
module load parallel    

decade=$1
var=$2

export var

ensmean(){
    decade=$1 # 1850, node

    echo "Decade ${decade} for variable ${var}"


    base_path=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/${var}_daily/
    to_path=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/${var}_monthly_ensmean/
    mkdir -p $to_path

    file_name=*_day_MPI-ESM1-2-LR_r*_gn_${decade}*.nc
    out_name=${var}_monmean_ensmean_${decade}05_$((${decade}+9))09.nc


    # Save the find command output to first_ens_list
    first_ens_list=($(find $base_path -name $file_name -print))


    cdo -O -P 5 -ensmean -apply,ymonmean [ ${first_ens_list[@]} ] $to_path${out_name}

}

export -f ensmean

parallel --jobs 25 ensmean ::: {1850..2090..10}

