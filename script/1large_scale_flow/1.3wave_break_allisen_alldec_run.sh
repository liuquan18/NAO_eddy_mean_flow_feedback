#!/bin/bash
#SBATCH --job-name=wb_isent
#SBATCH --output=wb_isent.%j.out
#SBATCH --nodes=13
#SBATCH --ntasks-per-node=1
#SBATCH --time=01:00:00
#SBATCH --partition=compute
#SBATCH --cpus-per-task=1
#SBATCH --mem=0
#SBATCH --account=mh0033

# Load modules
module load python3/unstable
module load intel-oneapi-mpi/2021.5.0-intel-2021.5.0

# Activate conda
source ~/.bashrc
conda activate air_sea

# Set PMI library
export I_MPI_PMI_LIBRARY=/usr/lib64/libpmi.so
export TQDM_DISABLE=1

# Launch MPI job directly

for dec in $(seq 1860 10 2080)
do
  srun --mpi=pmi2 python 1.3wave_break_allisen_alldec.py $1 $dec # ens # decade
done

# srun --mpi=pmi2 python 1.3wave_break_allisen_alldec.py $1 $2 # ens # decade