#%%
from easyclimate.core.eddy import calc_eady_growth_rate
# %%
import xarray as xr
import numpy as np
import logging
import os
import sys
import glob

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
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
zg_path = f"/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/zg_daily/r{ens}i1p1f1/"
ta_path = f"/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/ta_daily/r{ens}i1p1f1/"

# save path

eddy_growth_rate_path = f"/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/eady_growth_rate_daily/r{ens}i1p1f1/"

if rank == 0:
    if not os.path.exists(eddy_growth_rate_path):
        os.makedirs(eddy_growth_rate_path)
# %%
all_decades = np.arange(1850, 2100, 10)
single_decades = np.array_split(all_decades, size)[rank]
# %%
for i, dec in enumerate(single_decades):
    logging.info(f"rank {rank} Processing {i+1}/{len(single_decades)}")

    # read data
    logging.info(f"   reading data for {dec}...")
    ua_file = glob.glob(ua_path + f"*{dec}*.nc")
    zg_file = glob.glob(zg_path + f"*{dec}*.nc")
    ta_file = glob.glob(ta_path + f"*{dec}*.nc")

    ua = xr.open_dataset(ua_file[0]).ua
    zg = xr.open_dataset(zg_file[0]).zg
    ta = xr.open_dataset(ta_file[0]).ta

    logging.info("   calculating eady growth rate...")
    egr = calc_eady_growth_rate(
        u_daily_data=ua,
        z_daily_data=zg,
        temper_daily_data=ta,
        vertical_dim='plev',
        vertical_dim_units='Pa',
        lat_dim='lat',
        g = 9.81,
    )

    egr = egr.eady_growth_rate

    # save
    logging.info(f"   saving data for {dec}...")
    egr.to_netcdf(os.path.join(eddy_growth_rate_path, f"eddy_growth_rate_{dec}0501_{dec}0930_r{ens}i1p1f1.nc"))
# %%
