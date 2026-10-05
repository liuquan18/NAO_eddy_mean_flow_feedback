#%%
import xarray as xr
import numpy as np

from src.dynamics.theta_on_pv import cal_pv_isent
# %%
import logging
import os
import glob
import sys

logging.basicConfig(level=logging.INFO)



# %%
node = sys.argv[1]
ens = int(node)
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
ua_path = f"/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/ua_daily/r{ens}i1p1f1/"
va_path = f"/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/va_daily/r{ens}i1p1f1/"
ta_path = f"/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/ta_daily/r{ens}i1p1f1/"

# save path
pv_path = f"/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6/pv_daily/r{ens}i1p1f1/"
if rank == 0:
    if not os.path.exists(pv_path):
        os.makedirs(pv_path)

# %%
all_decades = np.arange(1850, 2100, 10)
single_decades = np.array_split(all_decades, size)[rank]
# %%
for i, dec in enumerate(single_decades):
    logging.info(f"rank {rank} Processing {i+1}/{len(single_decades)}")

    # read data
    logging.info(f"   reading data for {dec}...")
    ua_file = glob.glob(ua_path + f"*{dec}*.nc")
    va_file = glob.glob(va_path + f"*{dec}*.nc")
    ta_file = glob.glob(ta_path + f"*{dec}*.nc")

    ua = xr.open_dataset(ua_file[0]).ua
    va = xr.open_dataset(va_file[0]).va
    ta = xr.open_dataset(ta_file[0]).ta

    logging.info(f"   calculating pv...")
    # calculate theta on 2PVU
    pv = cal_pv_isent(ta, ua, va)

    # drop the 'metpy_crs'
    try:
        pv = pv.drop_vars("metpy_crs")
    except AttributeError:
        # If the variable does not exist, we can safely ignore this error
        pass

    pv = pv.metpy.dequantify()
    logging.info (f"   saving data for {dec}...")
    pv.to_netcdf(
        pv_path + f"pv_day_MPI-ESM1-2-LR_r{ens}i1p1f1_gn_{dec}0501-{dec+9}0930.nc"
    )