# %%
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import pandas as pd
import seaborn as sns
import seaborn.objects as so
import cmocean
import os


from src.data_helper import read_composite
from src.data_helper.read_variable import read_climatology
import importlib
import matplotlib
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator

from src.plotting.util import map_smooth
import src.plotting.util as util

importlib.reload(read_composite)

read_EP_flux = read_composite.read_EP_flux
read_E_div = read_composite.read_E_div
read_comp_var = read_composite.read_comp_var


# %%
MODEL_DIR = "MPI_GE_CMIP6_allplev"


def _read_all(var_name, name=None, method="no_stat", chunks=None):
    """Read pos/neg x 1850/2090 composites.

    Returns a dict keyed by '{phase}_{decade}', e.g. 'pos_1850'.
    """
    kwargs = dict(time_window="all", model_dir=MODEL_DIR)
    if method is not None:
        kwargs["method"] = method
    if name is not None:
        kwargs["name"] = name
    if chunks is not None:
        kwargs["chunks"] = chunks
    return {
        f"{phase}_{decade}": read_comp_var(var_name, phase, decade, **kwargs).sum(dim = 'isen_level', skipna=True)
        for phase in ("pos", "neg")
        for decade in (1850, 2090)
    }


#%%
# Wave breaking (isen_level summed lazily to avoid OOM on large 5-D arrays)
awb = _read_all("wb_anticyclonic_allisen", name="smooth_pv", chunks=None)
#%%
cwb = _read_all("wb_cyclonic_allisen", name="smooth_pv", chunks=None)

#%%
# Count, if >=10% of pixels in box have WB (value==1), then count as 1 occurrence, else 0.
# awb region [-60, 30, 40, 60], cwb region [-120, -30, 50, 70]
def _fld_mean(da, lat_min = 40, lat_max = 60, lon_min=-90, lon_max=40):
    """Zonal mean over [lon_min, lon_max], handling both 0-360 and -180-180 grids."""
    if da.lon.max() > 180:
        # Convert 0-360 to -180-180
        da = da.assign_coords(lon=(da.lon + 180) % 360 - 180).sortby("lon")
    return da.sel(lat = slice(lat_min, lat_max), lon=slice(lon_min, lon_max)).mean(dim=("lon", "lat"), skipna=True)

# %% Save all variables to 0composite_feedback

save_xr_dir = "/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/0composite_feedback"
os.makedirs(save_xr_dir, exist_ok=True)

save_df_dir = "/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/0eddy_momentum_pd/non_anomaly"
os.makedirs(save_df_dir, exist_ok=True)
#%%
awb_to_save = {
    "wb_anticyclonic_pos_1850":       awb["pos_1850"],
    "wb_anticyclonic_neg_1850":       awb["neg_1850"],
    "wb_anticyclonic_pos_2090":       awb["pos_2090"],
    "wb_anticyclonic_neg_2090":       awb["neg_2090"],
}
# awb_lon_slice = slice(-60, 30)
# cwb_lon_slice = slice(-120, -30)
save_xr_dir
# awb save
for fname, da in awb_to_save.items():
    xr_path = os.path.join(save_xr_dir, f"{fname}.nc")
    awb_count = _fld_mean(da, lat_min = 40, lat_max=60, lon_min=-60, lon_max=30)
    # save xarray
    # awb_count.to_netcdf(xr_path)
    # save df
    df = awb_count.to_dataframe("count").reset_index()
    df["phase"] = fname.split("_")[2] # pos or neg
    df["decade"] = fname.split("_")[3] # 1850 or 2090

    df_path = os.path.join(save_df_dir, f"{fname}.csv")
    df.to_csv(df_path, index=False)
    print(f"Saved {df_path}")

#%%
cwb_to_save = {
    "wb_cyclonic_pos_1850":          cwb["pos_1850"],
    "wb_cyclonic_neg_1850":          cwb["neg_1850"],
    "wb_cyclonic_pos_2090":          cwb["pos_2090"],
    "wb_cyclonic_neg_2090":          cwb["neg_2090"],
}
save_xr_dir

for fname, da in cwb_to_save.items():
    xr_path = os.path.join(save_xr_dir, f"{fname}.nc")
    cwb_count = _fld_mean(da, lat_min = 50, lat_max=70, lon_min=-120, lon_max=-30)
    # cwb_count.to_netcdf(xr_path)
    df = cwb_count.to_dataframe("count").reset_index()
    df["phase"] = fname.split("_")[2] # pos or neg
    df["decade"] = fname.split("_")[3] # 1850 or 2090
    df_path = os.path.join(save_df_dir, f"{fname}.csv")
    df.to_csv(df_path, index=False)
    print(f"Saved {df_path}")
# %%

#%%