#!/bin/bash
#SBATCH --job-name=EP_flux_dec
#SBATCH --time=01:00:00
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=5
#SBATCH --mem=200G
#SBATCH --mail-type=FAIL
#SBATCH --account=mh0033
#SBATCH --output=EP_flux_dec.%j.out



mpirun -n 5 python 6EP_flux.py $1