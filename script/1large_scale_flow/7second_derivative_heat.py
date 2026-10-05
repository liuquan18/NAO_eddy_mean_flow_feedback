#%%
import xarray as xr
import numpy as np
from metpy.units import units
import os
import sys
import metpy
import metpy.calc as mpcalc
from src.data_helper.read_variable import read_prime_single_ens

import logging
# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def second_derivative_heat(decade, ens, eddy='transient', **kwargs):
    """
    Calculate the second derivative of heat flux with respect to latitude
    """
    equiv_theta = kwargs.get('equiv_theta', True)
    if eddy == 'transient':
        if equiv_theta:
            vptp = read_prime_single_ens(decade, ens, 'vpetp', **kwargs)
        else:
            vptp = read_prime_single_ens(decade, ens, 'vptp', **kwargs)
    elif eddy == 'steady':
        if equiv_theta:
            vptp = read_prime_single_ens(decade, ens, 'vsets', **kwargs)   
        else:
            vptp = read_prime_single_ens(decade, ens, 'vsts',  **kwargs)

    else:
        raise ValueError("eddy must be 'transient' or 'steady'")

    # metpy
    vptp = vptp.metpy.assign_crs(
            grid_mapping_name='latitude_longitude',
            earth_radius=6371229.0
        )
    vptp = vptp * units('K m s-1')
    
    # Calculate the second derivative with respect to latitude
    dx, dy = mpcalc.lat_lon_grid_deltas(vptp.lon, vptp.lat)
    # second derivative on y
    d2vptpdy2 = mpcalc.second_derivative(vptp, dy=dy, axis=2)

    d2vptpdy2.name = 'eddy_heat_d2y2'

    d2vptpdy2 = d2vptpdy2.metpy.dequantify()
    d2vptpdy2 = d2vptpdy2.drop_vars('metpy_crs')

    # save
    save_dir = f"/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/{eddy}_eddy_heat_d2y2_daily/r{ens}i1p1f1/"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        
    d2vptpdy2.to_netcdf(os.path.join(save_dir, f"eddy_heat_d2y2_{decade}.nc"))
# %%

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

    
    # transient
    logging.info(f"Processing transient eddy for decade {dec} and ensemble {ens}")
    second_derivative_heat(dec, ens, eddy='transient', equiv_theta=True, model_dir='MPI_GE_CMIP6_allplev', suffix = '')

    # steady
    logging.info(f"Processing steady eddy for decade {dec} and ensemble {ens}")
    second_derivative_heat(dec, ens, eddy='steady', equiv_theta=True, model_dir='MPI_GE_CMIP6_allplev', suffix = '')
