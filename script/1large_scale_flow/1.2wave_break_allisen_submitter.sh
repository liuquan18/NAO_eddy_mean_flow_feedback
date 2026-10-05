#!/bin/bash
#SBATCH --job-name=wb
#SBATCH --time=06:00:00
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem=200G
#SBATCH --mail-type=FAIL
#SBATCH --account=mh0033
#SBATCH --output=wb.%j.out


# Disable tqdm progress bars
export TQDM_DISABLE=1

# mpirun -n 1 python 1wave_break_allisen.py $1
python 1.2wave_break_allisen.py $1