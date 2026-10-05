#%%
import xarray as xr
import numpy as np
import logging
import os
import glob
import sys

logging.basicConfig(level=logging.INFO)

#%%
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

# %%
# save path
jet_lat_path = f"/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/jet_latitude_daily/r{ens}i1p1f1/"
if rank == 0:
    if not os.path.exists(jet_lat_path):
        os.makedirs(jet_lat_path)

#%%

def jet_latitude(ua):
    # a limit of jet loc between (0, 70)
    
    # average over lon if present, then find lat of max ua
    if ua.lon.max() > 180:
        # Convert 0-360 to -180-180
        ua = ua.assign_coords(lon=(ua.lon + 180) % 360 - 180).sortby("lon")
        ua = ua.sel(lon = slice(-90, 40), lat = slice(25, 75)).mean(dim="lon") # not too far south, not too far north

    if "plev" in ua.dims:
        # ua = ua.sel(plev=slice(92500, 70000)).mean(dim="plev") # eddy driven jet
        ua = ua.sel(plev = 25000) # upper level, for positive anyways.
    jet_lat = ua.idxmax(dim="lat")

    return jet_lat


# %%
all_decades = np.arange(1850, 2100, 10)
single_decades = np.array_split(all_decades, size)[rank]

# %%

for i, dec in enumerate(single_decades):
    logging.info(f"rank {rank} Processing {i+1}/{len(single_decades)}")

    # read data
    logging.info(f"   reading data for {dec}...")
    ua_file = glob.glob(ua_path + f"*{dec}*.nc")
    if not ua_file:
        logging.warning(f"No ua file found for decade {dec}. Skipping.")
        continue
    ua = xr.open_dataset(ua_file[0])

    logging.info(f"   calculating jet latitude...")
    jet_lat = jet_latitude(ua.ua)

    # copy attributes from ua to jet_lat
    jet_lat.attrs = ua.ua.attrs

    logging.info(f"   saving jet latitude...")
    jet_lat.to_netcdf(jet_lat_path + f"jet_latitude_{dec}.nc")
# %%
