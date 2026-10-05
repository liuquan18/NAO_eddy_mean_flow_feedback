#!/bin/bash
#SBATCH --job-name=mul
#SBATCH --time=00:30:00
#SBATCH --partition=compute
#SBATCH --nodes=46
#SBATCH --ntasks=46
#SBATCH --cpus-per-task=8
#SBATCH --mem=200G
#SBATCH --mail-type=FAIL
#SBATCH --account=mh0033
#SBATCH --output=mul.%j.out

module load cdo/2.5.0-gcc-11.2.0
module load parallel

var1=$1
var2=$2


if [ "$var1" == "vp" ]; then
    # transient eddies
    var1_path=/work/mh0033/m300883/High_frequecy_flow/data/ERA5_allplev/va_prime_daily/
elif [ "$var1" == "up" ]; then
    var1_path=/work/mh0033/m300883/High_frequecy_flow/data/ERA5_allplev/ua_prime_daily/
elif [ "$var1" == "tp" ]; then
    var1_path=/work/mh0033/m300883/High_frequecy_flow/data/ERA5_allplev/theta_prime_daily/
elif [ "$var1" == "etp" ]; then
    var1_path=/work/mh0033/m300883/High_frequecy_flow/data/ERA5_allplev/equiv_theta_prime_daily/
elif [ "$var1" == "qp" ]; then
    var1_path=/work/mh0033/m300883/High_frequecy_flow/data/ERA5_allplev/hus_prime_daily/

    # steady eddies
elif [ "$var1" == "vs" ]; then
    var1_path=/work/mh0033/m300883/High_frequecy_flow/data/ERA5_allplev/va_steady_daily/
elif [ "$var1" == "us" ]; then
    var1_path=/work/mh0033/m300883/High_frequecy_flow/data/ERA5_allplev/ua_steady_daily/
elif [ "$var1" == "ts" ]; then
    var1_path=/work/mh0033/m300883/High_frequecy_flow/data/ERA5_allplev/theta_steady_daily/
elif [ "$var1" == "ets" ]; then
    var1_path=/work/mh0033/m300883/High_frequecy_flow/data/ERA5_allplev/equiv_theta_steady_daily/
elif [ "$var1" == "qs" ]; then
    var1_path=/work/mh0033/m300883/High_frequecy_flow/data/ERA5_allplev/hus_steady_daily/
fi

if [ "$var2" == "vp" ]; then
    # transient eddies
    var2_path=/work/mh0033/m300883/High_frequecy_flow/data/ERA5_allplev/va_prime_daily/
elif [ "$var2" == "up" ]; then
    var2_path=/work/mh0033/m300883/High_frequecy_flow/data/ERA5_allplev/ua_prime_daily/
elif [ "$var2" == "tp" ]; then
    var2_path=/work/mh0033/m300883/High_frequecy_flow/data/ERA5_allplev/theta_prime_daily/
elif [ "$var2" == "etp" ]; then
    var2_path=/work/mh0033/m300883/High_frequecy_flow/data/ERA5_allplev/equiv_theta_prime_daily/  # equivalent potential temperature
elif [ "$var2" == "qp" ]; then
    var2_path=/work/mh0033/m300883/High_frequecy_flow/data/ERA5_allplev/hus_prime_daily/    
    # steady eddies
elif [ "$var2" == "vs" ]; then
    var2_path=/work/mh0033/m300883/High_frequecy_flow/data/ERA5_allplev/va_steady_daily/
elif [ "$var2" == "us" ]; then
    var2_path=/work/mh0033/m300883/High_frequecy_flow/data/ERA5_allplev/ua_steady_daily/
elif [ "$var2" == "ts" ]; then
    var2_path=/work/mh0033/m300883/High_frequecy_flow/data/ERA5_allplev/theta_steady_daily/
elif [ "$var2" == "ets" ]; then
    var2_path=/work/mh0033/m300883/High_frequecy_flow/data/ERA5_allplev/equiv_theta_steady_daily/
elif [ "$var2" == "qs" ]; then
    var2_path=/work/mh0033/m300883/High_frequecy_flow/data/ERA5_allplev/hus_steady_daily/
fi
    




flux_path=/work/mh0033/m300883/High_frequecy_flow/data/ERA5_allplev/${var1}${var2}_daily/

mkdir -p ${flux_path}

export var1_path var2_path flux_path var1 var2

flux(){
    dec=$1
    vfile=$(find ${var1_path} -name "*${dec}*.nc")
    tfile=$(find ${var2_path} -name "*${dec}*.nc")

    # get var-name for vfile and tfile, remove any spaces
    var1_name=$(cdo -s showname ${vfile} | tr -d ' ')
    var2_name=$(cdo -s showname ${tfile} | tr -d ' ')

    # prepare output file name
    outfile="${flux_path}${var1}${var2}_${dec}.nc"
    if [ "$var1" == "$var2" ]; then
        echo "Calculating square for ${dec} in ${var1}${var2}"
        cdo -P 8 -r -O mul ${vfile} ${tfile} ${outfile}
    else
        echo "Calculating eddy flux for ${dec} in ${var1}${var2}"
        cdo -P 8 -r -O -expr,"${var1}${var2}=${var1_name}*${var2_name}" -merge ${vfile} ${tfile} ${outfile}
    fi

}

export -f flux



for year in {1979..2024}; do
    echo "fluxing year: $year"
    while [ "$(jobs -p | wc -l)" -ge "$SLURM_NTASKS" ]; do
        sleep 2
    done
    srun --ntasks=1 --nodes=1 --cpus-per-task=$SLURM_CPUS_PER_TASK bash -c "flux '$year'" &
done

wait  # Wait for all background pre_process jobs to finish
