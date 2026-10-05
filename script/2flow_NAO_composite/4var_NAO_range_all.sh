#!/bin/bash
# decade
decade=$1
sbatch 4var_NAO_range_submit.sh $decade wb_anticyclonic flag 
sbatch 4var_NAO_range_submit.sh $decade wb_cyclonic flag

sbatch 4var_NAO_range_submit.sh $decade upvp upvp _ano
sbatch 4var_NAO_range_submit.sh $decade vpetp vpetp _ano
sbatch 4var_NAO_range_submit.sh $decade upqp upqp _ano
sbatch 4var_NAO_range_submit.sh $decade vpqp vpqp _ano