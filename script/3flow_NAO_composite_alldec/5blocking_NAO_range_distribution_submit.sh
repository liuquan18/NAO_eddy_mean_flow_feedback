#!/bin/bash
#SBATCH --job-name=NAO_dis
#SBATCH --time=01:00:00
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem=200G
#SBATCH --mail-type=FAIL
#SBATCH --account=mh0033
#SBATCH --output=NAO_dis.%j.out


decade=$1
var=$2
name=$3
model_dir=$4
plev=$5
base_dir=$6
suffix=""
# mpirun -n 5 python 5var_NAO_range_distribution.py $decade $var $name $model_dir $plev $suffix
python 5blocking_NAO_range_distribution.py $decade $var $name $model_dir $plev $base_dir $suffix