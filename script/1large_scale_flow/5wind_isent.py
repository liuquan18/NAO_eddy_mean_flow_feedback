#%%
import xarray as xr
import numpy as np

from src.dynamics.theta_on_pv import from_pressure_to_isentropic

import logging
import os
import glob
import sys

logging.basicConfig(level=logging.INFO)


# %%
node = sys.argv[1]
ens = int(node)
var = sys.argv[2] # ua, va,
logging.info(f"Processing ensemble {ens}")
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
# %%
var_path = f"/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/{var}_daily/r{ens}i1p1f1/"
ta_path = f"/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/ta_daily/r{ens}i1p1f1/"

# save path
save_path = f"/scratch/m/m300883/{var}_isentropic_daily/r{ens}i1p1f1/"
if rank == 0:
    if not os.path.exists(save_path):
        os.makedirs(save_path)

# %%
all_decades = np.arange(1850, 2100, 10)
single_decades = np.array_split(all_decades, size)[rank]
# %%
for i, dec in enumerate(single_decades):
    logging.info(f"rank {rank} Processing {i+1}/{len(single_decades)}")

    # read data
    logging.info(f"   reading data {var} and 'ta' for {dec}...")
    var_file = glob.glob(var_path + f"*{dec}*.nc")
    ta_file = glob.glob(ta_path + f"*{dec}*.nc")

    var_data = xr.open_dataset(var_file[0])
    
    # Get the variable name from the dataset (assuming only one data variable)
    var_name = list(var_data.data_vars)[-1]
    var_data = var_data[var_name]
    ta_data = xr.open_dataset(ta_file[0]).ta

    logging.info("   interpolating from pressure to isentropic surfaces...")
    # calculate theta on 2PVU
    var_isent = from_pressure_to_isentropic(var_data, ta_data)

    # drop the 'metpy_crs'
    try:
        var_isent = var_isent.drop_vars("metpy_crs")
    except ValueError:
        # If the variable does not exist, we can safely ignore this error
        pass

    var_isent = var_isent.metpy.dequantify()
    logging.info (f"   saving data for {dec}...")
    var_isent.to_netcdf(
        save_path + f"{var}_day_MPI-ESM1-2-LR_r{ens}i1p1f1_gn_{dec}0501-{dec+9}0930.nc"
    )
# %%
