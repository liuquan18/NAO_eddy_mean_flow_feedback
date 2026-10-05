#!/bin/bash
# decade
decade=$1
suffix=$2
# sbatch 4var_NAO_range_submit.sh $decade wb_anticyclonic flag MPI_GE_CMIP6_allplev
# sbatch 4var_NAO_range_submit.sh $decade wb_cyclonic flag MPI_GE_CMIP6_allplev

sbatch 4var_NAO_range_submit.sh $decade upvp upvp MPI_GE_CMIP6_allplev $suffix
sbatch 4var_NAO_range_submit.sh $decade vpetp vpetp MPI_GE_CMIP6_allplev $suffix
# sbatch 4var_NAO_range_submit.sh $decade upqp upqp MPI_GE_CMIP6_allplev
# sbatch 4var_NAO_range_submit.sh $decade vpqp vpqp MPI_GE_CMIP6_allplev

sbatch 4var_NAO_range_submit.sh $decade usvs usvs MPI_GE_CMIP6_allplev $suffix
sbatch 4var_NAO_range_submit.sh $decade vsets vsets MPI_GE_CMIP6_allplev $suffix


sbatch ./4var_NAO_range_submit.sh 1850 Fdiv_p_transient div2 MPI_GE_CMIP6_allplev 85000 _ano
sbatch ./4var_NAO_range_submit.sh 2090 Fdiv_p_transient div2 MPI_GE_CMIP6_allplev 85000 _ano

sbatch ./4var_NAO_range_submit.sh 1850 Fdiv_phi_transient div MPI_GE_CMIP6_allplev 25000 _ano
sbatch ./4var_NAO_range_submit.sh 2090 Fdiv_phi_transient div MPI_GE_CMIP6_allplev 25000 _ano

sbatch ./4var_NAO_range_submit.sh 1850 Fdiv_p_steady div2 MPI_GE_CMIP6_allplev 85000 _ano
sbatch ./4var_NAO_range_submit.sh 2090 Fdiv_p_steady div2 MPI_GE_CMIP6_allplev 85000 _ano

sbatch ./4var_NAO_range_submit.sh 1850 Fdiv_phi_steady div MPI_GE_CMIP6_allplev 25000 _ano
sbatch ./4var_NAO_range_submit.sh 1850 Fdiv_phi_transient div MPI_GE_CMIP6_allplev 25000 _ano


