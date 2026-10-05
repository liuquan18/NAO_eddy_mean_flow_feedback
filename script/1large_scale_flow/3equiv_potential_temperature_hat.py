#%%
import xarray as xr
import numpy as np
import os
import sys
import logging
import glob
logging.basicConfig(level=logging.INFO)
# %%
import src.dynamics.EP_flux as EP_flux
import importlib
importlib.reload(EP_flux)
# %%
member= sys.argv[1]
# %%
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
# from temperature to potential temperature
ta_path = f'/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/ta_hat_daily/r{member}i1p1f1/'
q_path = f'/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/hus_hat_daily/r{member}i1p1f1/'
to_path = f'/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/equiv_theta_hat_daily/r{member}i1p1f1/'

if rank == 0:
    if not os.path.exists(to_path):
        os.makedirs(to_path)
    logging.info(f"This node is processing ensemble member {member}")

# %%
all_decs = np.arange(1850, 2091, 10)
dec_core = np.array_split(all_decs, size)[rank]

# %%
for i, dec in enumerate (dec_core):
    logging.info(f"rank {rank} Processing decade {dec} {i+1}/{len(dec_core)}")
    ta_file = glob.glob(ta_path + f"*{dec}*.nc")
    q_file = glob.glob(q_path + f"*{dec}*.nc")
    ta_file = ta_file[0]
    q_file = q_file[0]
    basename = os.path.basename(ta_file)
    # replace the 'ta' in basename with 'theta'
    basename = basename.replace('ta', 'equiv_theta')
    to_file = os.path.join(to_path, basename)

    t = xr.open_dataset(ta_file).ta
    q = xr.open_dataset(q_file).hus
    # make sure the time dimension is the same
    if t.shape[0] != q.shape[0]:
        logging.warning(f"::: Warning: time dimension of {ta_file} and {q_file} do not match! :::")
        continue

    # calculate equivalent potential temperature
    ds = EP_flux.equivalent_potential_temperature(t, q, p='plev', p0=1e5)
    # save to netcdf
    ds.to_netcdf(to_file)
    ds.close()