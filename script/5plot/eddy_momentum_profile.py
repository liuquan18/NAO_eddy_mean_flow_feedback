# %%
import numpy as np
import matplotlib.pyplot as plt

from src.data_helper import read_composite
import importlib

importlib.reload(read_composite)

read_EP_flux = read_composite.read_EP_flux


# %%
# Read transient EP-flux divergence for positive/negative phase in first/last decade and climatology
Tdivphi_pos_first = read_EP_flux(
    phase="pos", decade=1850, eddy="transient", ano=False, lon_mean=False, region=None
)[2]
Tdivphi_neg_first = read_EP_flux(
    phase="neg", decade=1850, eddy="transient", ano=False, lon_mean=False, region=None
)[2]
Tdivphi_pos_last = read_EP_flux(
    phase="pos", decade=2090, eddy="transient", ano=False, lon_mean=False, region=None
)[2]
Tdivphi_neg_last = read_EP_flux(
    phase="neg", decade=2090, eddy="transient", ano=False, lon_mean=False, region=None
)[2]
Tdivphi_clima_first = read_EP_flux(
    phase="clima", decade=1850, eddy="transient", ano=False, lon_mean=False, region=None
)[2]
Tdivphi_clima_last = read_EP_flux(
    phase="clima", decade=2090, eddy="transient", ano=False, lon_mean=False, region=None
)[2]


# %%
def anomaly(ds, ds_clima):
    ds = ds.sel(time=slice(-10, 5)).mean(dim=("time", "event", "lon"))
    ds_clima = ds_clima.mean(dim=("lon"))
    return (ds - ds_clima).load()


# %%
Tdiv_phi_pos_first_anomaly = anomaly(Tdivphi_pos_first, Tdivphi_clima_first)
Tdiv_phi_neg_first_anomaly = anomaly(Tdivphi_neg_first, Tdivphi_clima_first)
Tdiv_phi_pos_last_anomaly = anomaly(Tdivphi_pos_last, Tdivphi_clima_last)
Tdiv_phi_neg_last_anomaly = anomaly(Tdivphi_neg_last, Tdivphi_clima_last)


# %%
phi_trans_levels = np.arange(-0.2, 0.21, 0.05)
phi_trans_levels_diff = np.arange(-0.2, 0.21, 0.05)

fig, axes = plt.subplots(1, 3, figsize=(10, 4), sharex=False, sharey=True)

# axes[0]: positive phase, transient anomaly
cf_phi_trans_pos = Tdiv_phi_pos_first_anomaly.plot.contourf(
    ax=axes[0],
    levels=phi_trans_levels,
    cmap="RdBu_r",
    add_colorbar=False,
    extend="both",
    xlim=(0, 90),
    ylim=(100000, 10000),
)
contour_levels = [l for l in phi_trans_levels if l != 0]
Tdiv_phi_pos_last_anomaly.plot.contour(
    ax=axes[0],
    levels=contour_levels,
    colors="k",
    linewidths=1,
    add_colorbar=False,
    xlim=(0, 90),
    ylim=(100000, 10000),
)

# axes[1]: negative phase, transient anomaly
cf_phi_trans_neg = Tdiv_phi_neg_first_anomaly.plot.contourf(
    ax=axes[1],
    levels=phi_trans_levels,
    cmap="RdBu_r",
    add_colorbar=False,
    extend="both",
    xlim=(0, 90),
    ylim=(100000, 10000),
)
Tdiv_phi_neg_last_anomaly.plot.contour(
    ax=axes[1],
    levels=contour_levels,
    colors="k",
    linewidths=1,
    add_colorbar=False,
    xlim=(0, 90),
    ylim=(100000, 10000),
)

# axes[2]: pos-neg difference in first/last decades
diff_first = Tdiv_phi_pos_first_anomaly - Tdiv_phi_neg_first_anomaly
diff_last = Tdiv_phi_pos_last_anomaly - Tdiv_phi_neg_last_anomaly

cf_phi_trans_diff = diff_first.plot.contourf(
    ax=axes[2],
    levels=phi_trans_levels_diff,
    cmap="RdBu_r",
    add_colorbar=False,
    extend="both",
    xlim=(0, 90),
    ylim=(100000, 10000),
)
contour_levels_diff = [l for l in phi_trans_levels_diff if l != 0]
diff_last.plot.contour(
    ax=axes[2],
    levels=contour_levels_diff,
    colors="k",
    linewidths=1,
    add_colorbar=False,
    xlim=(0, 90),
    ylim=(100000, 10000),
)

# Add a colorbar for each subplot
cbar0 = fig.colorbar(
    cf_phi_trans_pos,
    ax=axes[0],
    orientation="horizontal",
    fraction=0.08,
    pad=0.15,
    aspect=30,
    shrink=0.8,
    label=r"$-\frac{\partial}{\partial y} (\overline{u'v'})$ / m $s^{-1}$ day $^{-1}$",
)
cbar0.set_ticks([-0.2, -0.1, 0.0, 0.1, 0.2])

cbar1 = fig.colorbar(
    cf_phi_trans_neg,
    ax=axes[1],
    orientation="horizontal",
    fraction=0.08,
    pad=0.15,
    aspect=30,
    shrink=0.8,
    label=r"$-\frac{\partial}{\partial y} (\overline{u'v'})$ / m $s^{-1}$ day $^{-1}$",
)
cbar1.set_ticks([-0.2, -0.1, 0.0, 0.1, 0.2])

cbar2 = fig.colorbar(
    cf_phi_trans_diff,
    ax=axes[2],
    orientation="horizontal",
    fraction=0.08,
    pad=0.15,
    aspect=30,
    shrink=0.8,
    label=r"$-\frac{\partial}{\partial y} (\overline{u'v'})$ / m $s^{-1}$ day $^{-1}$",
)
cbar2.set_ticks([-0.2, -0.1, 0.0, 0.1, 0.2])

# Axis labels
axes[0].set_ylabel("Pressure / hPa")
axes[0].set_yticks(
    [100000, 90000, 80000, 70000, 60000, 50000, 40000, 30000, 20000, 10000]
)
axes[0].set_yticklabels([str(int(tick / 100)) for tick in axes[0].get_yticks()])

for ax in axes:
    ax.set_xlabel("lat [°N]")

axes[1].set_ylabel("")
axes[2].set_ylabel("")

for i, ax in enumerate(axes):
    ax.text(
        0.1,
        0.88,
        chr(97 + i),
        transform=ax.transAxes,
        fontsize=14,
        fontweight="bold",
        va="bottom",
        ha="right",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7, edgecolor="none"),
    )

plt.savefig(
    "/work/mh0033/m300883/High_frequecy_flow/docs/plots/0after_defense/eddy_momentum_transient_profile.pdf",
    bbox_inches="tight",
)
# %%
