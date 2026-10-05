#!/bin/bash
#SBATCH --job-name=variability
#SBATCH --time=01:30:00
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks=5
#SBATCH --mem=200G
#SBATCH --mail-type=FAIL
#SBATCH --account=mh0033
#SBATCH --output=variability.%j.out

module load cdo/2.5.0-gcc-11.2.0
module load parallel

member=$1
var1=$2
var2=$3
suffix=$4

var1_path=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/${var1}_daily_ano/r${member}i1p1f1/

var2_path=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/${var2}_daily_ano/r${member}i1p1f1/

# var1_path=/scratch/m/m300883/${var1}_daily${suffix}/r${member}i1p1f1/
# var2_path=/scratch/m/m300883/${var2}_daily${suffix}/r${member}i1p1f1/

echo "Ensemble member ${member}"

# create output directory
if [ "$var1" == "$var2" ]; then
    output_dir=/scratch/m/m300883/${var1}_std_daily/r${member}i1p1f1/
else
    output_dir=/scratch/m/m300883/${var1}_${var2}_cov_daily/r${member}i1p1f1/
fi
mkdir -p ${output_dir}

export var1
export var2
export var1_path
export var2_path
export output_dir
export member

std(){
    dec=$1
    var1_file=$(find ${var1_path} -name "*${dec}*.nc" | head -n 1)
    var2_file=$(find ${var2_path} -name "*${dec}*.nc" | head -n 1)
    if [ -z "$var1_file" ] || [ -z "$var2_file" ]; then
        echo "Files not found for date: $dec"
        return
    fi
    #output_file
    if [ "$var1" == "$var2" ]; then
        output_file=${output_dir}${var1}_std_${dec}.nc
        echo "Calculating standard deviation for ${var1} for date: $dec"
        var1_name=$(cdo -s showname ${var1_file} | tr -d ' ')
        cdo -r -O -expr,"std=${var1_name}*${var1_name}" ${var1_file} ${output_file}
    else
        output_file=${output_dir}${var1}_${var2}_cov_${dec}.nc
        echo "Calculating covariance for ${var1} and ${var2} for date: $dec"
        var1_name=$(cdo -s showname ${var1_file} | tr -d ' ')
        var2_name=$(cdo -s showname ${var2_file} | tr -d ' ')
        cdo -r -O -expr,"cov=${var1}*${var2}" -merge ${var1_file} ${var2_file} ${output_file}
    fi

}

export -f std

parallel -j 5 std ::: {1850..2090..10}