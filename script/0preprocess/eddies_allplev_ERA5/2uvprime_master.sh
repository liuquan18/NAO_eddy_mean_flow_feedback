#!/bin/bash

for year in {2005..2024..5}
do
    start_year=$year
    end_year=$((year+4))

    if [ $end_year -gt 2024 ]; then
        end_year=2024
    fi

    echo "This node is calculating VKE for ${start_year} to ${end_year}"

    sbatch 2uvprime.sh $start_year $end_year
done