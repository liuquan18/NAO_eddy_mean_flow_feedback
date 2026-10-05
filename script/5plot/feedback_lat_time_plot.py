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
import matplotlib
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator, FuncFormatter

from src.plotting.util import map_smooth
import src.plotting.util as util
import metpy.calc as mpcalc
from metpy.units import units

# %%
data_dir = "/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/0composite_feedback"

def _load(name):
    return xr.open_dataarray(os.path.join(data_dir, f"{name}.nc"))

# Jet stream
ua_pos_first = _load("ua_pos_1850")
ua_neg_first = _load("ua_neg_1850")
ua_pos_last  = _load("ua_pos_2090")
ua_neg_last  = _load("ua_neg_2090")

# Convergence of eddy momentum flux
momentum_pos_first = _load("Fdiv_phi_transient_pos_1850")
momentum_neg_first = _load("Fdiv_phi_transient_neg_1850")
momentum_pos_last  = _load("Fdiv_phi_transient_pos_2090")
momentum_neg_last  = _load("Fdiv_phi_transient_neg_2090")


# %%# upvp
upvp_pos_first = _load("upvp_pos_1850")
upvp_neg_first = _load("upvp_neg_1850")
upvp_pos_last  = _load("upvp_pos_2090")
upvp_neg_last  = _load("upvp_neg_2090")

#%%
awb_pos_first = _load("wb_anticyclonic_pos_1850")
awb_neg_first = _load("wb_anticyclonic_neg_1850")
awb_pos_last  = _load("wb_anticyclonic_pos_2090")
awb_neg_last  = _load("wb_anticyclonic_neg_2090")

#%%
cwb_pos_first = _load("wb_cyclonic_pos_1850")
cwb_neg_first = _load("wb_cyclonic_neg_1850")
cwb_pos_last  = _load("wb_cyclonic_pos_2090")
cwb_neg_last  = _load("wb_cyclonic_neg_2090")

# %%
ua_pos_first=ua_pos_first.sel(plev = 25000)
ua_neg_first=ua_neg_first.sel(plev = 25000)
ua_pos_last=ua_pos_last.sel(plev = 25000)
ua_neg_last=ua_neg_last.sel(plev = 25000)

#%%
upvp_pos_first=upvp_pos_first.sel(plev = 25000)
upvp_neg_first=upvp_neg_first.sel(plev = 25000)
upvp_pos_last=upvp_pos_last.sel(plev = 25000)
upvp_neg_last=upvp_neg_last.sel(plev = 25000)

# %% Prepare: average over event dim, compute diffs, scale baroclinicity
def _em(da):
    return da.mean(dim="event").sel(lat=slice(0, 90))

def _es(da):
    return da.sum(dim="event").sel(lat=slice(0, 90)) 
#%%
ua_p1 = _em(ua_pos_first);  ua_n1 = _em(ua_neg_first)
ua_p2 = _em(ua_pos_last);   ua_n2 = _em(ua_neg_last)
ua_d1 = ua_p1 - ua_n1;      ua_d2 = ua_p2 - ua_n2

uv_p1 = _em(upvp_pos_first);  uv_n1 = _em(upvp_neg_first)
uv_p2 = _em(upvp_pos_last);   uv_n2 = _em(upvp_neg_last)
uv_d1 = uv_p1 - uv_n1;      uv_d2 = uv_p2 - uv_n2

mom_p1 = _em(momentum_pos_first);  mom_n1 = _em(momentum_neg_first)
mom_p2 = _em(momentum_pos_last);   mom_n2 = _em(momentum_neg_last)
mom_d1 = mom_p1 - mom_n1;          mom_d2 = mom_p2 - mom_n2

awb_p1 = _es(awb_pos_first);  awb_n1 = _es(awb_neg_first)
awb_p2 = _es(awb_pos_last);   awb_n2 = _es(awb_neg_last)
awb_d1 = awb_p1 - awb_n1;      awb_d2 = awb_p2 - awb_n2 

cwb_p1 = _es(cwb_pos_first);  cwb_n1 = _es(cwb_neg_first)
cwb_p2 = _es(cwb_pos_last);   cwb_n2 = _es(cwb_neg_last)
cwb_d1 = cwb_p1 - cwb_n1;      cwb_d2 = cwb_p2 - cwb_n2


#%%
jet_loc_first = 47.56392575
jet_loc_last = 49.4291537

# +/- 10 degrees around the jet location
lat_min_first = jet_loc_first - 10
lat_max_first = jet_loc_first + 10
lat_min_last = jet_loc_last - 10
lat_max_last = jet_loc_last + 10


# %% Meridional gradient of ua (∂ua/∂y, units: s⁻¹ = m s⁻¹ per meter)
def _ua_meridional_grad(da):
    """Compute ∂ua/∂y in s⁻¹. Converts lat degrees → meters (R·Δlat·π/180)
    then applies np.gradient along the lat axis."""
    R = 6371229.0  # Earth radius in metres
    lat_rad = np.deg2rad(da.lat.values)   # radians
    y_m = R * lat_rad                     # metres along meridian
    grad_vals = np.gradient(da.values, y_m, axis=da.dims.index('lat'))
    return xr.DataArray(grad_vals, coords=da.coords, dims=da.dims)

uag_p1 = _ua_meridional_grad(ua_p1)*86400;  uag_n1 = _ua_meridional_grad(ua_n1)*86400
uag_p2 = _ua_meridional_grad(ua_p2)*86400;  uag_n2 = _ua_meridional_grad(ua_n2)*86400
uag_d1 = uag_p1 - uag_n1
uag_d2 = uag_p2 - uag_n2

# %% Contour levels
# -- difference (pos - neg) levels
ua_dlev   = np.arange(-12, 13, 2)
uag_dlev  = np.arange(-2, 2.1, 0.4)
uv_dlev   = np.arange(-20, 21, 4)
mom_dlev  = np.arange(-3, 3.1, 0.5)
awb_dlev  = np.arange(-3, 3.1, 1)
cwb_dlev  = np.arange(-1, 1.1, 0.5)

# -- absolute (per-phase) levels
ua_lev   = np.arange(-12, 13, 2)
uag_lev  = np.arange(-2, 2.1, 0.4)
uv_lev   = np.arange(-20, 21, 4)
mom_lev  = np.arange(-3, 3.1, 0.5)
awb_lev  = np.arange(-3, 3.1, 1)
cwb_lev  = np.arange(-1, 1.1, 0.5)



# %% Shared plot function
def _make_fig(rows_data, suptitle="", col_titles=None):
    """Create a (nrows × 3) lat-time figure.

    rows_data: list of (d1, d2, lev, lev_dd, label)
      d1    : data for 1850s
      d2    : data for 2090s
      lev   : contour levels for columns 0 and 1
      lev_dd: contour levels for column 2 (d2 - d1)
      label : colorbar title
    Columns: 1850s | 2090s | 2090s - 1850s
    """
    fig, axes = plt.subplots(
        nrows=len(rows_data), ncols=3,
        figsize=(8, 14),
        constrained_layout=False,
        sharey=True, sharex=True,
    )
    fig.subplots_adjust(left=0.09, right=0.83, top=0.93, bottom=0.08,
                        wspace=0.08, hspace=0.22)

    for row_idx, (d1, d2, lvl, ddlv, label) in enumerate(rows_data):
        t   = d1.time.values
        lat = d1.lat.values
        dd  = d2 - d1  # col2 − col1 (e.g. 2090s − 1850s, or neg − pos)

        for col_idx, (data, lv) in enumerate([(d1, lvl), (d2, lvl), (dd, ddlv)]):
            ax = axes[row_idx, col_idx]
            cf = ax.contourf(t, lat, data.values.T, levels=lv, cmap="RdBu_r", extend="both")
            ax.contour(t, lat, data.values.T,
                       levels=[l for l in lv if l != 0], colors="k", linewidths=0.5)
            if col_idx == 0:
                cf_main = cf

        # Dual-axis colorbar: left = lvl (cols 0&1), right = ddlv (col 2)
        bbox = axes[row_idx, 2].get_position()
        cax = fig.add_axes([bbox.x1 + 0.04, bbox.y0, 0.016, bbox.height])
        cb = fig.colorbar(cf_main, cax=cax, orientation="vertical", extend="both")
        cb.set_ticks(lvl)
        cb.ax.tick_params(labelsize=7)
        cb.ax.yaxis.set_ticks_position("left")
        cb.ax.yaxis.set_label_position("left")
        cb.ax.set_title(label, fontsize=7, pad=4)

        pmin, pmax = float(lvl[0]),  float(lvl[-1])
        dmin, dmax = float(ddlv[0]), float(ddlv[-1])
        ax_sec = cax.secondary_yaxis(
            "right",
            functions=(lambda x, pm=pmin, pm2=pmax, dm=dmin, dm2=dmax:
                           dm + (x - pm) * (dm2 - dm) / (pm2 - pm),
                       lambda x, pm=pmin, pm2=pmax, dm=dmin, dm2=dmax:
                           pm + (x - dm) * (pm2 - pm) / (dm2 - dm)),
        )
        ax_sec.set_yticks(ddlv)
        ax_sec.tick_params(labelsize=7)

    n_last = 3 * (len(rows_data) - 1)
    for i, ax in enumerate(axes.flatten()):
        if i >= n_last:
            ax.set_xlabel("Lag (days)", fontsize=8)
        if i % 3 == 0:
            ax.set_ylabel("Latitude (°N)", fontsize=8)
        ax.tick_params(labelsize=7)
        ax.text(0.02, 0.98, chr(97 + i), transform=ax.transAxes,
                fontsize=9, fontweight="bold", va="top", ha="left")
        ax.set_xlim(-5, 20)
        ax.axvline(0, color="k", linestyle=":", linewidth=0.5)

    _col_titles = col_titles if col_titles is not None else ["1850s", "2090s", "2090s - 1850s"]
    for ax, title in zip(axes[0, :], _col_titles):
        ax.set_title(title, fontsize=8)

    if suptitle:
        fig.suptitle(suptitle, fontsize=10, y=0.97)

    return fig


def _make_change_fig(rows_data, suptitle="", col_titles=None):
    """Like _make_fig but col3 = d1 - d2 (col1 − col2, e.g. Δpos − Δneg)."""
    fig, axes = plt.subplots(
        nrows=len(rows_data), ncols=3,
        figsize=(8, 14),
        constrained_layout=False,
        sharey=True, sharex=True,
    )
    fig.subplots_adjust(left=0.09, right=0.83, top=0.93, bottom=0.08,
                        wspace=0.08, hspace=0.22)

    for row_idx, (d1, d2, lvl, ddlv, label) in enumerate(rows_data):
        t   = d1.time.values
        lat = d1.lat.values
        dd  = d1 - d2  # col1 − col2 (e.g. Δpos − Δneg)

        for col_idx, (data, lv) in enumerate([(d1, lvl), (d2, lvl), (dd, ddlv)]):
            ax = axes[row_idx, col_idx]
            cf = ax.contourf(t, lat, data.values.T, levels=lv, cmap="RdBu_r", extend="both")
            ax.contour(t, lat, data.values.T,
                       levels=[l for l in lv if l != 0], colors="k", linewidths=0.5)
            if col_idx == 0:
                cf_main = cf

        bbox = axes[row_idx, 2].get_position()
        cax = fig.add_axes([bbox.x1 + 0.04, bbox.y0, 0.016, bbox.height])
        cb = fig.colorbar(cf_main, cax=cax, orientation="vertical", extend="both")
        cb.set_ticks(lvl)
        cb.ax.tick_params(labelsize=7)
        cb.ax.yaxis.set_ticks_position("left")
        cb.ax.yaxis.set_label_position("left")
        cb.ax.set_title(label, fontsize=7, pad=4)

        pmin, pmax = float(lvl[0]),  float(lvl[-1])
        dmin, dmax = float(ddlv[0]), float(ddlv[-1])
        ax_sec = cax.secondary_yaxis(
            "right",
            functions=(lambda x, pm=pmin, pm2=pmax, dm=dmin, dm2=dmax:
                           dm + (x - pm) * (dm2 - dm) / (pm2 - pm),
                       lambda x, pm=pmin, pm2=pmax, dm=dmin, dm2=dmax:
                           pm + (x - dm) * (pm2 - pm) / (dm2 - dm)),
        )
        ax_sec.set_yticks(ddlv)
        ax_sec.tick_params(labelsize=7)

    n_last = 3 * (len(rows_data) - 1)
    for i, ax in enumerate(axes.flatten()):
        if i >= n_last:
            ax.set_xlabel("Lag (days)", fontsize=8)
        if i % 3 == 0:
            ax.set_ylabel("Latitude (°N)", fontsize=8)
        ax.tick_params(labelsize=7)
        ax.text(0.02, 0.98, chr(97 + i), transform=ax.transAxes,
                fontsize=9, fontweight="bold", va="top", ha="left")
        ax.set_xlim(-5, 20)
        ax.axvline(0, color="k", linestyle=":", linewidth=0.5)

    _col_titles = col_titles if col_titles is not None else ["col1", "col2", "col1 - col2"]
    for ax, title in zip(axes[0, :], _col_titles):
        ax.set_title(title, fontsize=8)

    if suptitle:
        fig.suptitle(suptitle, fontsize=10, y=0.97)

    return fig

# %% Plot 1 – difference (pos - neg)
diff_rows = [
    (ua_d1,  ua_d2,  ua_dlev,  ua_dlev  / 2, "$\\Delta u$ / m s$^{-1}$"),
    (awb_d1, awb_d2, awb_dlev, awb_dlev / 2, "$\\Delta$ awb / day"),
    (cwb_d1, cwb_d2, cwb_dlev, cwb_dlev / 2, "$\\Delta$ cwb / day"),
    (uag_d1, uag_d2, uag_dlev, uag_dlev / 2, "$\\Delta(\\partial_y u)$ / day$^{-1}$"),
    (uv_d1,  uv_d2,  uv_dlev,  uv_dlev  / 2, "$\\Delta(u'v')$ / m$^2$ s$^{-2}$"),
    (mom_d1, mom_d2, mom_dlev, mom_dlev / 2,  "$\\Delta(\\partial_y u'v')$ / m s$^{-1}$ day$^{-1}$"),
]
fig_diff = _make_fig(diff_rows, suptitle="NAO positive $-$ negative")

plt.savefig(
    "/work/mh0033/m300883/High_frequecy_flow/docs/plots/0after_defense/feedback_diff_ua_grad_upvp.pdf",
    dpi=300,
)

# %% Plot 2 – NAO positive
pos_rows = [
    (ua_p1,  ua_p2,  ua_lev,  ua_dlev / 2,  "$u$ / m s$^{-1}$"),
    (awb_p1, awb_p2, awb_lev, awb_dlev / 2, "awb / day"),
    (cwb_p1, cwb_p2, cwb_lev, cwb_dlev / 2, "cwb / day"),
    (uag_p1, uag_p2, uag_lev, uag_dlev / 2, "$\\partial_y u$ / day$^{-1}$"),
    (uv_p1,  uv_p2,  uv_lev,  uv_dlev / 2,  "$u'v'$ / m$^2$ s$^{-2}$"),
    (mom_p1, mom_p2, mom_lev, mom_dlev / 2, "$\\partial_y u'v'$ / m s$^{-1}$ day$^{-1}$"),
]
fig_pos = _make_fig(pos_rows, suptitle="NAO positive")

plt.savefig(
    "/work/mh0033/m300883/High_frequecy_flow/docs/plots/0after_defense/feedback_pos_ua_grad_upvp.pdf",
    dpi=300,
)

# %% Plot 3 – NAO negative
neg_rows = [
    (ua_n1,  ua_n2,  ua_lev,  ua_dlev / 2,  "$u$ / m s$^{-1}$"),
    (awb_n1, awb_n2, awb_lev, awb_dlev / 2, "awb / day"),
    (cwb_n1, cwb_n2, cwb_lev, cwb_dlev / 2, "cwb / day"),
    (uag_n1, uag_n2, uag_lev, uag_dlev / 2, "$\\partial_y u$ / day$^{-1}$"),
    (uv_n1,  uv_n2,  uv_lev,  uv_dlev / 2,  "$u'v'$ / m$^2$ s$^{-2}$"),
    (mom_n1, mom_n2, mom_lev, mom_dlev / 2, "$\\partial_y u'v'$ / m s$^{-1}$ day$^{-1}$"),
]
fig_neg = _make_fig(neg_rows, suptitle="NAO negative")

plt.savefig(
    "/work/mh0033/m300883/High_frequecy_flow/docs/plots/0after_defense/feedback_neg_ua_grad_upvp.pdf",
    dpi=300,
)

# %% Plot 4 – Decadal change: Δ NAO+ | Δ NAO− | Δ NAO+ − Δ NAO−
# col1 = pos_2090 − pos_1850,  col2 = neg_2090 − neg_1850,  col3 = col1 − col2
change_rows = [
    (ua_p2  - ua_p1,  ua_n2  - ua_n1,  ua_dlev  / 2, ua_dlev  / 2, "$\\delta u$ / m s$^{-1}$"),
    (awb_p2 - awb_p1, awb_n2 - awb_n1, awb_dlev / 2, awb_dlev / 2, "$\\delta$ awb / day"),
    (cwb_p2 - cwb_p1, cwb_n2 - cwb_n1, cwb_dlev / 2, cwb_dlev / 2, "$\\delta$ cwb / day"),
    (uag_p2 - uag_p1, uag_n2 - uag_n1, uag_dlev / 2, uag_dlev / 2, "$\\delta(\\partial_y u)$ / day$^{-1}$"),
    (uv_p2  - uv_p1,  uv_n2  - uv_n1,  uv_dlev  / 2, uv_dlev  / 2, "$\\delta(u'v')$ / m$^2$ s$^{-2}$"),
    (mom_p2 - mom_p1, mom_n2 - mom_n1, mom_dlev / 2, mom_dlev / 2,  "$\\delta(\\partial_y u'v')$ / m s$^{-1}$ day$^{-1}$"),
]
fig_change = _make_change_fig(
    change_rows,
    suptitle="Decadal change (2090s $-$ 1850s)",
    col_titles=["$\\delta$ NAO+", "$\\delta$ NAO$-$", "$\\delta$ NAO+ $-$ $\\delta$ NAO$-$"],
)

plt.savefig(
    "/work/mh0033/m300883/High_frequecy_flow/docs/plots/0after_defense/feedback_change_pos_neg.pdf",
    dpi=300,
)

# %%
