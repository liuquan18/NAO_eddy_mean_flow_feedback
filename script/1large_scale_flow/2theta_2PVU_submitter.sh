#!/bin/bash
#SBATCH --job-name=2pvu
#SBATCH --time=01:00:00
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=5
#SBATCH --mem=200G
#SBATCH --mail-type=FAIL
#SBATCH --account=mh0033
#SBATCH --output=2pvu.%j.out



mpirun -n 5 python 2theta_2PVU.py $1