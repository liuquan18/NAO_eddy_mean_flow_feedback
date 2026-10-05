#%%
import xarray as xr
import numpy as np
from src.data_helper.read_NAO_extremes import read_NAO_extremes_single_ens
from src.composite import composite
from src.data_helper import read_variable
import sys
import logging
logging.basicConfig(level=logging.INFO)
import importlib
import pandas as pd
importlib.reload(composite)
importlib.reload(read_variable)
read_prime_single_ens = read_variable.read_prime_single_ens
range_NAO_composite = composite.range_NAO_composite

#%%
import mpi4py.MPI as MPI
# %%
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
name = MPI.Get_processor_name()
#%%
def composite_single_ens(var, decade, ens, **kwargs):
    # read NAO extremes
    pos_extreme = read_NAO_extremes_single_ens('pos', decade, ens)
    neg_extreme = read_NAO_extremes_single_ens('neg', decade, ens)

    # read variable
    var_field = read_prime_single_ens( decade, ens,var, **kwargs)

    if not pos_extreme.empty and not neg_extreme.empty:

        var_pos, var_neg = range_NAO_composite(var_field, pos_extreme, neg_extreme)

    else:
        var_pos = None
        var_neg = None
    return var_pos, var_neg
# %%
# %%
decade = int(sys.argv[1]) if len(sys.argv) > 1 else 1850
var = sys.argv[2] if len(sys.argv) > 2 else 'ua'
name = sys.argv[3] if len(sys.argv) > 3 else var
model_dir = sys.argv[4] if len(sys.argv) > 4 else 'MPI_GE_CMIP6_allplev'

# Check if the argument is 'None' string before converting to int
plev_arg = sys.argv[5] if len(sys.argv) > 5 else None
plev = int(plev_arg) if plev_arg is not None and plev_arg != 'None' else None

base_dir = sys.argv[6] if len(sys.argv) > 6 else '/work/mh0033/m300883/High_frequecy_flow/data/'
suffix = sys.argv[7] if len(sys.argv) > 7 else ''

# report the input
logging.info(f"Rank {rank} of {size} is processing {var} for decade {decade}, model_dir {model_dir}, name {name}, suffix {suffix}, plev {plev}")
# %%
members = np.arange(1, 51)  # all members
members_single = np.array_split(members, size)[rank]  # members on this core

# %%

theta_2PVU_poss = []
theta_2PVU_negs = []
for i, member in enumerate(members_single):
    print(f"Rank {rank}, member {member}/{members_single[-1]}")

    theta_2pvu_pos, theta_2pvu_neg = composite_single_ens(var, decade=decade, ens=member, name = name, suffix = suffix, model_dir=model_dir, plev = plev)

    theta_2PVU_poss.append(theta_2pvu_pos)
    theta_2PVU_negs.append(theta_2pvu_neg)


# # combine all members from all cores
# theta_2PVU_poss = comm.gather(theta_2PVU_poss, root=0)
# theta_2PVU_negs = comm.gather(theta_2PVU_negs, root=0)

# # concatenate the results 
# if rank == 0:

# # Flatten the gathered lists
# theta_2PVU_poss = [item for sublist in theta_2PVU_poss for item in sublist if item is not None]
# theta_2PVU_negs = [item for sublist in theta_2PVU_negs for item in sublist if item is not None]


# concat the results
theta_2PVU_poss = xr.concat([x for x in theta_2PVU_poss if x is not None], dim='event')
theta_2PVU_negs = xr.concat([x for x in theta_2PVU_negs if x is not None], dim='event')

#%%
# postprocessing to align with the scatter plot
# Count, if >=20% of pixels in box have WB (value==1), then count as 1 occurrence, else 0.
# awb region [-60, 30, 40, 60], cwb region [-120, -30, 50, 70]

def _fld_mean(da, lat_min = 40, lat_max = 60, lon_min=-90, lon_max=40):
    """Zonal mean over [lon_min, lon_max], handling both 0-360 and -180-180 grids."""
    if da.lon.max() > 180:
        # Convert 0-360 to -180-180
        da = da.assign_coords(lon=(da.lon + 180) % 360 - 180).sortby("lon")
    return da.sel(lat = slice(lat_min, lat_max), lon=slice(lon_min, lon_max)).mean(dim=("lon", "lat"), skipna=True)

theta_2PVU_poss = _fld_mean(theta_2PVU_poss)
theta_2PVU_negs = _fld_mean(theta_2PVU_negs)

# save the results
save_dir = "/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/0composite_alldec/"

theta_2PVU_poss.to_netcdf(f'{save_dir}{var}{suffix}_NAO_pos_{decade}.nc')
theta_2PVU_negs.to_netcdf(f'{save_dir}{var}{suffix}_NAO_neg_{decade}.nc')
