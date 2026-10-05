#!/bin/bash
#SBATCH --job-name=eady
#SBATCH --time=01:00:00
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=5
#SBATCH --mem=200G
#SBATCH --mail-type=FAIL
#SBATCH --account=mh0033
#SBATCH --output=eady.%j.out



mpirun -n 5 python 4eady_growth_rate.py $1