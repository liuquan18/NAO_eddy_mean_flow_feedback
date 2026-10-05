# %%
import src.dynamics.EP_flux as EP_flux_module
import importlib
import sys
import os
import numpy as np

import logging
importlib.reload(EP_flux_module)
from src.dynamics.EP_flux import (  # noqa: E402
    EP_flux,
    eff_stat_stab_xr,
)
from src.data_helper.read_variable import read_prime_single_ens


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

#%%
def read_data_all_dec(decade, ens, eddy = 'transient', equiv_theta = True, **kwargs):
    """
    Read data for all members in a given decade
    """
    ta_hat = kwargs.get('ta_hat', True)
    if eddy == 'transient':
        N = 'upvp'
        if equiv_theta:
            P = 'vpetp'
        else:
            P = 'vptp'
    elif eddy == 'steady':
        N = 'usvs'
        if equiv_theta:
            P = 'vsets'
        else:
            P = 'vpts'

    if ta_hat:
        T = 'ta_hat'
    else:
        T = 'ta'

    upvp = read_prime_single_ens(decade, ens, N, name = N,**kwargs) 
    vptp = read_prime_single_ens(decade, ens, P, name = P, **kwargs)
    ta = read_prime_single_ens(decade, ens, T, name = 'ta', **kwargs)

    
    return upvp, vptp, ta

def calculate_EP_flux(decade, ens, equiv_theta=True, eddy='transient',suffix = ''):
    """
    Calculate EP flux for a given decade and phase
    """
    # Read data
    logging.info (f"Read data for {ens} ens in {decade}")



    upvp, vptp, ta = read_data_all_dec(decade, ens, equiv_theta=equiv_theta, eddy=eddy, model_dir = 'MPI_GE_CMIP6_allplev', suffix = suffix)

    logging.info (f"Calculate {eddy} EP flux for {ens} ens in {decade}")
    phi_dir = f"/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/Fphi_{eddy}_daily/r{ens}i1p1f1/"
    p_dir = f"/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/Fp_{eddy}_daily/r{ens}i1p1f1/"
    div1_dir = f"/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/Fdiv_phi_{eddy}_daily/r{ens}i1p1f1/"
    div2_dir = f"/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/Fdiv_p_{eddy}_daily/r{ens}i1p1f1/"

    for d in [phi_dir, p_dir, div1_dir, div2_dir]:
        if not os.path.exists(d):
            os.makedirs(d)

    # Calculate EP flux
    stat_stab = eff_stat_stab_xr(ta)
    F_phi, F_p, div_phi, div_p = EP_flux(vptp, upvp, stat_stab)

    # Save data
    logging.info (f"Save data for in {decade} of ens {ens}")
    F_phi.to_netcdf(f"{phi_dir}Fphi_{decade}_r{ens}i1p1f1.nc")
    F_p.to_netcdf(f"{p_dir}Fp_{decade}_r{ens}i1p1f1.nc")
    div_phi.to_netcdf(f"{div1_dir}Fdiv_phi_{decade}_r{ens}i1p1f1.nc")
    div_p.to_netcdf(f"{div2_dir}Fdiv_p_{decade}_r{ens}i1p1f1.nc")



#%%

# %%
node = sys.argv[1]
ens = int(node)
# %%
#%%
try:
    from mpi4py import MPI

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()  # [0,1,2,3,4,5,6,7,8,9]
    size = comm.Get_size()  # 10
except:
    logging.warning("::: Warning: Proceeding without mpi4py! :::")
    rank = 0
    size = 1
#%%
all_decades = np.arange(1850, 2100, 10)
single_decades = np.array_split(all_decades, size)[rank]
# %%
for i,dec in enumerate(single_decades):
    logging.info(f"rank {rank} Processing {i+1}/{len(single_decades)}")

    # calculate EP flux
    logging.info(f"Calculate transient EP flux for {ens} ens in {dec}")
    calculate_EP_flux(decade=dec, ens=ens, equiv_theta=True, eddy='transient', suffix = '')

    # calculate steady EP flux
    logging.info(f"Calculate steady EP flux for {ens} ens in {dec}")
    calculate_EP_flux(decade=dec, ens=ens, equiv_theta=True, eddy='steady', suffix = '')