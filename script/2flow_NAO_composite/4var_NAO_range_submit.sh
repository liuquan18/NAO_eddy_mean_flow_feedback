#!/bin/bash
#SBATCH --job-name=NAO_range
#SBATCH --time=01:00:00
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=5
#SBATCH --mem=200G
#SBATCH --mail-type=FAIL
#SBATCH --account=mh0033
#SBATCH --output=NAO_range.%j.out


decade=$1
var=$2
name=$3
model_dir=$4
plev=$5
suffix=$6
mpirun -n 5 python 4var_NAO_range.py $decade $var $name $model_dir $plev $suffix