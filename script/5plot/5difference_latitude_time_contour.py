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

def _zonal_mean(da, lon_min=-90, lon_max=40):
    """Zonal mean over [lon_min, lon_max], handling both 0-360 and -180-180 grids."""
    if da.lon.max() > 180:
        # Convert 0-360 to -180-180
        da = da.assign_coords(lon=(da.lon + 180) % 360 - 180).sortby("lon")
    return da.sel(lon=slice(lon_min, lon_max), lat = slice(20, 90)).mean(dim="lon")

#%%
# Convergence of transient eddy momentum flux
Fdiv_phi_transient = _read_all("Fdiv_phi_transient", suffix="_ano", name="div")
#%%
Fdiv_p_transient = _read_all("Fdiv_p_transient", suffix="_ano", name="div2")
# %%
eke = _read_all("eke", suffix="_ano", name="eke")

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
#%%

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


def _plot_contour_time(ax, da_zm, label, levels, cmap="RdBu_r", show_ylabel=True):
    """Contourf of lat (y) vs lag/time (x) with significance dots."""
    reduce_dims = [d for d in da_zm.dims if d not in ("lat", "event", "time")]
    if reduce_dims:
        da_zm = da_zm.mean(dim=reduce_dims)
    da_zm = da_zm.sortby("lat").transpose("event", "time", "lat")

    mean_da = da_zm.mean(dim="event")  # (time, lat)
    _, p_two = stats.ttest_1samp(da_zm.values, 0, axis=0)
    sig = (p_two / 2) < 0.05  # (time, lat)

    lats = mean_da.lat.values
    times = mean_da.time.values

    # Swap: times on x-axis, lats on y-axis → data shape (n_lat, n_time)
    cf = ax.contourf(times, lats, mean_da.values.T, levels=levels, cmap=cmap, extend="both")
    ax.contour(times, lats, mean_da.values.T, levels=levels, colors="k", linewidths=0.3, alpha=0.5)

    time_2d, lat_2d = np.meshgrid(times, lats)
    ax.scatter(time_2d[sig.T], lat_2d[sig.T], s=3, color="k", marker=".", linewidths=0, zorder=5)

    ax.axvline(0, color="k", lw=0.8, ls="--")
    ax.set_xlabel("days relative to onset")
    ax.set_yticks([30, 50, 70])
    ax.set_xlim(-10, 20)
    ax.set_ylim(20, 80)
    if show_ylabel:
        ax.set_ylabel("Latitude")
        ax.set_yticklabels(["30°N", "50°N", "70°N"])
    else:
        ax.set_yticklabels([])
    ax.text(0.02, 0.97, label, transform=ax.transAxes,
            fontsize=12, fontweight="bold", va="top", ha="left",
            bbox=dict(facecolor="white", alpha=0.6, edgecolor="none"))
    ax.spines[["top", "right"]].set_visible(False)
    return cf


#%%
LEVELS_FDIV  = np.arange(-1.0, 1.05, 0.2)
LEVELS_EPDIV = np.arange(-1.0, 1.05, 0.2)
LEVELS_EKE   = np.arange(-3.5, 3.6, 0.5)

CLABEL_FDIV  = r"$-\frac{\partial}{\partial y} (\overline{u'v'})$ / m s$^{-1}$ day$^{-1}$"
CLABEL_EPDIV = r"$\nabla \cdot F$ / m s$^{-1}$ day$^{-1}$"
CLABEL_EKE   = r"EKE / m$^2$ s$^{-2}$"

fig = plt.figure(figsize=(9, 9))
gs = fig.add_gridspec(3, 3, width_ratios=[1, 1, 0.05], wspace=0.1, hspace=0.3)
axes = np.array([[fig.add_subplot(gs[i, j]) for j in range(2)] for i in range(3)])
caxes = [fig.add_subplot(gs[i, 2]) for i in range(3)]

# Row 0: Fdiv_phi
cf0 = _plot_contour_time(axes[0, 0], Fdiv_phi_diff_pos_zm, "a", LEVELS_FDIV)
_plot_contour_time(axes[0, 1], Fdiv_phi_diff_neg_zm, "b", LEVELS_FDIV, show_ylabel=False)
fig.colorbar(cf0, cax=caxes[0], label=CLABEL_FDIV)
# Row 1: EPdiv
cf1 = _plot_contour_time(axes[1, 0], EPdiv_diff_pos_zm, "c", LEVELS_EPDIV)
_plot_contour_time(axes[1, 1], EPdiv_diff_neg_zm, "d", LEVELS_EPDIV, show_ylabel=False)
fig.colorbar(cf1, cax=caxes[1], label=CLABEL_EPDIV)
# Row 2: EKE
cf2 = _plot_contour_time(axes[2, 0], eke_diff_pos_zm, "e", LEVELS_EKE)
_plot_contour_time(axes[2, 1], eke_diff_neg_zm, "f", LEVELS_EKE, show_ylabel=False)
fig.colorbar(cf2, cax=caxes[2], label=CLABEL_EKE)

for ax in axes[:2, :].flatten():
    ax.set_xlabel("")

# plt.tight_layout()

plt.savefig("/work/mh0033/m300883/High_frequecy_flow/docs/plots/0after_defense/diff_lat_time_contour.pdf", dpi=300, bbox_inches="tight", transparent=True)

# %%
