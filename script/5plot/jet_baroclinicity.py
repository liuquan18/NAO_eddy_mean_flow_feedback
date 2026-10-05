# %%
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import importlib

from src.data_helper import read_composite
from src.plotting.util import map_smooth

importlib.reload(read_composite)

read_comp_var = read_composite.read_comp_var
# %%
ua_pos_first = read_comp_var(
    "ua",
    "pos",
    1850,
    time_window=(-10, 5),
    method="mean",
    name="ua",
    model_dir="MPI_GE_CMIP6_allplev",
)
ua_neg_first = read_comp_var(
    "ua",
    "neg",
    1850,
    time_window=(-10, 5),
    method="mean",
    name="ua",
    model_dir="MPI_GE_CMIP6_allplev",
)
# %%
ua_pos_last = read_comp_var(
    "ua",
    "pos",
    2090,
    time_window=(-10, 5),
    method="mean",
    name="ua",
    model_dir="MPI_GE_CMIP6_allplev",
)
ua_neg_last = read_comp_var(
    "ua",
    "neg",
    2090,
    time_window=(-10, 5),
    method="mean",
    name="ua",
    model_dir="MPI_GE_CMIP6_allplev",
)
# %%
baroc_pos_first = read_comp_var(
    "eady_growth_rate",
    "pos",
    1850,
    time_window=(-10, 5),
    method="mean",
    name="eady_growth_rate",
    model_dir="MPI_GE_CMIP6_allplev",
)
baroc_neg_first = read_comp_var(
    "eady_growth_rate",
    "neg",
    1850,
    time_window=(-10, 5),
    method="mean",
    name="eady_growth_rate",
    model_dir="MPI_GE_CMIP6_allplev",
)
baroc_pos_last = read_comp_var(
    "eady_growth_rate",
    "pos",
    2090,
    time_window=(-10, 5),
    method="mean",
    name="eady_growth_rate",
    model_dir="MPI_GE_CMIP6_allplev",
)
baroc_neg_last = read_comp_var(
    "eady_growth_rate",
    "neg",
    2090,
    time_window=(-10, 5),
    method="mean",
    name="eady_growth_rate",
    model_dir="MPI_GE_CMIP6_allplev",
)
# %%
# baroclinicity from s-1 to day-1
baroc_pos_first = baroc_pos_first * 86400
baroc_neg_first = baroc_neg_first * 86400
baroc_pos_last = baroc_pos_last * 86400
baroc_neg_last = baroc_neg_last * 86400


# %%
# ua select 25000
ua_pos_first = ua_pos_first.sel(plev=25000)
ua_neg_first = ua_neg_first.sel(plev=25000)
ua_pos_last = ua_pos_last.sel(plev=25000)
ua_neg_last = ua_neg_last.sel(plev=25000)
# %%
# baroc select 85000
baroc_pos_first = baroc_pos_first.sel(plev=85000)
baroc_neg_first = baroc_neg_first.sel(plev=85000)
baroc_pos_last = baroc_pos_last.sel(plev=85000)
baroc_neg_last = baroc_neg_last.sel(plev=85000)

# %%
# smooth the baroc
baroc_pos_first = map_smooth(baroc_pos_first, 5, 5)
baroc_neg_first = map_smooth(baroc_neg_first, 5, 5)
baroc_pos_last = map_smooth(baroc_pos_last, 5, 5)
baroc_neg_last = map_smooth(baroc_neg_last, 5, 5)
# %%
ua_diff_first = ua_pos_first - ua_neg_first
ua_diff_last = ua_pos_last - ua_neg_last
baroc_diff_first = baroc_pos_first - baroc_neg_first
baroc_diff_last = baroc_pos_last - baroc_neg_last
# %%
uhat_levels_div = np.arange(-15, 16, 3)  # for difference
baroc_levels_div = np.arange(-3, 3.1, 0.5)  # for difference

# %%
fig, axes = plt.subplots(
    nrows=1,
    ncols=2,
    figsize=(8, 4),
    subplot_kw={"projection": ccrs.Orthographic(-30, 70)},
    constrained_layout=True,
)

# --- Jet stream difference ---
cf_hat_diff_first = ua_diff_first.plot.contourf(
    ax=axes[0],
    transform=ccrs.PlateCarree(),
    cmap="RdBu_r",
    add_colorbar=True,
    extend="both",
    levels=uhat_levels_div,
    cbar_kwargs={
        "label": r"$\Delta\overline{u}$ / ms$^{-1}$",
        "orientation": "horizontal",
        "shrink": 0.8,
        "pad": 0.05,
        "aspect": 20,
    },
)

# last decade in contour
cf_hat_diff_last = ua_diff_last.plot.contour(
    ax=axes[0],
    transform=ccrs.PlateCarree(),
    add_colorbar=False,
    extend="both",
    linewidths=1,
    colors="black",
    levels=[l for l in uhat_levels_div if l != 0],  # exclude zero
)

# --- Baroclinicity difference ---
cf_baroc_diff_first = baroc_diff_first.plot.contourf(
    ax=axes[1],
    transform=ccrs.PlateCarree(),
    cmap="RdBu_r",
    add_colorbar=True,
    extend="both",
    levels=baroc_levels_div,
    cbar_kwargs={
        "label": r"$\Delta \overline{\sigma_E}$ / day$^{-1}$",
        "orientation": "horizontal",
        "shrink": 0.8,
        "pad": 0.05,
        "aspect": 20,
    },
)

# last decade in contour
cf_baroc_diff_last = baroc_diff_last.plot.contour(
    ax=axes[1],
    transform=ccrs.PlateCarree(),
    add_colorbar=False,
    extend="both",
    linewidths=1,
    colors="black",
    levels=[l for l in baroc_levels_div if l != 0],  # exclude zero
)

# --- Formatting ---
for i, ax in enumerate(axes.flatten()):
    ax.coastlines(color="grey", linewidth=1)
    ax.gridlines(
        draw_labels=False, linewidth=1, color="grey", alpha=0.5, linestyle="--"
    )
    ax.set_global()
    ax.set_title("")

    # add a, b labels
    ax.text(
        0.02,
        0.9,
        f"{chr(97 + i)}",
        transform=ax.transAxes,
        fontsize=12,
        fontweight="bold",
    )

# savefig
plt.savefig(
    "/work/mh0033/m300883/High_frequecy_flow/docs/plots/0after_defense/jet_baroclinicity_diff.pdf",
    dpi=500,
    bbox_inches="tight",
    metadata={"Creator": __file__},
    transparent=True,
)
# %%
# %%
