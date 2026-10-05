#!/bin/bash
#SBATCH --job-name=wb
#SBATCH --time=01:00:00
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=10
#SBATCH --mem=200G
#SBATCH --mail-type=FAIL
#SBATCH --account=mh0033
#SBATCH --output=wb.%j.out


# Disable tqdm progress bars
export TQDM_DISABLE=1

mpirun -n 10 python 1.0wave_break.py $1