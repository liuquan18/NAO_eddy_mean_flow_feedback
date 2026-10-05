#!/bin/bash
#SBATCH --job-name=ano
#SBATCH --time=00:30:00
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks=5
#SBATCH --mem=0
#SBATCH --mail-type=FAIL
#SBATCH --account=mh0033
#SBATCH --output=ano.%j.out

module load cdo/2.5.0-gcc-11.2.0
module load parallel

# get the ensemble member from the command line
member=$1
var=$2
echo "Ensemble member ${member} for variable ${var}"


# vt daily
vt_daily_path=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/${var}_daily/r${member}i1p1f1/
daily_files=($(find $vt_daily_path -name *.nc -print))


savedir=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/${var}_daily_ano/r${member}i1p1f1/
mkdir -p $savedir

export savedir
export var

# define the function
Anomaly() {

    infile=$1
    
    # get the decade label from $infile name
    year=$(cdo -s showyear ${infile} | head -n 1)
    decade_label=$(echo ${year} | cut -c 1-4)
    month_ens=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/${var}_monthly_ensmean/${var}_monmean_ensmean_${decade_label}05_$((${decade_label}+9))09.nc

    cdo -O -ymonsub ${infile} ${month_ens} ${savedir}$(basename ${infile} .nc)_ano.nc
}


export -f Anomaly
parallel --jobs 2 Anomaly ::: ${daily_files[@]}



# # Check if all required decades are saved
# for dec in {1850..2090..10}; do
#     if [ ! -f ${savedir}*${dec}*.nc ]; then
#         echo "File for decade ${dec} is missing in ${savedir}"
    
#         # calculate the missing dec
#         echo "recalculate ${dec}"
#         Anomaly ${vt_daily_path}*${dec}*.nc
#     fi
# done
