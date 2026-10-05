# %%
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import pandas as pd
import seaborn as sns
import seaborn.objects as so
import cmocean


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

#%%
suffix =""
#%%
ua_pos_first = read_comp_var(
    "ua",
    "pos",
    1850,
    suffix = suffix,
    time_window=(0, 20),
    method='mean',
    name="ua",
    model_dir="MPI_GE_CMIP6_allplev",
)
# %%
ua_pos_last = read_comp_var(
    "ua",
    "pos",
    2090,
    suffix = suffix,
    time_window=(0, 20),
    method='mean',
    name="ua",
    model_dir="MPI_GE_CMIP6_allplev",
)
# %%
ua_pos_diff = ua_pos_last - ua_pos_first
# %%
ua_neg_first = read_comp_var(
    "ua",
    "neg",
    1850,
    suffix = suffix,
    time_window=(0, 20),
    method='mean',
    name="ua",
    model_dir="MPI_GE_CMIP6_allplev",
)

ua_neg_last = read_comp_var(
    "ua",
    "neg",
    2090,
    suffix = suffix,
    time_window=(0, 20),
    method='mean',
    name="ua",
    model_dir="MPI_GE_CMIP6_allplev",
)

ua_neg_diff = ua_neg_last - ua_neg_first
# %%
# zonal mean between -90, 40
def _zonal_mean(da, lon_min=-90, lon_max=40):
    """Zonal mean over [lon_min, lon_max], handling both 0-360 and -180-180 grids."""
    if da.lon.max() > 180:
        # Convert 0-360 to -180-180
        da = da.assign_coords(lon=(da.lon + 180) % 360 - 180).sortby("lon")
    return da.sel(lon=slice(lon_min, lon_max)).mean(dim="lon").sel(lat = slice(20, 90), plev = slice(100000, 25000))

#%%
ua_pos_diff_zm = _zonal_mean(ua_pos_diff)
ua_neg_diff_zm = _zonal_mean(ua_neg_diff)

# Convert plev from Pa to hPa
ua_pos_diff_zm = ua_pos_diff_zm.assign_coords(plev=ua_pos_diff_zm.plev / 100)
ua_neg_diff_zm = ua_neg_diff_zm.assign_coords(plev=ua_neg_diff_zm.plev / 100)

#%%
# Vertical profile: lat vs plev
ua_diff_diff_zm = ua_pos_diff_zm - ua_neg_diff_zm

fig, axes = plt.subplots(1, 3, figsize=(14, 3.5), sharey=True)

levels = np.arange(-2, 2.1, 0.2)
levels_diff = np.arange(-2, 2.1, 0.2)

for ax, da, title, lvls , label in zip(
    axes,
    [ua_pos_diff_zm, ua_neg_diff_zm, ua_diff_diff_zm],
    ["NAO+ (last10 - first10)", "NAO- (last10 - first10)", "NAO+ minus NAO-"],
    [levels, levels, levels_diff],
    ["a", "b", "c"],
):
    cf = ax.pcolormesh(
        da.lat, da.plev, da.values,
        cmap="RdBu_r",
        shading="nearest",
        vmin = -2.0,
        vmax = 2.0,
        snap = False,
    )
    # ax.contour(
    #     da.lat, da.plev, da.values,
    #     levels=lvls,
    #     colors="k",
    #     linewidths=0.2,
    # )
    ax.set_xlabel("Latitude (°N)")
    ax.set_ylabel("Pressure (hPa)")
    ax.set_title(title)
    ax.set_ylim(1000, 250)
    ax.yaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())

    # add panel label
    ax.text(
        -0.1,
        1.07,
        label,
        transform=ax.transAxes,
        fontsize=14,
        fontweight="bold",
        va="top",
    )

    # add vertical line at 60N
    ax.axvline(60, color="k", linestyle="dotted", linewidth=2)
axes[1].set_ylabel("")  # only show y-axis label on the first subplot
axes[2].set_ylabel("")  # hide y-axis ticks on the last subplot
plt.colorbar(cf, ax=axes, label="$\Delta$ua / $ms^{-1}$", shrink=0.8, pad=0.02)
# plt.tight_layout()
plt.savefig("/work/mh0033/m300883/High_frequecy_flow/docs/plots/0after_defense/ua_diff_vertical_profile.pdf", dpi=150, bbox_inches="tight")
plt.show()
# %%
