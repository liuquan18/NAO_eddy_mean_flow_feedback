#!/bin/bash
#SBATCH --job-name=Ex
#SBATCH --time=01:30:00
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks=5
#SBATCH --mem=200G
#SBATCH --mail-type=FAIL
#SBATCH --account=mh0033
#SBATCH --output=Ex.%j.out

module load cdo/2.5.0-gcc-11.2.0
module load parallel

member=$1
eddy=$2 # transient or steady


if [ "$eddy" = "transient" ]; then
    up_path=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/ua_prime_daily/r${member}i1p1f1/
    vp_path=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/va_prime_daily/r${member}i1p1f1/
    output_dir=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/M2_prime_daily/r${member}i1p1f1/
elif [ "$eddy" = "steady" ]; then
    up_path=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/ua_steady_daily/r${member}i1p1f1/
    vp_path=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/va_steady_daily/r${member}i1p1f1/
    output_dir=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/M2_steady_daily/r${member}i1p1f1/
else
    echo "Unknown eddy type: $eddy"
    exit 1
fi

mkdir -p ${output_dir}
export up_path
export vp_path
export output_dir
export member

echo "Ensemble member ${member}"


Ex_cal(){
    dec=$1
    up_file=$(find ${up_path} -name "*${dec}*.nc" | head -n 1)
    vp_file=$(find ${vp_path} -name "*${dec}*.nc" | head -n 1)
    
    if [ -z "$up_file" ] || [ -z "$vp_file" ]; then
        echo "Files not found for date: $dec"
        return
    fi
    
    output_file=${output_dir}M2_${dec}.nc
    echo "Calculating M2 for date: $dec"
    
    cdo -r -O -expr,"M2=va*va-ua*ua" -merge ${up_file} ${vp_file} ${output_file}
}

export -f Ex_cal

parallel -j 5 Ex_cal ::: {1850..2090..10}