#!/bin/bash
#SBATCH --job-name=fluxmean
#SBATCH --time=03:30:00
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=200G
#SBATCH --mail-type=FAIL
#SBATCH --account=mh0033
#SBATCH --output=fluxmean.%j.out

module load cdo/2.5.0-gcc-11.2.0
module load parallel


var=$1

dir=/work/mh0033/m300883/High_frequecy_flow/data/ERA5_allplev/${var}_daily/

to_dir=/work/mh0033/m300883/High_frequecy_flow/data/ERA5_allplev/${var}_monthly_mean/

mkdir -p ${to_dir}


daily_files=$(ls ${dir}/*.nc)

cdo -r -f nc -O -P 10 -ymonmean -mergetime ${daily_files} ${to_dir}${var}_monthly_05_09.nc

