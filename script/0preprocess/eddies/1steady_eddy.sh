#!/bin/bash
#SBATCH --job-name=steady
#SBATCH --time=01:30:00
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks=5
#SBATCH --mem=200G
#SBATCH --mail-type=FAIL
#SBATCH --account=mh0033
#SBATCH --output=steady.%j.out

module load cdo/2.5.0-gcc-11.2.0
module load parallel

node=$1
member=$node
var=$2
echo "Ensemble member ${member} of variable ${var}"


T_path=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6/${var}_hat_daily/r${member}i1p1f1/

T_mmean_path=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6/${var}_monthly_ensmean/


Ts_path=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6/${var}_steady_daily/r${member}i1p1f1/


tmp_dir=/scratch/m/m300883/${var}_steady/r${member}i1p1f1/

mkdir -p ${Ts_path} ${tmp_dir}


export T_path Ts_path member tmp_dir var


# function to band filter
sub_zonmean(){
    infile=$1
    mmean_file=$2
    outfile=$3


    # zonal anomaly
    cdo -O ymonsub ${infile} -enlarge,${mmean_file} -zonmean ${mmean_file} ${outfile}
}

steady_eddy(){
    dec=$1
    Tfile=$(find ${T_path} -name "*${dec}*.nc")
    Tfile=$(echo $Tfile | tr -d '\n')

    # monthly mean
    Tmmean_file=$(find ${T_mmean_path} -name "*${dec}*.nc")
    
    Tfile_name=$(basename "${Tfile}")
    Tsfile="${Ts_path}${Tfile_name//${var}/${var}_steady}"

    echo "Input file: ${Tfile}"
    echo "Output file: ${Tsfile}"
    sub_zonmean ${Tfile} ${Tmmean_file} ${Tsfile}
}

export -f sub_zonmean
export -f steady_eddy

parallel -j 5 steady_eddy ::: {1850..2090..10}

# check completion
for dec in {1850..2090..10}; do
    if [ ! -f ${Ts_path}/*${dec}*.nc ]; then
        echo "Decade ${dec} is missing"
        echo "Recalculate decade ${dec}"
        steady_eddy ${dec}
    fi
done