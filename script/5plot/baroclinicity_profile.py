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


## baroclinicity
# %%
time_window = (0, 30)
baroc_pos_first = read_comp_var(
    "eady_growth_rate",
    "pos",
    1850,
    time_window=time_window,
    method="mean",
    name="eady_growth_rate",
    model_dir="MPI_GE_CMIP6_allplev",
)
baroc_neg_first = read_comp_var(
    "eady_growth_rate",
    "neg",
    1850,
    time_window=time_window,
    method="mean",
    name="eady_growth_rate",
    model_dir="MPI_GE_CMIP6_allplev",
)
baroc_pos_last = read_comp_var(
    "eady_growth_rate",
    "pos",
    2090,
    time_window=time_window,
    method="mean",
    name="eady_growth_rate",
    model_dir="MPI_GE_CMIP6_allplev",
)
baroc_neg_last = read_comp_var(
    "eady_growth_rate",
    "neg",
    2090,
    time_window=time_window,
    method="mean",
    name="eady_growth_rate",
    model_dir="MPI_GE_CMIP6_allplev",
)


# baroclinicity from s-1 to day-1
baroc_pos_first = baroc_pos_first * 86400
baroc_neg_first = baroc_neg_first * 86400
baroc_pos_last = baroc_pos_last * 86400
baroc_neg_last = baroc_neg_last * 86400

#%%
# smooth the baroc
baroc_pos_first = map_smooth(baroc_pos_first, 5, 5)
baroc_neg_first = map_smooth(baroc_neg_first, 5, 5)
baroc_pos_last = map_smooth(baroc_pos_last, 5, 5)
baroc_neg_last = map_smooth(baroc_neg_last, 5, 5)

baroc_diff_first = baroc_pos_first - baroc_neg_first
baroc_diff_last = baroc_pos_last - baroc_neg_last

#%%
# read climatology
baroc_clim_first = read_climatology("eady_growth_rate", 1850, model_dir="MPI_GE_CMIP6_allplev")
baroc_clim_last = read_climatology("eady_growth_rate", 2090, model_dir="MPI_GE_CMIP6_allplev")
baroc_clim_first = baroc_clim_first * 86400
baroc_clim_last = baroc_clim_last * 86400

# smooth the climatology
baroc_clim_first = map_smooth(baroc_clim_first, 5, 5)
baroc_clim_last = map_smooth(baroc_clim_last, 5, 5)

# diff
baroc_clim_diff = baroc_clim_last - baroc_clim_first


#%%
# zonal average between -90, 40

def _zonal_mean(da, lon_min = -90, lon_max=40):
    """Zonal mean over [lon_min, lon_max], handling both 0-360 and -180-180 grids."""
    da = da.sel(lat = slice(0, 90))
    if da.lon.max() > 180:
        # Convert 0-360 to -180-180
        da = da.assign_coords(lon=(((da.lon + 180) % 360) - 180)).sortby("lon")
    da_subset = da.sel(lon=slice(lon_min, lon_max))
    # plev from pa to hpa
    da_subset = da_subset.assign_coords(plev=da_subset.plev / 100)
    return da_subset.mean(dim="lon")
# %%
baroc_pos_first_zonal = _zonal_mean(baroc_pos_first)
baroc_neg_first_zonal = _zonal_mean(baroc_neg_first)
baroc_pos_last_zonal = _zonal_mean(baroc_pos_last)
baroc_neg_last_zonal = _zonal_mean(baroc_neg_last)
baroc_diff_first_zonal = _zonal_mean(baroc_diff_first)
baroc_diff_last_zonal = _zonal_mean(baroc_diff_last)
baroc_clim_first_zonal = _zonal_mean(baroc_clim_first)
baroc_clim_last_zonal = _zonal_mean(baroc_clim_last)
baroc_clim_diff_zonal = _zonal_mean(baroc_clim_diff)

#%%
baroc_levels = np.arange(-10, 10.1, 1)
baroc_diff_levels = np.arange(-2, 2.1, 0.2)
baroc_diff_diff_levels = np.arange(-0.5, 0.6, 0.1)

def _plot_profile(da, ax, label=None, levels = baroc_levels, fill = True, ):
    if fill:
        return da.plot.contourf(
            x = 'lat',
            y = 'plev',
            ax = ax,
            yincrease = False,
            levels = levels,
            cmap = cmocean.cm.balance,
            add_colorbar = False,
            extend = 'both',
        )
    da.plot.contour(
        x = 'lat',
        y = 'plev',
        ax = ax,
        yincrease = False,
        # without 0
        levels = [ level for level in levels if level != 0],
        colors = 'k',
        add_colorbar = False,
        zorder = 100,
    )
    return None


fig, axes = plt.subplots(3, 3, figsize = (12, 12), sharey=True)
fig.subplots_adjust(bottom=0.20)

mappable_baroc = _plot_profile(baroc_pos_first_zonal, axes[0, 0], label="pos_1850")
_plot_profile(baroc_pos_last_zonal, axes[0, 0], label="neg_1850", fill=False)

_plot_profile(baroc_neg_first_zonal, axes[0, 1], label="pos_2090")
_plot_profile(baroc_neg_last_zonal, axes[0, 1], label="neg_2090", fill=False)

mappable_diff = _plot_profile(baroc_diff_first_zonal, axes[0, 2], label="diff_1850", levels=baroc_diff_levels)
_plot_profile(baroc_diff_last_zonal, axes[0, 2], label="diff_2090", fill=False, levels=baroc_diff_levels)

# second row for the difference between last and first
baroc_diff_first_last = baroc_pos_last_zonal - baroc_pos_first_zonal
baroc_diff_neg_first_last = baroc_neg_last_zonal - baroc_neg_first_zonal
baroc_diff_diff_first_last = baroc_diff_last_zonal - baroc_diff_first_zonal

mappable_diff_diff = _plot_profile(baroc_diff_first_last, axes[1, 0], label="diff_pos_2090-1850", levels=baroc_diff_diff_levels)
_plot_profile(baroc_diff_neg_first_last, axes[1, 1], label="diff_neg_2090-1850", levels=baroc_diff_diff_levels)
_plot_profile(baroc_diff_diff_first_last, axes[1, 2], label="diff_diff_2090-1850", levels=baroc_diff_diff_levels)


# third row for the climatology
_plot_profile(baroc_clim_first_zonal, axes[2, 0], label="clim_1850")
_plot_profile(baroc_clim_last_zonal, axes[2, 1], label="clim_2090")
_plot_profile(baroc_clim_diff_zonal, axes[2, 2], label="clim_diff_2090-1850", levels=baroc_diff_diff_levels)


for i, ax in enumerate(axes.flatten()):
    ax.set_ylim(1000, 250)
    ax.yaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax.yaxis.set_major_locator(MaxNLocator(5))
    ax.set_xlabel("Latitude")
    ax.set_ylabel("")
    # add a, b, c in the top left corner
    ax.text(0.02, 0.98, chr(97 + i), transform=ax.transAxes, fontsize=14, verticalalignment='top', fontweight='bold')
for ax in axes[:, 0]:
    ax.set_ylabel("Pressure (hPa)")

# single shared colorbar with three tick-label rows for the three level families
cbar_ax = fig.add_axes([0.20, 0.1, 0.60, 0.025])
cbar = fig.colorbar(mappable_baroc, cax=cbar_ax, orientation="horizontal")
cbar.set_label("Eady growth rate (day$^{-1}$)")

# Top ticks: baroc_levels  (panels a, b, g, h)
baroc_tick_labels = [f"{v:.0f}" for v in baroc_levels]
cbar.ax.xaxis.set_ticks_position("top")
cbar.ax.xaxis.set_label_position("top")
cbar.set_ticks(baroc_levels)
cbar.set_ticklabels(baroc_tick_labels)
cbar.ax.tick_params(axis="x", labelsize=7, pad=2)
cbar.ax.annotate(
    "a, b, g, h",
    xy=(1.05, 0.3), xycoords="axes fraction",
    xytext=(5, 0), textcoords="offset points",
    va="bottom", ha="left", fontsize=8,
)

# Bottom ticks row 1: baroc_diff_levels, mapped to the base colorbar scale [-10, 10]  (panel c)
ax_bottom_1 = cbar.ax.twiny()
ax_bottom_1.set_xlim(cbar.ax.get_xlim())
ax_bottom_1.xaxis.set_ticks_position("bottom")
ax_bottom_1.xaxis.set_label_position("bottom")
ax_bottom_1.spines["bottom"].set_position(("outward", 14))
ax_bottom_1.spines["top"].set_visible(False)
ax_bottom_1.set_xticks(baroc_diff_levels * 10)
ax_bottom_1.set_xticklabels([f"{v:.1f}" for v in baroc_diff_levels])
ax_bottom_1.tick_params(axis="x", labelsize=7, pad=1)
ax_bottom_1.annotate(
    "c",
    xy=(1.05, 0.0), xycoords="axes fraction",
    xytext=(5, -14), textcoords="offset points",
    va="center", ha="left", fontsize=8,
)

# Bottom ticks row 2: baroc_diff_diff_levels, mapped to the base colorbar scale [-10, 10]  (panels d–f, i)
ax_bottom_2 = cbar.ax.twiny()
ax_bottom_2.set_xlim(cbar.ax.get_xlim())
ax_bottom_2.xaxis.set_ticks_position("bottom")
ax_bottom_2.xaxis.set_label_position("bottom")
ax_bottom_2.spines["bottom"].set_position(("outward", 30))
ax_bottom_2.spines["top"].set_visible(False)
ax_bottom_2.set_xticks(baroc_diff_diff_levels * 20)
ax_bottom_2.set_xticklabels([f"{v:.1f}" for v in baroc_diff_diff_levels])
ax_bottom_2.tick_params(axis="x", labelsize=7, pad=1)
ax_bottom_2.annotate(
    "d–f, i",
    xy=(1.05, 0.0), xycoords="axes fraction",
    xytext=(5, -30), textcoords="offset points",
    va="center", ha="left", fontsize=8,
)

plt.savefig("/work/mh0033/m300883/High_frequecy_flow/docs/plots/0after_defense/baroclinicity_profile_full.pdf", dpi=300, bbox_inches='tight')

# # %%
# # new plot, only with above axes[0, 2] and axes[1, 2],
# fig, axes = plt.subplots(1, 2, figsize = (12, 6), sharey=True)
# _plot_profile(baroc_diff_first_zonal, axes[0], label="diff_1850", levels=baroc_diff_levels)
# _plot_profile(baroc_diff_last_zonal, axes[0], label="diff_2090", fill=False, levels=baroc_diff_levels)
# _plot_profile(baroc_diff_diff_first_last, axes[1], label="diff_diff_2090-1850", levels=baroc_diff_diff_levels)
# for i, ax in enumerate(axes.flatten()):
#     ax.set_ylim(1000, 250)
#     ax.set_xlim(20, 90)
#     ax.yaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
#     ax.yaxis.set_major_locator(MaxNLocator(5))
#     ax.set_xlabel("Latitude")
#     ax.set_ylabel("")
#     # add a, b in the top left corner
#     ax.text(0.02, 0.98, chr(97 + i), transform=ax.transAxes, fontsize=14, verticalalignment='top', fontweight='bold')
# axes[0].set_title("NAO pos - neg")
# axes[1].set_title("(NAO pos - neg) 2090 - (NAO pos - neg) 1850")
# axes[0].legend(loc='lower left')

# plt.savefig("/work/mh0033/m300883/High_frequecy_flow/docs/plots/0after_defense/baroclinicity_profile.pdf", dpi=300, bbox_inches='tight')
# # %%

# %%
