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
module load cdo/2.5.0-gcc-11.2.0
module load parallel

# get the ensemble member from the command line
member=$1
var=$2 #'geopoth'
simulations='vco2_1pctco2_land'
echo "Ensemble member ${member}"


simulation_path=/work/mh1421/m300849/simulations/${simulations}/ens_${simulations}_${member}/echam6/
ensmean_path=/work/mh1421/m300849/simulations/ens_mean/ens_${simulations}/echam6/

# Find files for both scenarios and combine the lists
file_list=$(find $simulation_path -name "*_ATM_monmean_*.nc" -print)


to_path=/scratch/m/m300883/${simulations}/${var}_monmean/ens_${member}/
tmp_path=/scratch/m/m300883/vco2_${var}/ens_${member}/

mkdir -p $to_path 
if [ -d "$tmp_path" ]; then
    rm -rf "$tmp_path"
fi
mkdir -p "$tmp_path"

export to_path tmp_path member simulations ensmean_path simulation_path


# define function anomaly (remove ensemble mean)
anomaly() {
    infile=$1
    # Get the filename
    filename=$(basename $infile)
    echo "anomaly $filename"

    # Set name_ensmean to the same filename but with the first occurrence of _${member} removed
    name_ensmean="${filename/_${member}/}"

    cdo -sub $infile ${ensmean_path}${name_ensmean} $tmp_path$filename

}

export -f anomaly
echo "$file_list" | parallel --jobs 10 anomaly


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
    files=$(find $tmp_path -type f -name "ens_${simulations}_${member}_echam6_ATM_monmean*.nc" | grep -E "$regex")

    if [ -n "$files" ]; then
        outfile="${to_path}ens_${simulations}_${member}_echam6_ATM_monmean_${start_year}0501-${end_year}0930.nc"
        cdo -O -selname,$var -mergetime -apply,-selmonth,5/9 [ $files ] $outfile
        echo "Created $outfile"
    else
        echo "No files found for the decade ${start_year}-${end_year}"
    fi
}

export -f merge

# Loop through decades from 1850 to 2100
for year in $(seq 1850 10 1889); do
    merge $year
done
