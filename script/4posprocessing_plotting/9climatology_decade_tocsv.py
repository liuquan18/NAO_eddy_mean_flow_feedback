#%%
import xarray as xr
import numpy as np
import pandas as pd
from glob import glob
import os
# %%
to_dir = "/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/0climatology_alldec/"
def read_data(var_name, model_dir = 'MPI_GE_CMIP6_allplev', plev=None):
    data_dir = f"/work/mh0033/m300883/High_frequecy_flow/data/{model_dir}/{var_name}_monthly_ensmean/"
    files = glob(os.path.join(data_dir, "*.nc"))
    data = xr.open_mfdataset(files, combine="by_coords")
    # 
    if plev is not None:
        data = data.sel(plev=plev)
    
    # yearly mean
    data_ym = data.groupby("time.year").mean(dim="time")
    
    if 'lon' in data_ym.coords:
        # lon to -180 to 180
        data_ym = data_ym.assign_coords(lon=(data_ym.lon + 180) % 360 - 180).sortby("lon")
    return data_ym.load()

# %%
zg_hat = read_data("zg_hat", plev=50000)
# %%
GB_index = zg_hat.sel(lon=slice(-80, -20), lat=slice(60, 80)).mean(dim=("lon", "lat"))['zg']
GB_index.to_dataframe().to_csv(f"{to_dir}GB_index.csv")
# %%
eady_growth_rate = read_data("eady_growth_rate", plev = 85000)
baroclinicity = eady_growth_rate.sel(lon=slice(-90, 40), lat=slice(50, 70)).mean(dim=("lon", "lat"))['eady_growth_rate']
baroclinicity.to_dataframe().to_csv(f"{to_dir}baroclinicity.csv")
# %%

jet_lat = read_data("jet_latitude")

# %%
jet_lat.to_dataframe().to_csv(f"{to_dir}jet_latitude.csv")
# %%
awb = read_data("wb_anticyclonic_allisen", model_dir = 'MPI_GE_CMIP6')
# %%
awb_index = awb.sel(lon=slice(-90, 40), lat=slice(40, 60)).mean(dim=("lon", "lat"))['smooth_pv']
awb_index.to_dataframe().to_csv(f"{to_dir}awb_index.csv")
# %%
thermal = read_data("steady_eddy_heat_d2y2", plev = 85000)
# %%
thermal.to_dataframe().to_csv(f"{to_dir}eddy_heat_d2y2.csv")
# %%
