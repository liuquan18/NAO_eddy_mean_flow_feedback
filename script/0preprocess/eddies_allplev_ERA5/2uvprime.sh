#!/bin/bash
#SBATCH --job-name=eddy
#SBATCH --time=01:30:00
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks=5
#SBATCH --mem=200G
#SBATCH --mail-type=FAIL
#SBATCH --account=mh0033
#SBATCH --output=eddy.%j.out

module load parallel

model=ERA5_ano

u_path=/work/mh0033/m300883/High_frequecy_flow/data/${model}/ua_daily/
v_path=/work/mh0033/m300883/High_frequecy_flow/data/${model}/va_daily/

up_path=/work/mh0033/m300883/High_frequecy_flow/data/${model}/up_daily/
vp_path=/work/mh0033/m300883/High_frequecy_flow/data/${model}/vp_daily/

tmp_dir=/scratch/m/m300883/${model}/upvp/
eddy_path=/work/mh0033/m300883/High_frequecy_flow/data/${model}/eke_daily/
upvp_path=/work/mh0033/m300883/High_frequecy_flow/data/${model}/upvp_daily/

mkdir -p ${eddy_path} ${up_path} ${vp_path} ${tmp_dir} ${upvp_path}

export u_path up_path
export v_path vp_path
export eddy_path tmp_dir upvp_path



# function to band filter
band_filter(){
    infile=$1
    outfile=$2  
    # basename without .nc
    fname=$(basename ${infile%.nc})

    cdo -O -highpass,36.55 ${infile} ${outfile}

}

EKE(){
    year=$1
    echo "Calculating EKE for ${year}"
    ufile=$(find ${u_path} -name "*${year}*.nc")
    vfile=$(find ${v_path} -name "*${year}*.nc")

    fname_u=$(basename ${ufile%.nc})
    fname_v=$(basename ${vfile%.nc})

    upfile=${up_path}${fname_u/ua/up}.nc
    vpfile=${vp_path}${fname_v/va/vp}.nc

    eddyfile=${eddy_path}E5pl00_1D_eke_daily_${year}.nc
    upvpfile=${upvp_path}E5pl00_1D_upvp_daily_${year}.nc
    

    echo "Filtering ${fname_u}"
    band_filter ${ufile} ${upfile}

    echo "Filtering ${fname_v}"
    band_filter ${vfile} ${vpfile}

    echo "Calculating EKE"
    cdo -O -expr,'eke=0.5*(var131*var131 + var132*var132)' -merge ${upfile} ${vpfile} ${eddyfile}

    echo "Calculating upvp"
    # cdo -O  -mul ${upfile} ${vpfile} ${upvpfile}
    cdo -r -O -expr,'upvp=var131*var132' -merge ${upfile} ${vpfile} ${upvpfile}
}

export -f EKE
export -f band_filter


start_year=${1:-1979}
end_year=${2:-2024}


# calculate EKE
seq ${start_year} ${end_year} | parallel -j 2 EKE
