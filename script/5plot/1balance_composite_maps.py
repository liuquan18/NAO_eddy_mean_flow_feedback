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


## wave breaking
#%%
awb_pos_first = read_comp_var(
    "wb_anticyclonic_allisen",
    "pos",
    1850,
    time_window=(-5, 5), # also precusors
    name="smooth_pv",
    model_dir = 'MPI_GE_CMIP6_allplev',
    method = 'sum'
)

awb_neg_first = read_comp_var(
    "wb_anticyclonic_allisen",
    "neg",
    1850,
    time_window=(-5, 5), # also precusors
    name="smooth_pv",
    model_dir = 'MPI_GE_CMIP6_allplev',
    method = 'sum'
)

awb_pos_last = read_comp_var(
    "wb_anticyclonic_allisen",
    "pos",
    2090,
    time_window=(-5, 5), # also precusors
    name="smooth_pv",
    model_dir = 'MPI_GE_CMIP6_allplev',
    method = 'sum'
)
awb_neg_last = read_comp_var(
    "wb_anticyclonic_allisen",
    "neg",
    2090,
    time_window=(-5, 5), # also precusors  
    name="smooth_pv",
    model_dir = 'MPI_GE_CMIP6_allplev',
    method = 'sum'
)
#%%
cwb_pos_first = read_comp_var(
    "wb_cyclonic_allisen",
    "pos",
    1850,
    time_window=(-5, 5), # also precusors
    name="smooth_pv",
    model_dir = 'MPI_GE_CMIP6_allplev',
    method = 'sum'
)
cwb_neg_first = read_comp_var(
    "wb_cyclonic_allisen",
    "neg",
    1850,
    time_window=(-5, 5), # also precusors
    name="smooth_pv",
    model_dir = 'MPI_GE_CMIP6_allplev',
    method = 'sum'
)
cwb_pos_last = read_comp_var(
    "wb_cyclonic_allisen",
    "pos",
    2090,
    time_window=(-5, 5), # also precusors
    name="smooth_pv",
    model_dir = 'MPI_GE_CMIP6_allplev',
    method = 'sum'
)
cwb_neg_last = read_comp_var(
    "wb_cyclonic_allisen",
    "neg",
    2090,
    time_window=(-5, 5), # also precusors
    name="smooth_pv",
    model_dir = 'MPI_GE_CMIP6_allplev',
    method = 'sum'
)

## eke
#%%
eke_pos_first = read_comp_var(
    "eke",
    "pos",
    1850,
    time_window=(-5, 5), # also precusors
    name="eke",
    model_dir = 'MPI_GE_CMIP6_allplev'
)

eke_neg_first = read_comp_var(
    "eke",
    "neg",
    1850,
    time_window=(-5, 5), # also precusors
    name="eke",
    model_dir = 'MPI_GE_CMIP6_allplev'
)
eke_pos_last = read_comp_var(
    "eke",
    "pos",
    2090,
    time_window=(-5, 5), # also precusors
    name="eke",
    model_dir = 'MPI_GE_CMIP6_allplev'
)
eke_neg_last = read_comp_var(
    "eke",
    "neg",
    2090,
    time_window=(-5, 5), # also precusors
    name="eke",
    model_dir = 'MPI_GE_CMIP6_allplev'
)
# Jet stream
#%%

ua_pos_first = read_comp_var(
    "ua",
    "pos",
    1850,
    time_window=((-5, 5)),
    method="mean",
    name="ua",
    model_dir="MPI_GE_CMIP6_allplev",
)
ua_neg_first = read_comp_var(
    "ua",
    "neg",
    1850,
    time_window=((-5, 5)),
    method="mean",
    name="ua",
    model_dir="MPI_GE_CMIP6_allplev",
)

ua_pos_last = read_comp_var(
    "ua",
    "pos",
    2090,
    time_window=((-5, 5)),
    method="mean",
    name="ua",
    model_dir="MPI_GE_CMIP6_allplev",
)
ua_neg_last = read_comp_var(
    "ua",
    "neg",
    2090,
    time_window=((-5, 5)),
    method="mean",
    name="ua",
    model_dir="MPI_GE_CMIP6_allplev",
)

## baroclinicity
# %%
baroc_pos_first = read_comp_var(
    "eady_growth_rate",
    "pos",
    1850,
    time_window=((-5, 5)),
    method="mean",
    name="eady_growth_rate",
    model_dir="MPI_GE_CMIP6_allplev",
)
baroc_neg_first = read_comp_var(
    "eady_growth_rate",
    "neg",
    1850,
    time_window=((-5, 5)),
    method="mean",
    name="eady_growth_rate",
    model_dir="MPI_GE_CMIP6_allplev",
)
baroc_pos_last = read_comp_var(
    "eady_growth_rate",
    "pos",
    2090,
    time_window=((-5, 5)),
    method="mean",
    name="eady_growth_rate",
    model_dir="MPI_GE_CMIP6_allplev",
)
baroc_neg_last = read_comp_var(
    "eady_growth_rate",
    "neg",
    2090,
    time_window=((-5, 5)),
    method="mean",
    name="eady_growth_rate",
    model_dir="MPI_GE_CMIP6_allplev",
)


## steady eddies/ blocking
# %%
steady_pos_first = read_comp_var(
    "zg_steady",
    "pos",
    1850,
    time_window=(0, 10),
    name="zg",
    model_dir = 'MPI_GE_CMIP6_allplev'
)

steady_neg_first = read_comp_var(
    "zg_steady",
    "neg",
    1850,
    time_window=(0, 10),
    name="zg",
    model_dir = 'MPI_GE_CMIP6_allplev'
)

steady_pos_last = read_comp_var(
    "zg_steady",
    "pos",
    2090,
    time_window=(0, 10),
    name="zg",
    model_dir = 'MPI_GE_CMIP6_allplev'
)

steady_neg_last = read_comp_var(
    "zg_steady",
    "neg",
    2090,
    time_window=(0, 10),
    name="zg",
    model_dir = 'MPI_GE_CMIP6_allplev'
)
## pre-processing
# %%
# wb isentropic sum
awb_pos_first = awb_pos_first.sum(dim="isen_level", skipna=True)
awb_neg_first = awb_neg_first.sum(dim="isen_level", skipna=True)
awb_pos_last = awb_pos_last.sum(dim="isen_level", skipna=True)
awb_neg_last = awb_neg_last.sum(dim="isen_level", skipna=True)

cwb_pos_first = cwb_pos_first.sum(dim="isen_level", skipna=True)
cwb_neg_first = cwb_neg_first.sum(dim="isen_level", skipna=True)
cwb_pos_last = cwb_pos_last.sum(dim="isen_level", skipna=True)
cwb_neg_last = cwb_neg_last.sum(dim="isen_level", skipna=True)

#%%
awb_pos_first = awb_pos_first/10 # to make the result as summed only over events (excluding sum over time, which is 10 days)
awb_neg_first = awb_neg_first/10
awb_pos_last = awb_pos_last/10
awb_neg_last = awb_neg_last/10

cwb_pos_first = cwb_pos_first/10
cwb_neg_first = cwb_neg_first/10
cwb_pos_last = cwb_pos_last/10
cwb_neg_last = cwb_neg_last/10
# diff between pos and neg
awb_diff_first = awb_pos_first - awb_neg_first
awb_diff_last = awb_pos_last - awb_neg_last

cwb_diff_first = cwb_pos_first - cwb_neg_first
cwb_diff_last = cwb_pos_last - cwb_neg_last
#%%
awb_pos_first = util.lon360to180(awb_pos_first)
awb_neg_first = util.lon360to180(awb_neg_first)
awb_diff_first = util.lon360to180(awb_diff_first)

awb_pos_last = util.lon360to180(awb_pos_last)
awb_neg_last = util.lon360to180(awb_neg_last)
awb_diff_last = util.lon360to180(awb_diff_last)
#%%
cwb_pos_first  = util.lon360to180(cwb_pos_first)
cwb_neg_first  = util.lon360to180(cwb_neg_first)
cwb_diff_first = util.lon360to180(cwb_diff_first)

cwb_pos_last  = util.lon360to180(cwb_pos_last)
cwb_neg_last  = util.lon360to180(cwb_neg_last)
cwb_diff_last = util.lon360to180(cwb_diff_last)
#%%
eke_diff_first = eke_pos_first - eke_neg_first
eke_diff_last = eke_pos_last - eke_neg_last

#%%
#%%
# ua select 250 hpa
ua_pos_first = ua_pos_first.sel(plev=25000)
ua_neg_first = ua_neg_first.sel(plev=25000)
ua_pos_last = ua_pos_last.sel(plev=25000)
ua_neg_last = ua_neg_last.sel(plev=25000)

# baroclinicity from s-1 to day-1
baroc_pos_first = baroc_pos_first * 86400
baroc_neg_first = baroc_neg_first * 86400
baroc_pos_last = baroc_pos_last * 86400
baroc_neg_last = baroc_neg_last * 86400

# # baroc select 85000
# baroc_pos_first = baroc_pos_first.sel(plev=85000)
# baroc_neg_first = baroc_neg_first.sel(plev=85000)
# baroc_pos_last = baroc_pos_last.sel(plev=85000)
# baroc_neg_last = baroc_neg_last.sel(plev=85000)

# smooth the baroc
baroc_pos_first = map_smooth(baroc_pos_first, 5, 5)
baroc_neg_first = map_smooth(baroc_neg_first, 5, 5)
baroc_pos_last = map_smooth(baroc_pos_last, 5, 5)
baroc_neg_last = map_smooth(baroc_neg_last, 5, 5)

ua_diff_first = ua_pos_first - ua_neg_first
ua_diff_last = ua_pos_last - ua_neg_last
baroc_diff_first = baroc_pos_first - baroc_neg_first
baroc_diff_last = baroc_pos_last - baroc_neg_last
#%%
awb_levels = np.arange(-50, 51, 20)
awb_diff_levels = np.arange(-25, 26, 10)

cwb_levels = np.arange(-20, 21, 8)
cwb_diff_levels = np.arange(-10, 11, 4)

eke_levels = np.arange(-40, 41, 8)
eke_diff_levels = np.arange(-20, 21, 4)

ua_levels = np.arange(-30, 31, 10)
ua_diff_levels = np.arange(-15, 16, 5)

baroc_levels = np.arange(-8, 8.1, 2)
baroc_diff_levels = np.arange(-4, 4.1, 1)
#%%
fig, axes = plt.subplots(
    nrows=5,
    ncols=3,
    figsize=(8., 15),
    subplot_kw={"projection": ccrs.Orthographic(-30, 70)},
    constrained_layout=False,
)
fig.subplots_adjust(left=0.04, right=0.88, top=0.94, bottom=0.14, wspace=0.02, hspace=0.16)

# first row ua, pos, neg, diff
ua_pos_cf = ua_pos_first.plot.contourf(
    ax=axes[0, 0],
    levels=ua_levels,
    cmap="RdBu_r",
    add_colorbar=False,
    transform=ccrs.PlateCarree(),
    extend = 'both',
    alpha = 0.8,
)
ua_neg_first.plot.contourf(
    ax=axes[0, 1],
    levels=ua_levels,
    cmap="RdBu_r",
    add_colorbar=False,
    transform=ccrs.PlateCarree(),
    extend = 'both',
    alpha = 0.8,
)
ua_diff_first.plot.contourf(
    ax=axes[0, 2],
    levels=ua_diff_levels,
    cmap="RdBu_r",
    add_colorbar=False,
    transform=ccrs.PlateCarree(),
    extend = 'both',
    alpha = 0.8,
)
ua_pos_last.plot.contour(
    ax=axes[0, 0],
    levels=[level for level in ua_levels if level != 0],
    colors="k",
    add_colorbar=False,
    transform=ccrs.PlateCarree(),
    linewidths=0.6,
)
ua_neg_last.plot.contour(
    ax=axes[0, 1],
    levels=[level for level in ua_levels if level != 0],
    colors="k",
    add_colorbar=False,
    transform=ccrs.PlateCarree(),
    linewidths=0.6,
)
ua_diff_last.plot.contour(
    ax=axes[0, 2],
    levels=[level for level in ua_diff_levels if level != 0],
    colors="k",
    add_colorbar=False,
    transform=ccrs.PlateCarree(),
    linewidths=0.6,
)

# second row cwb, pos, neg, diff
cwb_pos_cf = cwb_pos_first.plot.contourf(
    ax=axes[1, 0],
    levels=cwb_levels,
    cmap="RdBu_r",
    add_colorbar=False,
    transform=ccrs.PlateCarree(),
    extend = 'both',
    alpha = 0.8,
)
cwb_neg_first.plot.contourf(
    ax=axes[1, 1],
    levels=cwb_levels,
    cmap="RdBu_r",
    add_colorbar=False,
    transform=ccrs.PlateCarree(),
    extend = 'both',
    alpha = 0.8,
)

cwb_diff_first.plot.contourf(
    ax=axes[1, 2],
    levels=cwb_diff_levels,
    cmap="RdBu_r",
    add_colorbar=False,
    transform=ccrs.PlateCarree(),
    extend = 'both',
    alpha = 0.8,
)

cwb_pos_last.plot.contour(
    ax=axes[1, 0],
    levels=[level for level in cwb_levels if level != 0],
    colors="k",
    add_colorbar=False,
    transform=ccrs.PlateCarree(),
    linewidths=0.6,
)
cwb_neg_last.plot.contour(
    ax=axes[1, 1],
    levels=[level for level in cwb_levels if level != 0],
    colors="k",
    add_colorbar=False,
    transform=ccrs.PlateCarree(),
    linewidths=0.6,
)
cwb_diff_last.plot.contour(
    ax=axes[1, 2],
    levels=[level for level in cwb_diff_levels if level != 0],
    colors="k",
    add_colorbar=False,
    transform=ccrs.PlateCarree(),
    linewidths=0.6,
)

# third row awb, pos, neg, diff
awb_pos_cf = awb_pos_first.plot.contourf(
    ax=axes[2, 0],
    levels=awb_levels,
    cmap="RdBu_r",
    add_colorbar=False,
    transform=ccrs.PlateCarree(),
    extend = 'both',
    alpha = 0.8,
)
awb_neg_first.plot.contourf(
    ax=axes[2, 1],
    levels=awb_levels,
    cmap="RdBu_r",
    add_colorbar=False,
    transform=ccrs.PlateCarree(),
    extend = 'both',
    alpha = 0.8,
)
awb_diff_first.plot.contourf(
    ax=axes[2, 2],
    levels=awb_diff_levels,
    cmap="RdBu_r",
    add_colorbar=False,
    transform=ccrs.PlateCarree(),
    extend = 'both',
    alpha = 0.8,
)
awb_pos_last.plot.contour(
    ax=axes[2, 0],
    levels=[level for level in awb_levels if level != 0],
    colors="k",
    add_colorbar=False,
    transform=ccrs.PlateCarree(),
    linewidths=0.6,
)
awb_neg_last.plot.contour(
    ax=axes[2, 1],
    levels=[level for level in awb_levels if level != 0],
    colors="k",
    add_colorbar=False,
    transform=ccrs.PlateCarree(),
    linewidths=0.6,
)
awb_diff_last.plot.contour(
    ax=axes[2, 2],
    levels=[level for level in awb_diff_levels if level != 0],
    colors="k",
    add_colorbar=False,
    transform=ccrs.PlateCarree(),
    linewidths=0.6,
)

# fourth row eke, pos, neg, diff
eke_pos_cf = eke_pos_first.plot.contourf(
    ax=axes[3, 0],
    levels=eke_levels,
    cmap="RdBu_r",
    add_colorbar=False,
    transform=ccrs.PlateCarree(),
    extend = 'both',
    alpha = 0.8,
)
eke_neg_first.plot.contourf(
    ax=axes[3, 1],
    levels=eke_levels,
    cmap="RdBu_r",
    add_colorbar=False,
    transform=ccrs.PlateCarree(),
    extend = 'both',
    alpha = 0.8,
)
eke_diff_first.plot.contourf(
    ax=axes[3, 2],
    levels=eke_diff_levels,
    cmap="RdBu_r",
    add_colorbar=False,
    transform=ccrs.PlateCarree(),
    extend = 'both',
    alpha = 0.8,
)
eke_pos_last.plot.contour(
    ax=axes[3, 0],
    levels=[level for level in eke_levels if level != 0],
    colors="k",
    add_colorbar=False,
    transform=ccrs.PlateCarree(),
    linewidths=0.6,
)
eke_neg_last.plot.contour(
    ax=axes[3, 1],
    levels=[level for level in eke_levels if level != 0],
    colors="k",
    add_colorbar=False,
    transform=ccrs.PlateCarree(),
    linewidths=0.6,
)
eke_diff_last.plot.contour(
    ax=axes[3, 2],
    levels=[level for level in eke_diff_levels if level != 0],
    colors="k",
    add_colorbar=False,
    transform=ccrs.PlateCarree(),
    linewidths=0.6,
)

# fifth row baroc, pos, neg, diff
baroc_pos_cf = baroc_pos_first.plot.contourf(
    ax=axes[4, 0],
    levels=baroc_levels,
    cmap="RdBu_r",
    add_colorbar=False,
    transform=ccrs.PlateCarree(),
    extend = 'both',
    alpha = 0.8,
)
baroc_neg_first.plot.contourf(
    ax=axes[4, 1],
    levels=baroc_levels,
    cmap="RdBu_r",
    add_colorbar=False,
    transform=ccrs.PlateCarree(),
    extend = 'both',
    alpha = 0.8,
)
baroc_diff_first.plot.contourf(
    ax=axes[4, 2],
    levels=baroc_diff_levels,
    cmap="RdBu_r",
    add_colorbar=False,
    transform=ccrs.PlateCarree(),
    extend = 'both',
    alpha = 0.8,
)
baroc_pos_last.plot.contour(
    ax=axes[4, 0],
    levels=[level for level in baroc_levels if level != 0],
    colors="k",
    add_colorbar=False,
    transform=ccrs.PlateCarree(),
    linewidths=0.6, 
)
baroc_neg_last.plot.contour(
    ax=axes[4, 1],
    levels=[level for level in baroc_levels if level != 0],
    colors="k",
    add_colorbar=False,
    transform=ccrs.PlateCarree(),
    linewidths=0.6,
)
baroc_diff_last.plot.contour(
    ax=axes[4, 2],
    levels=[level for level in baroc_diff_levels if level != 0],
    colors="k",
    add_colorbar=False,
    transform=ccrs.PlateCarree(),
    linewidths=0.6,
)



# --- Formatting ---
for i, ax in enumerate(axes.flatten()):
    ax.coastlines(color="grey", linewidth=1)
    ax.gridlines(draw_labels=False, linewidth=1, color="grey", alpha=0.5, linestyle="--")
    ax.set_global()
    ax.set_title("")
    # add a, b, c, d,...
    ax.text(0.02, 0.98, chr(97 + i), transform=ax.transAxes,
            fontsize=10, fontweight='bold', va='top', ha='left')
    


# --- Colorbars ---
rows_config = [
    (ua_pos_cf,    ua_levels,    ua_diff_levels,    "ua / m s$^{-1}$",          'both'),
    (cwb_pos_cf,   cwb_levels,   cwb_diff_levels,   "CWB / day",  'both'),
    (awb_pos_cf,   awb_levels,   awb_diff_levels,   "AWB / day",  'both'),
    (eke_pos_cf,   eke_levels,   eke_diff_levels,   "EKE / m$^2$ s$^{-2}$",    'both'),
    (baroc_pos_cf, baroc_levels, baroc_diff_levels, "$\\sigma_E$ / day$^{-1}$",        'both'),
]

def _cbar_fwd(pmin, pmax, dmin, dmax):
    return lambda x: dmin + (x - pmin) * (dmax - dmin) / (pmax - pmin)

def _cbar_inv(pmin, pmax, dmin, dmax):
    return lambda x: pmin + (x - dmin) * (pmax - pmin) / (dmax - dmin)

for row_idx, (pos_cf, pos_levels, diff_levels, title, ext) in enumerate(rows_config):
    bbox = axes[row_idx, 2].get_position()
    cax = fig.add_axes([bbox.x1 + 0.04, bbox.y0, 0.018, bbox.height - 0.02])  # [left, bottom, width, height]
    cb = fig.colorbar(pos_cf, cax=cax, orientation='vertical', extend=ext)
    cb.ax.yaxis.set_ticks_position('left')
    cb.ax.yaxis.set_label_position('left')
    cb.set_ticks(pos_levels)
    cb.ax.tick_params(labelsize=7)

    pos_min_val  = float(pos_levels[0])
    pos_max_val  = float(pos_levels[-1])
    diff_min_val = float(diff_levels[0])
    diff_max_val = float(diff_levels[-1])

    ax_sec = cax.secondary_yaxis(
        'right',
        functions=(_cbar_fwd(pos_min_val, pos_max_val, diff_min_val, diff_max_val),
                   _cbar_inv(pos_min_val, pos_max_val, diff_min_val, diff_max_val)),
    )
    ax_sec.set_yticks(diff_levels)
    ax_sec.tick_params(labelsize=7)
    cb.ax.set_title(title, fontsize=7, pad=4)

plt.savefig("/work/mh0033/m300883/High_frequecy_flow/docs/plots/0after_defense/balance_composite.pdf", dpi=300, bbox_inches="tight",)


# %%
