# %%
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

import matplotlib.colors as mcolors
import pandas as pd
import seaborn as sns
from src.data_helper.read_NAO_extremes import read_NAO_extremes
import glob
import logging

logging.basicConfig(level=logging.INFO)
# %%
# NAO monthly data


def read_extrc(model, fixed_pattern="decade_mpi"):
    """read extreme counts"""
    odir = "/work/mh0033/m300883/Tel_MMLE/data/" + model + "/extreme_count/"
    filename = f"plev_50000_{fixed_pattern}_first_JJA_extre_counts.nc"
    ds = xr.open_dataset(odir + filename).pc

    # divide the ensemble size of each model
    ens_sizes = {
        "MPI_GE": 100,
        "MPI_GE_onepct": 100,
        "CanESM2": 50,
        "CESM1_CAM5": 40,
        "MK36": 30,
        "GFDL_CM3": 20,
        "MPI_GE_CMIP6": 50,
    }
    ds = ds / ens_sizes[model]
    return ds


# %%
NAO_monthly_extremes = read_extrc("MPI_GE_CMIP6", fixed_pattern="decade_mpi")


# %% NAO daily extremes
def NAO_extremes(return_days=False, threshold=7):
    NAO_pos_counts = pd.DataFrame(columns=["decade", "count"])
    NAO_neg_counts = pd.DataFrame(columns=["decade", "count"])

    for i, dec in enumerate(range(1850, 2100, 10)):
        NAO_pos = read_NAO_extremes(dec, "positive")
        NAO_neg = read_NAO_extremes(dec, "negative")

        # filter only duration above 7 days
        NAO_pos = NAO_pos[NAO_pos["extreme_duration"] >= threshold]
        NAO_neg = NAO_neg[NAO_neg["extreme_duration"] >= threshold]

        if return_days:
            # NAO duration sum
            NAO_pos_count = NAO_pos["extreme_duration"].sum() / 50
            NAO_neg_count = NAO_neg["extreme_duration"].sum() / 50

        else:
            NAO_pos_count = NAO_pos.shape[0] / 50
            NAO_neg_count = NAO_neg.shape[0] / 50

        NAO_pos_counts.loc[i] = [dec, NAO_pos_count]
        NAO_neg_counts.loc[i] = [dec, NAO_neg_count]

    return NAO_pos_counts, NAO_neg_counts


# %%
NAO_pos_count, NAO_neg_count = NAO_extremes(False, 5)
NAO_pos_days, NAO_neg_days = NAO_extremes(True, 5)
# %%
NAO_pos_days = NAO_pos_days.rename(columns={"count": "days"})
NAO_neg_days = NAO_neg_days.rename(columns={"count": "days"})
# %%
NAO_count_merge = pd.merge(
    NAO_pos_count, NAO_neg_count, on="decade", suffixes=("_pos", "_neg")
)
NAO_days_merge = pd.merge(
    NAO_pos_days, NAO_neg_days, on="decade", suffixes=("_pos", "_neg")
)
NAO_merge = pd.merge(NAO_count_merge, NAO_days_merge, on="decade")
# %%
NAO_merge["decade"] = NAO_merge["decade"].astype(int)


# %%
# wave breaking


def read_dec(decade):
    base_dir = "/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6/wb_both_allisen_fldmean_dec/"
    wb_dir = f"{base_dir}r*i1p1f1/wb_both_allisen_fldmean_dec_{decade}_r*i1p1f1.nc"
    wb_files = glob.glob(wb_dir)

    wb_data = xr.open_mfdataset(
        wb_files, combine="nested", parallel=True, concat_dim="ens"
    )
    wb_data = wb_data.mean(dim="ens")
    wb_data["decade"] = decade
    return wb_data.compute()


wbs = []
for dec in range(1850, 2090, 10):
    wb_dec = read_dec(dec)
    wbs.append(wb_dec)

wb_all = xr.concat(wbs, dim="decade")


# %%
# # # eady growth rate
# eady_gr = xr.open_dataset("/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/0std_change/eady_growth_rate_decmean_ensmean_40_70_half.nc")
# # scale by divide by 1850s value
# eady_gr_scale = eady_gr['std']/eady_gr['std'].isel(time = 0)
# eady_gr_scale = eady_gr_scale.sel(plev = 85000).squeeze()
# %%
# %%
# steady eddy thermal feedback
steady_heat = xr.open_dataset(
    "/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/0std_change/steady_eddy_heat_d2y2_decmean_ensmean_40_70N.nc"
)
steady_heat = steady_heat["std"].sel(plev=85000).squeeze()
steady_heat_scale = steady_heat / steady_heat.isel(time=0)
# %%
awb_df = wb_all["awb_fldmean"].squeeze().to_dataframe("awb").reset_index()
cwb_df = wb_all["cwb_fldmean"].squeeze().to_dataframe("cwb").reset_index()
# %%
steady_heat_scale_df = steady_heat_scale.to_dataframe("thermal_feedback").reset_index()
steady_heat_scale_df["decade"] = (steady_heat_scale_df["time"].dt.year // 10) * 10


# %%
fig, axes = plt.subplots(4, 1, figsize=(3.5, 10))
plt.subplots_adjust(hspace=0.0)

# Monthly NAO extremes
NAO_monthly_extremes.sel(extr_type="pos", mode="NAO", confidence="true").plot.line(
    ax=axes[0],
    x="time",
    color="k",
    linewidth=1.5,
    label="pos NAO",
    add_legend=False,
)

NAO_monthly_extremes.sel(extr_type="neg", mode="NAO", confidence="true").plot.line(
    ax=axes[0],
    x="time",
    color="k",
    linewidth=1.5,
    linestyle="--",
    label="neg NAO",
    add_legend=False,
)
axes[0].set_title("")  # Remove xarray auto-generated title

# Daily NAO
sns.lineplot(
    data=NAO_merge,
    x="decade",
    y="days_pos",
    ax=axes[1],
    label="pos NAO",
    color="k",
    linewidth=1.5,
)
sns.lineplot(
    data=NAO_merge,
    x="decade",
    y="days_neg",
    ax=axes[1],
    label="neg NAO",
    color="k",
    linestyle="--",
    linewidth=1.5,
)

# wave breaking
sns.lineplot(
    data=awb_df[awb_df["isen_level"] == 335],
    x="decade",
    y="awb",
    ax=axes[2],
    label="anticyclonic 335K",
    color="#006E66",
    linewidth=1.5,
)
sns.lineplot(
    data=cwb_df[cwb_df["isen_level"] == 325],
    x="decade",
    y="cwb",
    ax=axes[2],
    label="cyclonic 325K",
    color="#006E66",
    linestyle="--",
    linewidth=1.5,
)


# momentum flux
sns.lineplot(
    data=steady_heat_scale_df,
    x="decade",
    y="thermal_feedback",
    ax=axes[3],
    label="thermal feedback",
    color="#FF514A",
    linestyle="-",
    linewidth=1.5,
)

# Adjust position of last row to reduce gap with row above
pos3 = axes[3].get_position()
pos2 = axes[2].get_position()
# Move axes[3] up by reducing the gap
new_bottom = pos2.y0 - pos3.height + 0.07  # 0.02 controls the gap size
axes[3].set_position([pos3.x0, new_bottom, pos3.width, pos3.height])

for i, ax in enumerate(axes):
    ax.spines["top"].set_visible(False)
    ax.set_facecolor("none")
    ax.set_ylabel("")
    # remove all ticks at x-axis except bottom plot
    if i % 2 == 0:
        ax.yaxis.set_label_position("left")
        ax.yaxis.tick_left()
        ax.spines["left"].set_visible(True)
        ax.spines["right"].set_visible(False)
        visible_spine = "left"
        # set color

    else:
        ax.yaxis.set_label_position("right")
        ax.yaxis.tick_right()
        ax.spines["right"].set_visible(True)
        ax.spines["left"].set_visible(False)
        visible_spine = "right"
    ax.spines["bottom"].set_visible(i == len(axes) - 1)
    if i != len(axes) - 1:
        # remove x ticks and labels on top three subplots
        ax.tick_params(
            axis="x", which="both", bottom=False, top=False, labelbottom=False
        )
    else:
        ax.tick_params(axis="x", which="both", bottom=True, top=False, labelbottom=True)
    ax.set_xlabel("")

    # color the visible y-axis to match the primary line on this axis
    lines = ax.get_lines()
    axis_color = lines[0].get_color() if len(lines) > 0 else "k"
    ax.spines[visible_spine].set_color(axis_color)
    ax.tick_params(axis="y", colors=axis_color)
    if ax.yaxis.get_label() is not None:
        ax.yaxis.label.set_color(axis_color)

    # add a, b, c, d labels
    axes[0].text(
        -0.05,
        1,
        "a",
        transform=axes[0].transAxes,
        fontsize=12,
        color="k",
        weight='bold',
    )
    axes[1].text(
        1.05,
        1.05,
        "b",
        transform=axes[1].transAxes,
        fontsize=12,
        color="k",
        weight='bold',
    )
    axes[2].text(
        -0.05,
        1,
        "c",
        transform=axes[2].transAxes,
        fontsize=12,
        color="k",
        weight='bold',
    )
    axes[3].text(
        1.05,
        1,
        "d",
        transform=axes[3].transAxes,
        fontsize=12,
        color="k",
        weight='bold',
    )

    # add legend
    axes[0].legend(
        loc="upper left",
        fontsize=8,
        frameon=False,
        ncol=2,
        bbox_to_anchor=(0, -0.1, 1, 1),
        labelcolor="k",
        title="Monthly NAO extremes",
        title_fontsize=8,
    )

    # add legend
    axes[1].legend(
        loc="upper left",
        fontsize=8,
        frameon=False,
        ncol=2,
        bbox_to_anchor=(0, 0, 1, 1),
        labelcolor="k",
        title="Daily NAO extremes",\
        title_fontsize=8,
    )

    # add legend
    axes[2].legend(
        loc="upper left",
        fontsize=8,
        frameon=False,
        ncol=1,
        bbox_to_anchor=(0, -0.3, 1, 1),
        labelcolor="#006E66",
        title="Wave breaking",
        title_fontsize=8,
    )

    axes[3].legend(
        loc="upper left",
        fontsize=8,
        frameon=False,
        ncol=1,
        bbox_to_anchor=(0, -0.3, 1, 1),
        labelcolor="#FF514A",
        title="Thermal feedback",
        title_fontsize=8,
    )

    # remove legend from axes[3]
    if axes[3].get_legend() is not None:
        axes[3].get_legend().remove()

    axes[0].set_ylabel(r"Frequency / months", fontsize=12)
    axes[1].set_ylabel(r"Frequency / days", fontsize=12)
    axes[2].set_ylabel(r"Frequency / days", fontsize=12)
    axes[3].set_ylabel(r"scaled standard deviations", fontsize=12)


plt.savefig(
    "/work/mh0033/m300883/High_frequecy_flow/docs/plots/0after_defense/GHG_forced_changes.pdf",
    dpi=500,
    bbox_inches="tight",
    metadata={"Creator": __file__},
    transparent=True,
)
# %%
