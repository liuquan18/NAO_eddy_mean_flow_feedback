#!/bin/bash
#SBATCH --job-name=mul
#SBATCH --time=01:30:00
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks=5
#SBATCH --mem=200G
#SBATCH --mail-type=FAIL
#SBATCH --account=mh0033
#SBATCH --output=mul.%j.out

module load cdo/2.5.0-gcc-11.2.0
module load parallel

member=$1
var1=$2
var2=$3

if [ "$var1" == "vp" ]; then
    # transient eddies
    var1_path=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6/va_prime_daily/r${member}i1p1f1/
elif [ "$var1" == "up" ]; then
    var1_path=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6/ua_prime_daily/r${member}i1p1f1/
elif [ "$var1" == "tp" ]; then
    var1_path=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6/theta_prime_daily/r${member}i1p1f1/     # potential temperature
elif [ "$var1" == "etp" ]; then
    var1_path=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6/equiv_theta_prime_daily/r${member}i1p1f1/  # equivalent potential temperature
elif [ "$var1" == "qp" ]; then
    var1_path=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6/hus_prime_daily/r${member}i1p1f1/

    # steady eddies
elif [ "$var1" == "vs" ]; then
    var1_path=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6/va_steady_daily/r${member}i1p1f1/
elif [ "$var1" == "us" ]; then
    var1_path=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6/ua_steady_daily/r${member}i1p1f1/
elif [ "$var1" == "ts" ]; then
    var1_path=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6/theta_steady_daily/r${member}i1p1f1/
elif [ "$var1" == "ets" ]; then
    var1_path=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6/equiv_theta_steady_daily/r${member}i1p1f1/
elif [ "$var1" == "qs" ]; then
    var1_path=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6/hus_steady_daily/r${member}i1p1f1/
fi

if [ "$var2" == "vp" ]; then
    # transient eddies
    var2_path=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6/va_prime_daily/r${member}i1p1f1/
elif [ "$var2" == "up" ]; then
    var2_path=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6/ua_prime_daily/r${member}i1p1f1/
elif [ "$var2" == "tp" ]; then
    var2_path=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6/theta_prime_daily/r${member}i1p1f1/
elif [ "$var2" == "etp" ]; then
    var2_path=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6/equiv_theta_prime_daily/r${member}i1p1f1/  # equivalent potential temperature
elif [ "$var2" == "qp" ]; then
    var2_path=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6/hus_prime_daily/r${member}i1p1f1/
    # steady eddies
elif [ "$var2" == "vs" ]; then
    var2_path=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6/va_steady_daily/r${member}i1p1f1/
elif [ "$var2" == "us" ]; then
    var2_path=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6/ua_steady_daily/r${member}i1p1f1/
elif [ "$var2" == "ts" ]; then
    var2_path=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6/theta_steady_daily/r${member}i1p1f1/
elif [ "$var2" == "ets" ]; then
    var2_path=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6/equiv_theta_steady_daily/r${member}i1p1f1/
elif [ "$var2" == "qs" ]; then
    var2_path=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6/hus_steady_daily/r${member}i1p1f1/
fi
    


echo "Ensemble member ${member}"


flux_path=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6/${var1}${var2}_daily/r${member}i1p1f1/

mkdir -p ${flux_path}

export var1_path var2_path flux_path member var1 var2

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
        cdo -r -O mul ${vfile} ${tfile} ${outfile}
    else
        echo "Calculating eddy flux for ${dec} in ${var1}${var2}"
        cdo -r -O -expr,"${var1}${var2}=${var1_name}*${var2_name}" -merge ${vfile} ${tfile} ${outfile}
    fi

}

export -f flux

parallel --jobs 5 flux ::: {1850..2090..10}

# check if all files are created
for dec in {1850..2090..10}; do

    outfile="${flux_path}${var1}${var2}_${dec}.nc"
    
    if [ ! -f "${outfile}" ]; then
        echo "Error: ${outfile} not created"
        exit 1
    fi
done