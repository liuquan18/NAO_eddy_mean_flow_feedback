#!/bin/bash
#SBATCH --job-name=low
#SBATCH --time=01:00:00
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks=10
#SBATCH --mem=0
#SBATCH --mail-type=FAIL
#SBATCH --account=mh0033
#SBATCH --output=low.%j.out

module load cdo
module load parallel

from_dir=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6/hus_trop_daily/
to_dir=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/hus_daily/

# create all member folders in to_dir
for member in {1..50}; do
    mkdir -p ${to_dir}r${member}i1p1f1/
done


ta_files=$(find $from_dir -name "*.nc" -print)


low_level(){
    infile=$1
    outfile=${infile/hus_trop/hus}
    outfile=${outfile/MPI_GE_CMIP6/MPI_GE_CMIP6_allplev}

    cdo -O -sellevel,100000,85000 $infile $outfile
}


export -f low_level

parallel --jobs 10 low_level ::: ${ta_files[@]}


# check completeness
for member in {1..50}; do
    ta_files=$(find $from_dir -name "ta_day_MPI-ESM1-2-LR_r${member}i1p1f1_gn_*.nc" -print)
    tas_files=$(find $to_dir -name "tas_day_MPI-ESM1-2-LR_r${member}i1p1f1_gn_*.nc" -print)

    if [ ${#ta_files[@]} -ne ${#tas_files[@]} ]; then
        echo "r${member}i1p1f1 is incomplete, reproduce tas files"
        parallel --jobs 10 low_level ::: ${ta_files[@]}
    fi
done