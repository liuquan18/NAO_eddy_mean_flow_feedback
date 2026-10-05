#!/bin/bash
#SBATCH --job-name=prime
#SBATCH --time=00:30:00
#SBATCH --partition=compute
#SBATCH --nodes=46
#SBATCH --ntasks=46
#SBATCH --cpus-per-task=8
#SBATCH --mem=0
#SBATCH --mail-type=FAIL
#SBATCH --account=mh0033
#SBATCH --output=prime.%j.out

module load cdo/2.5.0-gcc-11.2.0
module load parallel

var=$1
model=${2:-ERA5_allplev}

echo "Processing variable: ${var} for model: ${model}"



T_path=/work/mh0033/m300883/High_frequecy_flow/data/${model}/${var}_daily/


Tp_path=/work/mh0033/m300883/High_frequecy_flow/data/${model}/${var}_prime_daily/


tmp_dir=/scratch/m/m300883/ERA5/${var}_prime/

if [ -d "${tmp_dir}" ]; then
    rm -rf "${tmp_dir}"
fi
mkdir -p "${Tp_path}" "${tmp_dir}"

frequency="prime"  # prime frequency is 2-12 days

export T_path Tp_path tmp_dir var frequency



# function to band filter
band_filter(){
    infile=$1
    outfile=$2  

    echo "Input: ${infile}"
    echo "Output: ${outfile}"

    # band filter
    year_files=$infile
    if [ "$frequency" == "prime" ]; then
        echo "Filtering 2-12 days"
        # cdo -O -mergetime -apply,bandpass,30.5,182.5 [ ${year_files} ] ${outfile}
        cdo -O -mergetime -apply,highpass,36.5 [ ${year_files} ] ${outfile}
        elif [ "$frequency" == "high" ]; then
        echo "Filtering 2-6 days"
        # cdo -O -mergetime -apply,bandpass,60.8,182.5 [ ${year_files} ] ${outfile}
        cdo -O -mergetime -apply,highpass,36.5 [ ${year_files} ] ${outfile}

    elif [ "$frequency" == "hat" ]; then
        echo "Filtering >30 days"  # 1/30 cycle per day, so 1/30*365 = 12.17 per year
        cdo -O -mergetime -apply,lowpass,12 [ ${year_files} ] ${outfile}   
    fi
}


T_prime(){
    dec=$1
    Tfile=$(find ${T_path} -name "*${dec}*.nc")
    Tfile=$(echo $Tfile | tr -d '\n')
    
    Tfile_name=$(basename "${Tfile}")
    Tpfile_name="${Tp_path}${Tfile_name//${var}/${var}_${frequency}}"

    echo "Input file: ${Tfile}"
    echo "Output file: ${Tpfile_name}"
    band_filter ${Tfile} ${Tpfile_name}
}

export -f band_filter
export -f T_prime

for dec in {1979..2024}; do
    echo "Processing decade: ${dec}"
    while [ "$(jobs -p | wc -l)" -ge "$SLURM_NTASKS" ]; do
        sleep 2
    done
    srun --ntasks=1 --nodes=1 --cpus-per-task=$SLURM_CPUS_PER_TASK bash -c "T_prime '$dec'" &
done
wait
rm -rf ${tmp_dir}
