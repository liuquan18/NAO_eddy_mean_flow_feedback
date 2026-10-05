#!/bin/bash

var=$1
#for loop 1-50
for ens in {1..50}
do
    echo "Ensemble member ${ens}"
    # run the python script
    sbatch daily_anomaly_single_ensemble.sh ${ens} ${var}
    # ./daily_anomaly_single_ensemble.sh ${ens} ${var}
done

# module load parallel

# # parallel --jobs $SLURM_NTASKS srun --nodes=1 --ntasks-per-node=1 --cpus-per-task=5 daily_anomaly_single_ensemble.sh ::: {1..50} ::: $var ::: {0..24}
# #!/bin/bash
# #SBATCH --job-name=ano
# #SBATCH --time=00:30:00
# #SBATCH --partition=compute
# #SBATCH --nodes=10
# #SBATCH --ntasks=1250
# #SBATCH --mem=0
# #SBATCH --mail-type=FAIL
# #SBATCH --account=mh0033
# #SBATCH --output=ano.%j.out

# module load cdo
# module load parallel

# # get the ensemble member from the command line
# var=$1
# echo " variable ${var}"


# base_dir=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6/${var}_daily/


# savedir=/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6/${var}_daily_ano/

# for ens in {1..50}; do
#     mkdir -p ${savedir}r${ens}i1p1f1/
# done


# find ${base_dir} -name "${var}_day_MPI-ESM1-2-LR_r*i1p1f1_gn_*.nc" | parallel -j $(($SLURM_NTASKS / 10)) srun --nodes=1 --ntasks=1 --cpus-per-task=10 anomaly.sh

# echo "##############################"
# echo "Check if all files are saved"

# for member in {1..50}; do
#     echo "Checking ensemble member ${member}"
#     # Check if all required decades are saved
#     for dec in {1850..2090..10}; do
#         if [ ! -f ${savedir}${var}_day_MPI-ESM1-2-LR_r${member}i1p1f1_gn_${dec}0501*.nc ]; then
#             echo "File for decade ${dec} is missing in ${savedir}"
        
#             # calculate the missing dec
#             echo "recalculate ${base_dir}r${member}i1p1f1/${var}_day_MPI-ESM1-2-LR_r${member}i1p1f1_gn_${dec}0501-$((dec+9))0930.nc"
#             ./anomaly.sh ${base_dir}r${member}i1p1f1/${var}_day_MPI-ESM1-2-LR_r${member}i1p1f1_gn_${dec}0501-$((dec+9))0930.nc
#         fi
#     done
# done