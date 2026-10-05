#!/bin/bash
# transient eddies
./3eddy_fluxes_master.sh up vp 
./3eddy_fluxes_master.sh vp etp
./3eddy_fluxes_master.sh up qp
./3eddy_fluxes_master.sh vp qp
# steady eddies
./3eddy_fluxes_master.sh us vs
./3eddy_fluxes_master.sh vs ets
./3eddy_fluxes_master.sh us qs
./3eddy_fluxes_master.sh vs qs