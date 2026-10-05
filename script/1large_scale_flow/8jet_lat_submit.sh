#!/bin/bash
#SBATCH --job-name=jet_lat
#SBATCH --time=00:30:00
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=5
#SBATCH --mem=200G
#SBATCH --mail-type=FAIL
#SBATCH --account=mh0033
#SBATCH --output=jet_lat.%j.out



mpirun -n 5 python 8jet_lat.py $1
