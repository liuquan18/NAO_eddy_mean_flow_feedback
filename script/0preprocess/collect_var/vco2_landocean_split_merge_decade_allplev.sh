#!/bin/bash
#SBATCH --job-name=collect_var
#SBATCH --time=01:30:00
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --mem=200G
#SBATCH --mail-type=FAIL
#SBATCH --account=mh0033
#SBATCH --output=coll.%j.out

module load cdo/2.5.0-gcc-11.2.0
module load parallel

# Get parameters from command line
var=$1 #'geopoth'
simulations=$2 #'vco2_4xco2_land', 'vco2_4xco2_ocean'

echo "Processing variable: ${var}"
echo "Simulation: ${simulations}"

# Define function to process each member
process_member() {
    member=$1
    var=$2
    simulations=$3
    
    echo "Processing Ensemble member ${member}"
    
    simulation_path=/work/mh1421/m300849/simulations/${simulations}/ens_${simulations}_${member}/echam6/
    to_path=/scratch/m/m300883/${simulations}/${var}_monmean/ens_${member}/
    
    mkdir -p $to_path
    
    # Define merge function for this member
    start_year=1850
    end_year=$((start_year+9))
    
    echo "Member ${member}: merging files from ${start_year} to ${end_year}"
    
    # Construct a regex pattern to match all years from start_year to end_year
    regex=""
    for year in $(seq $start_year $end_year); do
        if [ -z "$regex" ]; then
            regex="_${year}"
        else
            regex="${regex}|_${year}"
        fi
    done
    regex="${regex}"
    
    # Find files with name ending within start_year and end_year
    files=$(find $simulation_path -type f -name "ens_${simulations}_${member}_echam6_ATM_monmean*.nc" | grep -E "$regex")
    
    if [ -n "$files" ]; then
        outfile="${to_path}ens_${simulations}_${member}_echam6_ATM_monmean_${start_year}0501-${end_year}0930.nc"
        
        cdo -f nc -O -selname,$var -mergetime -apply,-selmonth,5/9 [ $files ] $outfile
        
        echo "Member ${member}: Created $outfile"
    else
        echo "Member ${member}: No files found for the decade ${start_year}-${end_year}"
    fi

}

export -f process_member
export var simulations

# Run for all members (01 to 24) with 4 parallel jobs
seq -f "%02g" 1 24 | parallel --jobs 4 process_member {} $var $simulations

echo "All members processed!"