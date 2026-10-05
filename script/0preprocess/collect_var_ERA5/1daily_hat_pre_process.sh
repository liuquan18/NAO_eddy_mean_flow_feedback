#!/bin/bash
#SBATCH --job-name=pre_hat
#SBATCH --time=01:00:00
#SBATCH --partition=compute
#SBATCH --nodes=46
#SBATCH --ntasks=46
#SBATCH --cpus-per-task=8
#SBATCH --mem=0
#SBATCH --mail-type=FAIL
#SBATCH --account=mh0033
#SBATCH --output=pre_hat.%j.out


module load cdo/2.5.0-gcc-11.2.0
module load parallel
declare -A var_map=( ["ua"]=131 ["va"]=132 ["hus"]=133 ["ta"]=130 )

var=$1
var_num=${var_map[$var]}

if [ -z "$var_num" ]; then
    echo "Invalid variable. Choose from: ua, va, hus, ta."
    exit 1
fi

levels=${2:-20000,22500,25000,30000,35000,40000,45000,50000,55000,60000,65000,70000,75000,77500,80000,82500,85000,87500,90000,92500,95000,97500,100000}



daily_dir=/pool/data/ERA5/E5/pl/an/1D/${var_num}/
tmp_dir=/scratch/m/m300883/ERA5_allplev/${var}_hat_daily/
to_dir=/work/mh0033/m300883/High_frequecy_flow/data/ERA5_allplev/${var}_hat_daily/

export daily_dir tmp_dir to_dir var levels
mkdir -p $tmp_dir $to_dir

Aprfiles=($(find $daily_dir -name "*.grb" -print | grep "\-04_${var_num}\.grb$"))
Mayfiles=($(find $daily_dir -name "*.grb" -print | grep "\-05_${var_num}\.grb$"))
Junfiles=($(find $daily_dir -name "*.grb" -print | grep "\-06_${var_num}\.grb$"))
Julfiles=($(find $daily_dir -name "*.grb" -print | grep "\-07_${var_num}\.grb$"))
Augfiles=($(find $daily_dir -name "*.grb" -print | grep "\-08_${var_num}\.grb$"))
Sepfiles=($(find $daily_dir -name "*.grb" -print | grep "\-09_${var_num}\.grb$"))
Octfiles=($(find $daily_dir -name "*.grb" -print | grep "\-10_${var_num}\.grb$"))

daily_files=(${Aprfiles[@]} ${Mayfiles[@]} ${Junfiles[@]} ${Julfiles[@]} ${Augfiles[@]} ${Sepfiles[@]} ${Octfiles[@]} )

pre_process(){
    infile=$1
    tmpfile=${tmp_dir}$(basename $infile .grb).nc
    cdo -r -f nc -O -P 8 -setgridtype,regular -sellevel,$levels $infile $tmpfile

}

merge_year(){
    year=$1
    year_files=$(find ${tmp_dir} -name "*.nc" | grep ${year})
    cdo -r -O -P 8 -selmonth,5/9 -runmean,30 -mergetime ${year_files} ${to_dir}E5pl00_1D_${var}_daily_${year}-05-01_${year}-09-31.nc
}

export -f pre_process 
export -f merge_year


# parallel --jobs $SLURM_NTASKS pre_process ::: ${daily_files[@]}

# wait
# parallel --jobs $SLURM_NTASKS merge_year ::: {1979..2024}

for file in "${daily_files[@]}"; do
    echo "selecting file: $file"
    while [ "$(jobs -p | wc -l)" -ge "$SLURM_NTASKS" ]; do
        sleep 2
    done
    srun --ntasks=1 --nodes=1 --cpus-per-task=$SLURM_CPUS_PER_TASK bash -c "pre_process '$file'" &
done

wait  # Wait for all background pre_process jobs to finish

for year in {1979..2024}; do
    echo "Merging year: $year"
    while [ "$(jobs -p | wc -l)" -ge "$SLURM_NTASKS" ]; do
        sleep 2
    done
    srun --ntasks=1 --nodes=1 --cpus-per-task=$SLURM_CPUS_PER_TASK bash -c "merge_year '$year'" &
done




# remove the temporary files
wait
rm -rf $tmp_dir
