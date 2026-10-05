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
model_dir = sys.argv[4] if len(sys.argv) > 4 else 'MPI_GE_CMIP6'

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


# Write per-rank results to temp files to avoid MPI 2GB message size limit
import tempfile, os, glob

save_dir = "/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/0composite_distribution/"
tmp_dir = os.path.join(save_dir, f"tmp_{decade}_{var}{suffix}")
if rank == 0:
    os.makedirs(tmp_dir, exist_ok=True)
comm.Barrier()

poss_valid = [x for x in theta_2PVU_poss if x is not None]
negs_valid = [x for x in theta_2PVU_negs if x is not None]

if poss_valid:
    xr.concat(poss_valid, dim='event').to_netcdf(os.path.join(tmp_dir, f"pos_rank{rank}.nc"))
if negs_valid:
    xr.concat(negs_valid, dim='event').to_netcdf(os.path.join(tmp_dir, f"neg_rank{rank}.nc"))

comm.Barrier()

if rank == 0:
    pos_files = sorted(glob.glob(os.path.join(tmp_dir, "pos_rank*.nc")))
    neg_files = sorted(glob.glob(os.path.join(tmp_dir, "neg_rank*.nc")))

    xr.open_mfdataset(pos_files, combine='nested', concat_dim='event').to_netcdf(
        f'{save_dir}{var}{suffix}_NAO_pos_{decade}.nc')
    xr.open_mfdataset(neg_files, combine='nested', concat_dim='event').to_netcdf(
        f'{save_dir}{var}{suffix}_NAO_neg_{decade}.nc')

    for f in pos_files + neg_files:
        os.remove(f)
    os.rmdir(tmp_dir)
