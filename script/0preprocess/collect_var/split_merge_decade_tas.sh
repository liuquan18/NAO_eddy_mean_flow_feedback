#!/bin/bash
#SBATCH --job-name=ano
#SBATCH --time=01:00:00
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks=10
#SBATCH --mem=0
#SBATCH --mail-type=FAIL
#SBATCH --account=mh0033
#SBATCH --output=ano.%j.out

# subtract the ensemble mean of the monthly data from the daily data using cdo monsub
# by doing which a long-term trend and seasonal cycle are removed
module load cdo
module load parallel

ta_dir=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6/ta_daily/
tas_dir=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6/tas_daily/

# create all member folders in tas_dir
for member in {1..50}; do
    mkdir -p ${tas_dir}r${member}i1p1f1/
done


ta_files=$(find $ta_dir -name "*.nc" -print)


low_level(){
    infile=$1
    outfile=${infile/ta_/tas_}

    cdo -O -vertmean -sellevel,100000,85000 $infile $outfile
}


export -f low_level

parallel --jobs 10 low_level ::: ${ta_files[@]}


# check completeness
for member in {1..50}; do
    ta_files=$(find $ta_dir -name "ta_day_MPI-ESM1-2-LR_r${member}i1p1f1_gn_*.nc" -print)
    tas_files=$(find $tas_dir -name "tas_day_MPI-ESM1-2-LR_r${member}i1p1f1_gn_*.nc" -print)

    if [ ${#ta_files[@]} -ne ${#tas_files[@]} ]; then
        echo "r${member}i1p1f1 is incomplete, reproduce tas files"
        parallel --jobs 10 low_level ::: ${ta_files[@]}
    fi
done