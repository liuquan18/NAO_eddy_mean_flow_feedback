#!/bin/bash

sbatch 5var_NAO_range_distribution_submit.sh 1850 upvp upvp MPI_GE_CMIP6_allplev
sbatch 5var_NAO_range_distribution_submit.sh 2090 upvp upvp MPI_GE_CMIP6_allplev

sbatch 5var_NAO_range_distribution_submit.sh 1850 usvs usvs MPI_GE_CMIP6_allplev
sbatch 5var_NAO_range_distribution_submit.sh 2090 usvs usvs MPI_GE_CMIP6_allplev

sbatch 5var_NAO_range_distribution_submit.sh 1850 vpetp vpetp MPI_GE_CMIP6_allplev #no suffix
sbatch 5var_NAO_range_distribution_submit.sh 2090 vpetp vpetp MPI_GE_CMIP6_allplev 

sbatch 5var_NAO_range_distribution_submit.sh 1850 vsets vsets MPI_GE_CMIP6_allplev #no suffix
sbatch 5var_NAO_range_distribution_submit.sh 2090 vsets vsets MPI_GE_CMIP6_allplev

sbatch 5var_NAO_range_distribution_submit.sh 1850 ta ta MPI_GE_CMIP6_allplev #no suffix
sbatch 5var_NAO_range_distribution_submit.sh 2090 ta ta MPI_GE_CMIP6_allplev

sbatch 5var_NAO_range_distribution_submit.sh 1850 ta_hat ta MPI_GE_CMIP6_allplev #no suffix
sbatch 5var_NAO_range_distribution_submit.sh 2090 ta_hat ta MPI_GE_CMIP6_allplev

sbatch 5var_NAO_range_distribution_submit.sh 1850 M2_prime M2 MPI_GE_CMIP6_allplev #no suffix
sbatch 5var_NAO_range_distribution_submit.sh 2090 M2_prime M2 MPI_GE_CMIP6_allplev

sbatch 5var_NAO_range_distribution_submit.sh 1850 M2_steady M2 MPI_GE_CMIP6_allplev #no suffix
sbatch 5var_NAO_range_distribution_submit.sh 2090 M2_steady M2 MPI_GE_CMIP6_allplev


# EP flux divergence with ano


sbatch ./5var_NAO_range_distribution_submit.sh 1850 ua ua MPI_GE_CMIP6_allplev None /work/mh0033/m300883/High_frequecy_flow/data/ _ano
sbatch ./5var_NAO_range_distribution_submit.sh 2090 ua ua MPI_GE_CMIP6_allplev None /work/mh0033/m300883/High_frequecy_flow/data/ _ano


sbatch ./5var_NAO_range_distribution_submit.sh 1850 Fdiv_p_transient div2 MPI_GE_CMIP6_allplev 25000 /work/mh0033/m300883/High_frequecy_flow/data/ _ano
sbatch ./5var_NAO_range_distribution_submit.sh 2090 Fdiv_p_transient div2 MPI_GE_CMIP6_allplev 25000 /work/mh0033/m300883/High_frequecy_flow/data/ _ano

sbatch ./5var_NAO_range_distribution_submit.sh 1850 Fdiv_phi_transient div MPI_GE_CMIP6_allplev 25000 /work/mh0033/m300883/High_frequecy_flow/data/ _ano
sbatch ./5var_NAO_range_distribution_submit.sh 2090 Fdiv_phi_transient div MPI_GE_CMIP6_allplev 25000 /work/mh0033/m300883/High_frequecy_flow/data/ _ano

sbatch ./5var_NAO_range_distribution_submit.sh 1850 Fdiv_p_steady div2 MPI_GE_CMIP6_allplev 25000 /work/mh0033/m300883/High_frequecy_flow/data/ _ano   
sbatch ./5var_NAO_range_distribution_submit.sh 2090 Fdiv_p_steady div2 MPI_GE_CMIP6_allplev 25000 /work/mh0033/m300883/High_frequecy_flow/data/ _ano

sbatch ./5var_NAO_range_distribution_submit.sh 1850 Fdiv_phi_steady div MPI_GE_CMIP6_allplev 25000 /work/mh0033/m300883/High_frequecy_flow/data/ _ano
sbatch ./5var_NAO_range_distribution_submit.sh 2090 Fdiv_phi_steady div MPI_GE_CMIP6_allplev 25000 /work/mh0033/m300883/High_frequecy_flow/data/ _ano

# eke with ano
sbatch ./5var_NAO_range_distribution_submit.sh 1850 eke eke MPI_GE_CMIP6 50000 /work/mh0033/m300883/High_frequecy_flow/data/ _ano
sbatch ./5var_NAO_range_distribution_submit.sh 2090 eke eke MPI_GE_CMIP6 50000 /work/mh0033/m300883/High_frequecy_flow/data/ _ano

# baroclinicity with ano
sbatch ./5var_NAO_range_distribution_submit.sh 1850 eady_growth_rate eady_growth_rate MPI_GE_CMIP6_allplev 85000 /work/mh0033/m300883/High_frequecy_flow/data/ _ano
sbatch ./5var_NAO_range_distribution_submit.sh 2090 eady_growth_rate eady_growth_rate MPI_GE_CMIP6_allplev 85000 /work/mh0033/m300883/High_frequecy_flow/data/ _ano

# transient eddy heat d2y2
sbatch ./5var_NAO_range_distribution_submit.sh 1850 transient_eddy_heat_d2y2 eddy_heat_d2y2 MPI_GE_CMIP6_allplev 85000 /work/mh0033/m300883/High_frequecy_flow/data/ _ano
sbatch ./5var_NAO_range_distribution_submit.sh 2090 transient_eddy_heat_d2y2 eddy_heat_d2y2 MPI_GE_CMIP6_allplev 85000 /work/mh0033/m300883/High_frequecy_flow/data/ _ano

# steady eddy heat d2y2
sbatch ./5var_NAO_range_distribution_submit.sh 1850 steady_eddy_heat_d2y2 eddy_heat_d2y2 MPI_GE_CMIP6_allplev 85000 /work/mh0033/m300883/High_frequecy_flow/data/ _ano
sbatch ./5var_NAO_range_distribution_submit.sh 2090 steady_eddy_heat_d2y2 eddy_heat_d2y2 MPI_GE_CMIP6_allplev 85000 /work/mh0033/m300883/High_frequecy_flow/data/ _ano


# without ano
sbatch ./5var_NAO_range_distribution_submit.sh 1850 Fdiv_p_transient div2 MPI_GE_CMIP6_allplev 25000 /work/mh0033/m300883/High_frequecy_flow/data/ 
sbatch ./5var_NAO_range_distribution_submit.sh 2090 Fdiv_p_transient div2 MPI_GE_CMIP6_allplev 25000 /work/mh0033/m300883/High_frequecy_flow/data/

sbatch ./5var_NAO_range_distribution_submit.sh 1850 Fdiv_phi_transient div MPI_GE_CMIP6_allplev 25000 /work/mh0033/m300883/High_frequecy_flow/data/
sbatch ./5var_NAO_range_distribution_submit.sh 2090 Fdiv_phi_transient div MPI_GE_CMIP6_allplev 25000 /work/mh0033/m300883/High_frequecy_flow/data/

sbatch ./5var_NAO_range_distribution_submit.sh 1850 Fdiv_p_steady div2 MPI_GE_CMIP6_allplev 25000 /work/mh0033/m300883/High_frequecy_flow/data/   
sbatch ./5var_NAO_range_distribution_submit.sh 2090 Fdiv_p_steady div2 MPI_GE_CMIP6_allplev 25000 /work/mh0033/m300883/High_frequecy_flow/data/

sbatch ./5var_NAO_range_distribution_submit.sh 1850 Fdiv_phi_steady div MPI_GE_CMIP6_allplev 25000 /work/mh0033/m300883/High_frequecy_flow/data/
sbatch ./5var_NAO_range_distribution_submit.sh 2090 Fdiv_phi_steady div MPI_GE_CMIP6_allplev 25000 /work/mh0033/m300883/High_frequecy_flow/data/

sbatch ./5var_NAO_range_distribution_submit.sh 1850 eke eke MPI_GE_CMIP6 50000 /work/mh0033/m300883/High_frequecy_flow/data/
sbatch ./5var_NAO_range_distribution_submit.sh 2090 eke eke MPI_GE_CMIP6 50000 /work/mh0033/m300883/High_frequecy_flow/data/

sbatch ./5var_NAO_range_distribution_submit.sh 1850 eady_growth_rate eady_growth_rate MPI_GE_CMIP6_allplev 85000 /work/mh0033/m300883/High_frequecy_flow/data/
sbatch ./5var_NAO_range_distribution_submit.sh 2090 eady_growth_rate eady_growth_rate MPI_GE_CMIP6_allplev 85000 /work/mh0033/m300883/High_frequecy_flow/data/

sbatch ./5var_NAO_range_distribution_submit.sh 1850 transient_eddy_heat_d2y2 eddy_heat_d2y2 MPI_GE_CMIP6_allplev 85000 /work/mh0033/m300883/High_frequecy_flow/data/
sbatch ./5var_NAO_range_distribution_submit.sh 2090 transient_eddy_heat_d2y2 eddy_heat_d2y2 MPI_GE_CMIP6_allplev 85000 /work/mh0033/m300883/High_frequecy_flow/data/

sbatch ./5var_NAO_range_distribution_submit.sh 1850 steady_eddy_heat_d2y2 eddy_heat_d2y2 MPI_GE_CMIP6_allplev 85000 /work/mh0033/m300883/High_frequecy_flow/data/
sbatch ./5var_NAO_range_distribution_submit.sh 2090 steady_eddy_heat_d2y2 eddy_heat_d2y2 MPI_GE_CMIP6_allplev 85000 /work/mh0033/m300883/High_frequecy_flow/data/

