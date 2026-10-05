#!/bin/bash
#SBATCH --job-name=prime
#SBATCH --time=01:30:00
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks=5
#SBATCH --mem=200G
#SBATCH --mail-type=FAIL
#SBATCH --account=mh0033
#SBATCH --output=prime.%j.out

module load cdo/2.5.0-gcc-11.2.0
module load parallel

node=$1
member=$node
var=$2
echo "Ensemble member ${member} of variable ${var}"

frequency=${3:-prime} # prime (2-12 days) or high (2-6 days), default prime

T_path=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6/${var}_daily/r${member}i1p1f1/


if [ "$frequency" == "prime" ]; then
    Tp_path=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6/${var}_prime_daily/r${member}i1p1f1/
elif [ "$frequency" == "prime_high" ]; then
    Tp_path=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6/${var}_prime_high_daily/r${member}i1p1f1/
else
    echo "Frequency not recognized, please use prime or high"
    exit 1
fi

tmp_dir=/scratch/m/m300883/${var}_prime/r${member}i1p1f1/

mkdir -p ${Tp_path} ${tmp_dir}


export T_path Tp_path member tmp_dir var
export frequency

# function to band filter
band_filter(){
    infile=$1
    outfile=$2  
    # basename without .nc
    fname=$(basename ${infile%.nc})

    # split years
    cdo -O -splityear ${infile} ${tmp_dir}${fname}_year
    # band filter
    year_files=$(ls ${tmp_dir}${fname}_year*)
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
        # echo "30 days running mean"
        # cdo -O -mergetime -apply,runmean,30 [ ${year_files} ] ${outfile}
    fi
    # remove temporary files
    rm ${tmp_dir}${fname}_year*
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

parallel -j 5 T_prime ::: {1850..2090..10}

# check completion
for dec in {1850..2090..10}; do
    if [ ! -f ${Tp_path}/*${dec}*.nc ]; then
        echo "Decade ${dec} is missing"
        echo "Recalculate decade ${dec}"
        T_prime ${dec}
    fi
done