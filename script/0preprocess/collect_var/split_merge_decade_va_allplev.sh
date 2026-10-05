#!/bin/bash
#SBATCH --job-name=collect_var
#SBATCH --time=01:30:00
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks=10
#SBATCH --mem=200G
#SBATCH --mail-type=FAIL
#SBATCH --account=mh0033
#SBATCH --output=coll.%j.out

# subtract the ensemble mean of the monthly data from the daily data using cdo monsub
# by doing which a long-term trend and seasonal cycle are removed
module load cdo
module load parallel

# get the ensemble member from the command line
member=$1
var='va'
echo "Ensemble member ${member}"

historical_path=/pool/data/CMIP6/data/CMIP/MPI-M/MPI-ESM1-2-LR/historical/r${member}i1p1f1/day/${var}/gn/v????????/
ssp585_path=/work/ik1017/CMIP6/data/CMIP6/ScenarioMIP/MPI-M/MPI-ESM1-2-LR/ssp585/r${member}i1p1f1/day/${var}/gn/v????????/
# Find files for both scenarios and combine the lists
file_list=$(find $historical_path -name "*.nc" -print; find $ssp585_path -name "*.nc" -print)


to_path=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/${var}_daily/r${member}i1p1f1/
tmp_path=/scratch/m/m300883/$var/r${member}i1p1f1/

mkdir -p $to_path 
if [ -d "$tmp_path" ]; then
    rm -rf "$tmp_path"
fi
mkdir -p "$tmp_path"

export to_path tmp_path

# define function split
split() {
    infile=$1
    # Get the filename
    filename=$(basename $infile)
    echo "Processing $filename"

    name_prefix=${filename:0:-20}

    cdo -splityear $infile $tmp_path$name_prefix

}

export -f split


echo "$file_list" | parallel --jobs 10 split

# define function merge, merge each decade from 1850 to 2100
merge() {
    start_year=$1
    end_year=$((start_year+9))

    echo "merging files from ${start_year} to ${end_year}"

    # Construct a regex pattern to match all years from start_year to end_year
    regex=""
    for year in $(seq $start_year $end_year); do
        if [ -z "$regex" ]; then
            regex="_${year}"
        else
            regex="${regex}|_${year}"
        fi
    done
    regex="${regex}\.nc"

    # Find files with name ending within start_year and end_year
    files=$(find $tmp_path -type f -name "*_r${member}i1p1f1_gn_*.nc" | grep -E "$regex")

    if [ -n "$files" ]; then
        outfile="${to_path}${var}_day_MPI-ESM1-2-LR_r${member}i1p1f1_gn_${start_year}0501-${end_year}0930.nc"
        cdo -O -mergetime -apply,-selmonth,5/9 [ $files ] $outfile
        echo "Created $outfile"
    else
        echo "No files found for the decade ${start_year}-${end_year}"
    fi
}

export -f merge

# Loop through decades from 1850 to 2100
for year in $(seq 1850 10 2090); do
    merge $year
done
