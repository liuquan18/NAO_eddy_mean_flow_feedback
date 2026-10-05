#!/bin/bash
infile=$1

outfile=${infile/zg_daily/zg_daily_ano}

# get the basename to echo
echo task $SLURM_PROCID Processing $(basename $infile)

# get the decade label from $infile name
decade_label=$(basename "$infile" | cut -d'_' -f 6 | cut -c1-4)
month_ens=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/${var}_monthly_ensmean/${var}_monmean_ensmean_${decade_label}05_$((${decade_label}+9))09.nc

cdo -O -P 10 -ymonsub ${infile} ${month_ens} ${outfile}

# check if the file is saved
if [ ! -f ${outfile} ]; then
    echo "File ${outfile} not saved"
    exit 1

fi
