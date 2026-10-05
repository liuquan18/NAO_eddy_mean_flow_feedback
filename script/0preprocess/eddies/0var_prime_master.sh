#!/bin/bash
var=$1 # variable to run
frequency=${2:-prime} # prime (2-12 days) or high (2-6 days), default prime
# print info, if frequency is not prime or high
if [ "$frequency" == "prime" ]; then
    echo frequency is set to prime
    echo "Filtering 2-12 days"

elif [ "$frequency" == "high" ]; then
    echo frequency is set to high
    echo "Filtering 2-6 days"
elif [ "$frequency" == "hat" ]; then
    echo frequency is set to hat
    echo "Filtering >30 days"
else
    echo "Frequency not recognized, please use prime or high"
    exit 1
fi

#for loop 1-50
for ens in {1..50}
do
    echo "Ensemble member ${ens}"
    # run the python script
    sbatch 0var_prime.sh ${ens} ${var} ${frequency}
    # ./1upvp.sh ${ens}
done