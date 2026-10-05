#!/bin/bash
#SBATCH --job-name=isent
#SBATCH --time=03:00:00
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=2
#SBATCH --mem=200G
#SBATCH --mail-type=FAIL
#SBATCH --account=mh0033
#SBATCH --output=isent.%j.out



mpirun -n 2 python 0pv_isent.py $1