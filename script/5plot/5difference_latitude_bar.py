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

from scipy import stats
from src.plotting.util import map_smooth
import src.plotting.util as util

importlib.reload(read_composite)

read_EP_flux = read_composite.read_EP_flux
read_E_div = read_composite.read_E_div
read_comp_var = read_composite.read_comp_var


# %%
MODEL_DIR = "MPI_GE_CMIP6_allplev"


def _read_all(var_name, suffix = '_ano', name=None, method="no_stat", chunks=None):
    """Read pos/neg x 1850/2090 composites.

    Returns a dict keyed by '{phase}_{decade}', e.g. 'pos_1850'.
    """
    kwargs = dict(time_window= 'all', model_dir=MODEL_DIR)
    if method is not None:
        kwargs["method"] = method
    if name is not None:
        kwargs["name"] = name
    if chunks is not None:
        kwargs["chunks"] = chunks
    return {
        f"{phase}_{decade}": read_comp_var(var_name, phase, decade, suffix=suffix, **kwargs)
        for phase in ("pos", "neg")
        for decade in (1850, 2090)
    }

def _zonal_mean(da, lon_min=-90, lon_max=40, time_window = (-5, 20)):
    """Zonal mean over [lon_min, lon_max], handling both 0-360 and -180-180 grids."""
    if da.lon.max() > 180:
        # Convert 0-360 to -180-180
        da = da.assign_coords(lon=(da.lon + 180) % 360 - 180).sortby("lon")
    return da.sel(lon=slice(lon_min, lon_max), lat = slice(20, 90), time=slice(*time_window)).mean(dim=("lon", "time"))

#%%
# Convergence of transient eddy momentum flux
Fdiv_phi_transient = _read_all("Fdiv_phi_transient", suffix="_ano", name="div")
#%%
Fdiv_p_transient = _read_all("Fdiv_p_transient", suffix="_ano", name="div2")
# %%
eke = _read_all("eke", suffix="_ano", name="eke")

#%%
ua = _read_all("ua", suffix="", name="ua", method="no_stat")

# %%
Fdiv_phi_diff_pos = Fdiv_phi_transient["pos_2090"] - Fdiv_phi_transient["pos_1850"]
Fdiv_phi_diff_neg = Fdiv_phi_transient["neg_2090"] - Fdiv_phi_transient["neg_1850"]
Fdiv_p_diff_pos = Fdiv_p_transient["pos_2090"] - Fdiv_p_transient["pos_1850"]
Fdiv_p_diff_neg = Fdiv_p_transient["neg_2090"] - Fdiv_p_transient["neg_1850"]
eke_diff_pos = eke["pos_2090"] - eke["pos_1850"]
eke_diff_neg = eke["neg_2090"] - eke["neg_1850"]
#%%
Fdiv_phi_diff_pos_zm = _zonal_mean(Fdiv_phi_diff_pos)
Fdiv_phi_diff_neg_zm = _zonal_mean(Fdiv_phi_diff_neg)
Fdiv_p_diff_pos_zm = _zonal_mean(Fdiv_p_diff_pos)
Fdiv_p_diff_neg_zm = _zonal_mean(Fdiv_p_diff_neg)
eke_diff_pos_zm = _zonal_mean(eke_diff_pos)
eke_diff_neg_zm = _zonal_mean(eke_diff_neg)
#%%
EPdiv_diff_pos_zm = Fdiv_phi_diff_pos_zm - Fdiv_p_diff_pos_zm
EPdiv_diff_neg_zm = Fdiv_phi_diff_neg_zm - Fdiv_p_diff_neg_zm
# %%
ua_diff_pos = ua["pos_2090"] - ua["pos_1850"]
ua_diff_neg = ua["neg_2090"] - ua["neg_1850"]
ua_diff_pos_zm = _zonal_mean(ua_diff_pos)
ua_diff_neg_zm = _zonal_mean(ua_diff_neg)

#%%
ua_diff_pos_zm = ua_diff_pos_zm.assign_coords(plev=ua_diff_pos_zm.plev / 100)
ua_diff_neg_zm = ua_diff_neg_zm.assign_coords(plev=ua_diff_neg_zm.plev / 100)


#%%
COLOR_POS = "#E57200"  # MPI orange
COLOR_NEG = "#006C66"  # MPI green


def _lat_mean_and_sig(da):
    """Return (mean_lat, sig_mask) where sig_mask is True where the
    one-sided t-test against zero (in direction of the mean) is p < 0.05.
    Averages all non-(lat, event) dims first, then tests across event.
    """
    reduce_dims = [d for d in da.dims if d not in ("lat", "event")]
    if reduce_dims:
        da = da.mean(dim=reduce_dims)
    da = da.sortby("lat")
    mean_lat = da.mean(dim="event")
    # one-sample t-test against 0 across events, per latitude
    t_vals, p_two = stats.ttest_1samp(da.values, 0, axis=da.dims.index("event"))
    sig = (p_two / 2) < 0.05  # one-sided p in the direction of the observed mean
    return mean_lat, sig


def _plot_sig_bars(ax, da_zm, color, label, ylabel="Value", ylim=None, show_xlabel=True):
    """Bar chart with filled bars where one-sided significant, outline only otherwise."""
    mean_lat, sig = _lat_mean_and_sig(da_zm)
    lats = mean_lat.lat.values
    vals = mean_lat.values
    for lat, val, significant in zip(lats, vals, sig):
        ax.bar(
            lat, val, width=1.0,
            color=color if significant else "none",
            edgecolor=color, linewidth=0.8,
        )
    ax.axhline(0, color="k", lw=0.5)
    ax.text(0.02, 0.97, label, transform=ax.transAxes,
            fontsize=12, fontweight="bold", va="top", ha="left")
    ax.set_ylabel(ylabel)
    if ylim is not None:
        ax.set_ylim(ylim)
    ax.set_xticks([30, 50, 70])
    if show_xlabel:
        ax.set_xlabel("Latitude")
        ax.set_xticklabels(["30°N", "50°N", "70°N"])
    else:
        ax.set_xticklabels([])
    ax.spines[["top", "right"]].set_visible(False)


def _plot_profile(ax, da_zm, label, vmin=-2, vmax=2, show_xlabel=True, cmap="RdBu_r"):
    """Pcolormesh lat-plev vertical profile with significance dots."""
    # Select plev range 250-1000 hPa and sort lat
    da_zm = da_zm.sortby("plev").sel(plev=slice(250, 1000)).sortby("lat")

    event_axis = da_zm.dims.index("event")
    mean_da = da_zm.mean(dim="event")
    _, p_two = stats.ttest_1samp(da_zm.values, 0, axis=event_axis)
    sig = (p_two / 2) < 0.05  # one-sided, direction of mean

    lats = mean_da.lat.values
    plevs = mean_da.plev.values

    cf = ax.contourf(
        lats, plevs, mean_da.values,
        cmap=cmap, shading="nearest",
        # vmin=vmin, vmax=vmax,
        levels = np.arange(-2.4, 2.5, 0.4),
        extend = 'both',
    )

    cl = ax.contour(
        lats, plevs, mean_da.values,
        colors = 'k', linewidths=0.5,
        alpha = 0.7,
        # vmin=vmin, vmax=vmax,
        levels = np.arange(-2.4, 2.5, 0.4),
        extend = 'both',
    )

    # Overlay dots where significant
    lat_grid, plev_grid = np.meshgrid(lats, plevs)
    ax.scatter(
        lat_grid[sig], plev_grid[sig],
        s=25, color="k", marker=".", linewidths=0, zorder=5,
    )

    ax.set_ylim(1020, 250)
    ax.yaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax.set_ylabel(r"Pressure / hPa")
    ax.set_xticks([30, 50, 70])
    if show_xlabel:
        ax.set_xlabel("Latitude")
        ax.set_xticklabels(["30°N", "50°N", "70°N"])
    else:
        ax.set_xticklabels([])
    ax.text(0.02, 0.97, label, transform=ax.transAxes,
            fontsize=12, fontweight="bold", va="top", ha="left")
    ax.spines[["top", "right"]].set_visible(False)
    return cf

#%%
fig, axes = plt.subplots(3, 2, figsize=(8, 7), gridspec_kw={"height_ratios": [0.8, 0.8, 0.8]})

YLABEL_FDIV  = r"$-\frac{\partial}{\partial y} (\overline{u'v'})$ / m s$^{-1}$ day$^{-1}$"
YLABEL_EPDIV = r"$\nabla \cdot F$ / m s$^{-1}$ day$^{-1}$"
YLABEL_EKE   = r"EKE / m$^2$ s$^{-2}$"


# Row 0: Fdiv_phi
_plot_sig_bars(axes[0, 0], Fdiv_phi_diff_pos_zm, COLOR_POS, "a", ylabel=YLABEL_FDIV,  ylim=(-1, 1), show_xlabel=False)
_plot_sig_bars(axes[0, 1], Fdiv_phi_diff_neg_zm, COLOR_NEG, "b", ylabel=YLABEL_FDIV,  ylim=(-1, 1), show_xlabel=False)
# Row 1: EPdiv
_plot_sig_bars(axes[1, 0], EPdiv_diff_pos_zm,    COLOR_POS, "c", ylabel=YLABEL_EPDIV, ylim=(-1, 1), show_xlabel=False)
_plot_sig_bars(axes[1, 1], EPdiv_diff_neg_zm,    COLOR_NEG, "d", ylabel=YLABEL_EPDIV, ylim=(-1, 1), show_xlabel=False)
# Row 2: EKE
_plot_sig_bars(axes[2, 0], eke_diff_pos_zm,      COLOR_POS, "e", ylabel=YLABEL_EKE,   ylim=(-3, 3), show_xlabel=True)
_plot_sig_bars(axes[2, 1], eke_diff_neg_zm,      COLOR_NEG, "f", ylabel=YLABEL_EKE,   ylim=(-3, 3), show_xlabel=True)

plt.tight_layout()

plt.savefig("/work/mh0033/m300883/High_frequecy_flow/docs/plots/0after_defense/difference_latitude.pdf", dpi=300, bbox_inches="tight", transparent=True)

#%%
# ===== Separate ua vertical profile figure =====
fig_ua, axes_ua = plt.subplots(1, 2, figsize=(8, 3.5))
cf_pos = _plot_profile(axes_ua[0], ua_diff_pos_zm, "a", vmin=-2, vmax=2)
cf_neg = _plot_profile(axes_ua[1], ua_diff_neg_zm, "b", vmin=-2, vmax=2)
axes_ua[1].set_ylabel("")
plt.tight_layout()
cbar_ax_ua = fig_ua.add_axes([0.25, -0.06, 0.5, 0.04])
fig_ua.colorbar(cf_neg, cax=cbar_ax_ua, orientation="horizontal", label=r"$\Delta$ua / m s$^{-1}$")
plt.savefig("/work/mh0033/m300883/High_frequecy_flow/docs/plots/0after_defense/ua_diff_vertical_profile.pdf", dpi=300, bbox_inches="tight", transparent=True)

# %%
