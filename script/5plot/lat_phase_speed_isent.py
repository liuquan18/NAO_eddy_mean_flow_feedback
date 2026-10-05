# %%
import glob
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

from src.data_helper.read_variable import read_prime

# %%


def read_dec(decade):
    wb_dir = "/scratch/m/m300883/MPI_GE_CMIP6/vsts_space_time_spectra_daily/r*i1p1f1/"

    wb_files = sorted(glob.glob(wb_dir + f"*dec_{decade}*.nc"))
    if len(wb_files) == 0:
        wb_files = sorted(glob.glob(wb_dir + f"dec_{decade}/*.nc"))
    if len(wb_files) == 0:
        raise FileNotFoundError(f"No vsts files found for decade={decade}")

    wb_data = xr.open_mfdataset(
        wb_files, combine="nested", parallel=True, concat_dim="ens"
    )
    wb_data = wb_data.mean(dim="ens")
    wb_data["decade"] = decade
    return wb_data.compute()


def calc_second_meridional_derivative(data, smooth=True):
    if smooth:
        data = data.rolling(lat=3, center=True).median().dropna("lat")

    r_earth = 6.371e6
    dlat_rad = np.deg2rad(data.lat.values[1] - data.lat.values[0])
    dy = r_earth * dlat_rad

    first_deriv = np.gradient(data.values, axis=1) / dy
    second_deriv = np.gradient(first_deriv, axis=1) / dy

    return xr.DataArray(
        second_deriv,
        coords=data.coords,
        dims=data.dims,
        attrs={"units": "1/m²", "long_name": "Second meridional derivative"},
    )


# %%
# Top-row data: transient eddy momentum flux in latitude-phase speed space
phase_speed_first = read_prime(
    decade=1850,
    var="uava_phase_speed_spectrum",
    name=None,
    model_dir="MPI_GE_CMIP6",
    suffix="",
)
# %%
phase_speed_last = read_prime(
    decade=2090,
    var="uava_phase_speed_spectrum",
    name=None,
    model_dir="MPI_GE_CMIP6",
    suffix="",
)

# %%
ua_first = xr.open_dataset(
    "/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/ua_monthly_ensmean/ua_monmean_ensmean_185005_185909.nc"
)
ua_first = ua_first["ua"].mean(dim="time").sel(plev=25000).mean(dim="lon")
ua_first = ua_first.sel(lat=slice(0, 90))
# %%
ua_last = xr.open_dataset(
    "/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/ua_monthly_ensmean/ua_monmean_ensmean_209005_209909.nc"
)
ua_last = ua_last["ua"].mean(dim="time").sel(plev=25000).mean(dim="lon")
ua_last = ua_last.sel(lat=slice(0, 90))


# %%
lats = phase_speed_first["lat"].values
phase_speeds_2d = phase_speed_first["phase_speed_grid"].values
P_cp_first = phase_speed_first["P_eastward"].mean(dim="ens").values
P_cn_first = phase_speed_first["P_westward"].mean(dim="ens").values

P_cp_last = phase_speed_last["P_eastward"].mean(dim="ens").values
P_cn_last = phase_speed_last["P_westward"].mean(dim="ens").values

# %%
# Use middle latitude for representative phase speeds
mid_lat_idx = len(lats) // 2
phase_speeds_plot = phase_speeds_2d[mid_lat_idx, :]


# %%
# Bottom-row data: quasi-stationary eddy thermal feedback proxy in latitude-wavenumber space
vsts_1850 = read_dec(1850)
vsts_2090 = read_dec(2090)

#%%
vsts_1850_sum = vsts_1850.sum(dim="freq").isel(wavenumber=slice(1, None))
vsts_2090_sum = vsts_2090.sum(dim="freq").isel(wavenumber=slice(1, None))

vsts_1850_combined = vsts_1850_sum.K_p + vsts_1850_sum.K_n
vsts_2090_combined = vsts_2090_sum.K_p + vsts_2090_sum.K_n

feedback_1850 = calc_second_meridional_derivative(vsts_1850_combined).compute()
feedback_2090 = calc_second_meridional_derivative(vsts_2090_combined).compute()


# %%
# Combined 2x2 plot:
# Row 1: phase speed spectrum (overlay + difference)
# Row 2: meridional-derivative feedback (overlay + difference)
fig, axes = plt.subplots(2, 2, figsize=(12, 8), sharey="row")

phase_speeds_combined = np.concatenate([-phase_speeds_plot[::-1], phase_speeds_plot])
P_combined_first = np.concatenate([P_cn_first[:, ::-1], P_cp_first], axis=1)
P_combined_last = np.concatenate([P_cn_last[:, ::-1], P_cp_last], axis=1)

# Define consistent levels excluding zero
levels_mom = np.arange(-1.2, 1.21, 0.1)
levels_mom_line = levels_mom[levels_mom != 0]  # Remove zero level

levels_heat = np.arange(-5, 5.1, 1) * 1e-9
levels_heat_line = levels_heat[levels_heat != 0]  # Remove zero level


# Left plot: first as colormap, last as contours
cs_fill = axes[0, 0].contourf(
    lats,
    phase_speeds_combined,
    P_combined_first.T,
    levels=levels_mom,
    cmap="RdBu_r",
    extend="both",
)

cs_line = axes[0, 0].contour(
    lats,
    phase_speeds_combined,
    P_combined_last.T,
    levels=levels_mom,
    colors="black",
    linewidths=1.5,
)

ua_first.plot(
    x="lat",
    ax=axes[0, 0],
    color="k",
    linewidth=4,
    linestyle="-",
    label="Zonal Wind 1850s",
)
ua_last.plot(
    x="lat",
    ax=axes[0, 0],
    color="k",
    linewidth=4,
    linestyle="--",
    label="Zonal Wind 2090s",
)

# Right plot: Difference
P_combined_diff = P_combined_last - P_combined_first


cs_diff = axes[0, 1].contourf(
    lats,
    phase_speeds_combined,
    P_combined_diff.T,
    levels=np.arange(-0.3, 0.31, 0.03),
    cmap="RdBu_r",
    extend="both",
)

ua_diff = ua_last - ua_first
ua_diff.plot(x="lat", ax=axes[0, 1], color="k", linewidth=4, label="Zonal Wind Change")


for ax in axes[0, :]:
    ax.axhline(0, color="gray", linestyle="--", linewidth=1.5, alpha=0.5)
    ax.set_xlabel("Latitude (°N)", fontsize=12)
    ax.set_title("")
    ax.set_ylim(-20, 30)
    ax.legend(fontsize=10)
    ax.set_ylabel("")

axes[0, 0].set_ylabel(r"Phase speed (ua) /$ms^{-1}$", fontsize=12)

fig.colorbar(cs_fill, ax=axes[0, 0], label="$u'v' / m^{2} s^{-2} \cdot \Delta c^{-1}$")
fig.colorbar(cs_diff, ax=axes[0, 1], label="$u'v' / m^{2} s^{-2} \cdot \Delta c^{-1}$")

# Bottom row: feedback in latitude-wavenumber space
# 1850 as shading
heat_first = feedback_1850.plot.contourf(
    x="lat",
    y="wavenumber",
    ax=axes[1, 0],
    add_labels=False,
    levels=levels_heat,
    cmap="RdBu_r",
    extend="both",
    cbar_kwargs={
        "label": r"$\frac{\partial^2}{\partial y^2} (v'\theta')$ / K $m^{-1} s^{-1} \cdot \Delta c^{-1}$"
    },
)
# 2090 as contours
heat_last = feedback_2090.plot.contour(
    x="lat",
    y="wavenumber",
    ax=axes[1, 0],
    add_labels=False,
    levels=levels_heat_line,
    colors="black",
    linewidths=1.5,
)

# difference plot
feedback_diff = feedback_2090 - feedback_1850
heat_diff = feedback_diff.plot.contourf(
    x="lat",
    y="wavenumber",
    ax=axes[1, 1],
    add_labels=False,
    levels=np.arange(-1.2, 1.3, 0.2) * 1e-9,
    cmap="RdBu_r",
    extend="both",
    cbar_kwargs={
        "label": r"$\frac{\partial^2}{\partial y^2} (v'\theta')$ / K $m^{-1} s^{-1} \cdot \Delta c^{-1}$"
    },
)


for ax in axes[1, :]:
    ax.set_ylim(2, 6)
    ax.set_yticks(range(2, 7))
    ax.set_xlabel("Latitude (°N)", fontsize=12)
    ax.set_title("")
    ax.set_ylabel("")
axes[1, 0].set_ylabel("Wavenumber", fontsize=12)

# change the title of the colorbar


panel_labels = ["a", "b", "c", "d"]
for label, ax in zip(panel_labels, axes.ravel()):
    ax.text(
        0.02,
        0.96,
        label,
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=14,
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7, edgecolor="none"),
    )

plt.tight_layout()
plt.savefig("/work/mh0033/m300883/High_frequecy_flow/docs/plots/0after_defense/lat_phase_speed_wavenumber.pdf", dpi=300, transparent=True)
# %%
