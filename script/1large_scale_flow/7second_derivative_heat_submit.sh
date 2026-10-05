#!/bin/bash
#SBATCH --job-name=heat_d2y2
#SBATCH --time=01:00:00
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=5
#SBATCH --mem=200G
#SBATCH --mail-type=FAIL
#SBATCH --account=mh0033
#SBATCH --output=heat_d2y2.%j.out



mpirun -n 5 python 7second_derivative_heat.py $1
