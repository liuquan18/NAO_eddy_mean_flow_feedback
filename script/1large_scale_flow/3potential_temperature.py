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
from_path = f'/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/ta_daily/r{member}i1p1f1/'
to_path = f'/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/theta_daily/r{member}i1p1f1/'

if rank == 0:
    if not os.path.exists(to_path):
        os.makedirs(to_path)
    logging.info(f"This node is processing ensemble member {member}")

# %%
all_files = glob.glob(from_path + "*.nc")
files_core = np.array_split(all_files, size)[rank]
# %%
for i, file in enumerate (files_core):
    logging.info(f"rank {rank} Processing {i+1}/{len(files_core)}")
    basename = os.path.basename(file)
    # replace the 'ta' in basename with 'theta'
    basename = basename.replace('ta', 'theta')
    to_file = os.path.join(to_path, basename)

    ds = xr.open_dataset(file)

    theta = EP_flux.potential_temperature(ds['ta'], p='plev', p0=1e5)

    # save to netcdf
    theta.to_netcdf(to_file)
    theta.close()
    ds.close()
# %%

