#!/bin/bash
#SBATCH --job-name=ensmean
#SBATCH --time=01:00:00
#SBATCH --partition=compute
#SBATCH --nodes=25
#SBATCH --ntasks=25
#SBATCH --ntasks-per-node=1
#SBATCH --mem=200G
#SBATCH --mail-type=FAIL
#SBATCH --account=mh0033
#SBATCH --output=ensmean.%j.out

module load cdo/2.5.0-gcc-11.2.0
module load parallel    

var=$1 

export var

parallel --jobs $SLURM_NTASKS srun --nodes=1 --ntasks=1 --ntasks-per-node=1 dec_mean.sh ::: {1850..2090..10} ::: $var
