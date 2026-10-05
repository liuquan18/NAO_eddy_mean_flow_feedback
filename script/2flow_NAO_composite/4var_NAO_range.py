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

        # average over the event
        var_pos = var_pos.mean(dim='event')
        var_neg = var_neg.mean(dim='event')

    return var_pos, var_neg
# %%
decade = int(sys.argv[1]) if len(sys.argv) > 1 else 1850
var = sys.argv[2] if len(sys.argv) > 2 else 'ua'
name = sys.argv[3] if len(sys.argv) > 3 else var
model_dir = sys.argv[4] if len(sys.argv) > 4 else 'MPI_GE_CMIP6'
plev = int(sys.argv[5]) if len(sys.argv) > 5 else None
suffix = sys.argv[6] if len(sys.argv) > 6 else ''

# report the input
logging.info(f"Rank {rank} of {size} is processing {var} for decade {decade}, model_dir {model_dir}, name {name}, plev {plev} suffix {suffix}")
# %%
members = np.arange(1, 51)  # all members
members_single = np.array_split(members, size)[rank]  # members on this core

# %%

theta_2PVU_poss = []
theta_2PVU_negs = []
for i, member in enumerate(members_single):
    print(f"Rank {rank}, member {member}/{members_single[-1]}")

    theta_2pvu_pos, theta_2pvu_neg = composite_single_ens(var, decade=decade, ens=member, name = name, suffix = suffix, model_dir=model_dir, plev=plev)

    theta_2PVU_poss.append(theta_2pvu_pos)
    theta_2PVU_negs.append(theta_2pvu_neg)


# combine all members from all cores
theta_2PVU_poss = comm.gather(theta_2PVU_poss, root=0)
theta_2PVU_negs = comm.gather(theta_2PVU_negs, root=0)

# concatenate the results 
if rank == 0:

    # Flatten the gathered lists
    theta_2PVU_poss = [item for sublist in theta_2PVU_poss for item in sublist]
    theta_2PVU_negs = [item for sublist in theta_2PVU_negs for item in sublist]

    theta_2PVU_poss = xr.concat(theta_2PVU_poss, dim='ens', coords = 'all')
    theta_2PVU_negs = xr.concat(theta_2PVU_negs, dim='ens', coords = 'all')

    # save the results
    theta_2PVU_poss.to_netcdf(f'/work/mh0033/m300883/High_frequecy_flow/data/{model_dir}/0composite_range/{var}{suffix}_NAO_pos_{decade}.nc')
    theta_2PVU_negs.to_netcdf(f'/work/mh0033/m300883/High_frequecy_flow/data/{model_dir}/0composite_range/{var}{suffix}_NAO_neg_{decade}.nc')
