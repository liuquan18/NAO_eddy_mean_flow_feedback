#!/bin/bash
#SBATCH --job-name=python
#SBATCH --time=01:00:00
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks=5
#SBATCH --mem=200G
#SBATCH --mail-type=FAIL
#SBATCH --account=mh0033
#SBATCH --output=python.%j.out

file=$1 # python file to run
ens=$2 # ensemble member

echo run $file of ens $ens
mpirun -n 5 python -u $file $ens
