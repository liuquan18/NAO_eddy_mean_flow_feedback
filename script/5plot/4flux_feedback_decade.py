#%%
import xarray as xr
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.patches import Ellipse, Circle
from matplotlib.lines import Line2D
from matplotlib.ticker import FormatStrFormatter
import matplotlib.patheffects as pe
from src.data_helper.read_NAO_extremes import read_NAO_extremes

COLOR_POS = "#E57200"  # MPI orange
COLOR_NEG = "#006C66"  # MPI green


from src.data_helper import read_composite
import importlib
xr.set_options(use_numbagg=False)

importlib.reload(read_composite)

read_comp_var = read_composite.read_comp_var


# %%
MODEL_DIR = "MPI_GE_CMIP6_allplev"


def _read_all(var_name, suffix = '', name=None, phase = 'pos', chunks=None, method = 'mean', M2E_window = (-5, 20)
):
    """Read pos composites for all decades, concatenated along a 'decade' dimension.

    Returns an xarray object with a new 'decade' coordinate.
    """
    kwargs = dict(time_window="all", model_dir=MODEL_DIR)
    if name is not None:
        kwargs["name"] = name
    if chunks is not None:
        kwargs["chunks"] = chunks
    kwargs["comp_path"] = "0composite_alldec"
    kwargs["erase_zero_line"] = False
    kwargs["time_window"] = M2E_window
    kwargs["method"] = method
    decades = np.arange(1850, 2100, 10)
    datasets = [
        read_comp_var(var_name, phase, decade, suffix=suffix, **kwargs).assign_coords(decade=decade)
        for decade in decades
    ]
    # if plev.size is 1, dorp the plev dim
    if "plev" in datasets[0].dims and datasets[0].plev.size == 1:
        datasets = [ds.squeeze("plev", drop=True) for ds in datasets]
    return xr.concat(datasets, dim="decade")

def read_climatology(var,var_name = None):
    base_dir = "/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/0climatology_alldec/"
    file_path = base_dir + f"{var}.csv"
    df = pd.read_csv(file_path)
    if var_name is not None:
        df = df[['year', var_name]]
    # rename year to decade
    df = df.rename(columns={'year': 'decade'})
    df['decade'] = df['decade'] - 9
    return df

# ---- 1850s and 2090s composite ----

# %%
jet_loc_pos = _read_all("jetloc", name = 'lat', phase="pos")
# %%
awb_pos = _read_all("wb_anticyclonic_allisen", name = 'smooth_pv', phase="pos", method='sum')
# into percent
awb_pos = awb_pos / 15 # only sum over event
#%%
baroc_neg = _read_all("eady_growth_rate", name = 'eady_growth_rate', phase="neg")
baroc_neg = baroc_neg * 86400  # convert from 1/s to 1/day
#%%
blocking_neg = _read_all("zg_hat", name = 'zg', phase="neg")
blocking_neg = blocking_neg / 1000 # convert to km
# %%

jet_loc_pos_df = jet_loc_pos.to_dataframe("jet_lat").reset_index()
# drop plev if exists

awb_pos_df = awb_pos.to_dataframe("awb").reset_index()
baroc_neg_df = baroc_neg.to_dataframe("baroclinicity").reset_index()
blocking_neg_df = blocking_neg.to_dataframe("GB_index").reset_index()

if "plev" in jet_loc_pos_df.columns:
    jet_loc_pos_df = jet_loc_pos_df.drop(columns=["plev"])
if "plev" in awb_pos_df.columns:
    awb_pos_df = awb_pos_df.drop(columns=["plev"])
if "plev" in baroc_neg_df.columns:
    baroc_neg_df = baroc_neg_df.drop(columns=["plev"])
if "plev" in blocking_neg_df.columns:
    blocking_neg_df = blocking_neg_df.drop(columns=["plev"])
#%%

dec_pos_df = awb_pos_df.merge(jet_loc_pos_df, on = ['decade'])
dec_neg_df = baroc_neg_df.merge(blocking_neg_df, on = ['decade'])


#%%

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


NAO_monthly_extremes = read_extrc("MPI_GE_CMIP6", fixed_pattern="decade_mpi")
NAO_monthly_extremes['time'] = NAO_monthly_extremes['time'].dt.year

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


NAO_pos_count, NAO_neg_count = NAO_extremes(False, 7)
NAO_pos_days, NAO_neg_days = NAO_extremes(True, 7)

NAO_pos_days = NAO_pos_days.rename(columns={"count": "days"})
NAO_neg_days = NAO_neg_days.rename(columns={"count": "days"})

NAO_count_merge = pd.merge(
    NAO_pos_count, NAO_neg_count, on="decade", suffixes=("_pos", "_neg")
)
NAO_days_merge = pd.merge(
    NAO_pos_days, NAO_neg_days, on="decade", suffixes=("_pos", "_neg")
)
NAO_merge = pd.merge(NAO_count_merge, NAO_days_merge, on="decade")

NAO_merge["decade"] = NAO_merge["decade"].astype(int)
#%%
dec_pos_df = dec_pos_df.merge(NAO_merge[["decade", "days_pos"]], on="decade")
dec_neg_df = dec_neg_df.merge(NAO_merge[["decade", "days_neg"]], on="decade")


#%%
ratio_pos = pd.read_csv("/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/0climatology_alldec/ratio_pos.csv")
ratio_neg = pd.read_csv("/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/0climatology_alldec/ratio_neg.csv")

#%%
ratio_pos['awb_dec'] = ratio_pos['awb_dec'] / 50
#%%
fig, axes = plt.subplots(3, 2, figsize=(9, 13), gridspec_kw={"height_ratios": [1, 1.25, 1]})
fig.subplots_adjust(bottom=0.18, wspace=0.5, hspace=0.25)

# Monthly NAO extremes
ln = NAO_monthly_extremes.sel(extr_type="pos", mode="NAO", confidence="true").plot.line(
    ax=axes[0, 0],
    x="time",
    color="k",
    linewidth=1.5,
    label="pos NAO",
    add_legend=True,
)

NAO_monthly_extremes.sel(extr_type="neg", mode="NAO", confidence="true").plot.line(
    ax=axes[0, 0],
    x="time",
    color="k",
    linewidth=1.5,
    linestyle="--",
    label="neg NAO",
    add_legend=True,
)
axes[0, 0].set_title("")  # Remove xarray auto-generated title
# add legend with custom labels
handles = [
    Line2D([0], [0], color="k", linewidth=1.5, label="pos NAO"),
    Line2D([0], [0], color="k", linewidth=1.5, linestyle="--", label="neg NAO"),
]
axes[0, 0].legend(handles=handles, loc="upper left")


# Daily NAO
sns.lineplot(
    data=NAO_merge,
    x="decade",
    y="days_pos",
    ax=axes[0, 1],
    label="pos NAO",
    color="k",
    linewidth=1.5,
)
sns.lineplot(
    data=NAO_merge,
    x="decade",
    y="days_neg",
    ax=axes[0, 1],
    label="neg NAO",
    color="k",
    linestyle="--",
    linewidth=1.5,
)

# ===== Row 1: Scatter panels (was Row 2) =====
# shared size scale so pos/neg panels and the size legend use identical, matching areas
_size_vmin = min(dec_pos_df["days_pos"].min(), dec_neg_df["days_neg"].min())
_size_vmax = max(dec_pos_df["days_pos"].max(), dec_neg_df["days_neg"].max())

sns.scatterplot(
    data=dec_pos_df,
    x="awb",
    y="jet_lat",
    ax=axes[1, 0],
    hue="decade",
    size="days_pos",
    sizes=(20, 400),
    size_norm=(_size_vmin, _size_vmax),
    palette="Oranges",
    legend=False,
)

sns.scatterplot(
    data=dec_neg_df,
    x="GB_index",
    y="baroclinicity",
    ax=axes[1, 1],
    hue="decade",
    size="days_neg",
    sizes=(20, 400),
    size_norm=(_size_vmin, _size_vmax),
    palette="GnBu",
    legend=False,
)

# ===== Row 2: Climatological ratio / change panels (was Row 1) =====
# Left y-axis (main): bar plot; right y-axis (twinx): line plot
axes[2, 0].bar(
    ratio_pos["decade"], ratio_pos["awb_dec"],
    width=8, color=COLOR_POS, alpha=0.45, zorder=2,
)
axes[2, 0].set_ylim(450, 700)

ax1_line = axes[2, 0].twinx()
ax1_line.spines["top"].set_visible(False)

_n0 = len(ax1_line.lines)
sns.lineplot(
    data=ratio_pos, x="decade", y="awb_ratio",
    color=COLOR_POS, linewidth=2.5, ax=ax1_line,
)
for _l in ax1_line.lines[_n0:]:
    _l.set_path_effects([
        pe.Stroke(linewidth=5, foreground="white"),
        pe.Normal(),
    ])

# Right panel: left y-axis (main): bar plot; right y-axis (twinx): line plot
axes[2, 1].bar(
    ratio_neg["decade"], ratio_neg["baroclinicity_dec"],
    width=8, color=COLOR_NEG, alpha=0.45, zorder=2,
)
axes[2, 1].set_ylim(3.39, 3.6)

ax2_line = axes[2, 1].twinx()
ax2_line.spines["top"].set_visible(False)

_n1 = len(ax2_line.lines)
sns.lineplot(
    data=ratio_neg, x="decade", y="baroclinicity_ratio",
    color=COLOR_NEG, linewidth=2.5, ax=ax2_line,
)
for _l in ax2_line.lines[_n1:]:
    _l.set_path_effects([
        pe.Stroke(linewidth=5, foreground="white"),
        pe.Normal(),
    ])

# remove upper and right spines
for ax in axes.flatten():
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
for ax in [ax1_line, ax2_line]:
    ax.spines['top'].set_visible(False)

# Panel labels a-f
axes[0, 0].text(-0.08, 1.1, "a", transform=axes[0, 0].transAxes,
                ha="left", va="top", fontsize=12, fontweight="bold")
axes[0, 1].text(-0.08, 1.1, "b", transform=axes[0, 1].transAxes,
                ha="left", va="top", fontsize=12, fontweight="bold")
axes[1, 0].text(-0.08, 1.1, "c", transform=axes[1, 0].transAxes,
                ha="left", va="top", fontsize=12, fontweight="bold")
axes[1, 1].text(-0.08, 1.1, "d", transform=axes[1, 1].transAxes,
                ha="left", va="top", fontsize=12, fontweight="bold")
axes[2, 0].text(-0.08, 1.1, "e", transform=axes[2, 0].transAxes,
                ha="left", va="top", fontsize=12, fontweight="bold")
axes[2, 1].text(-0.08, 1.1, "f", transform=axes[2, 1].transAxes,
                ha="left", va="top", fontsize=12, fontweight="bold")

axes[0, 0].set_xlabel("Year")
axes[0, 0].set_ylabel("Extreme NAO months / decade $^{-1}$")
axes[0, 1].set_xlabel("Decade")
axes[0, 1].set_ylabel("Extreme NAO days / decade $^{-1}$")

axes[1, 0].set_ylabel("Jet Latitude (°N)")
axes[1, 0].set_xlabel("AWB occurrence / day")
axes[1, 1].set_xlabel("GB Index / km")
axes[1, 1].set_ylabel("Eady growth rate / $day^{-1}$")
axes[1, 1].xaxis.set_major_formatter(FormatStrFormatter("%.1f"))
# axes[1, 0].set_xlim(5.7, 6.8)

axes[2, 0].set_xlabel("Decade")
axes[2, 0].set_ylabel("AWB occurrence / day")
ax1_line.set_ylabel("AWB ratio")

axes[2, 1].set_xlabel("Decade")
axes[2, 1].set_ylabel("Eady growth rate / $day^{-1}$")
ax2_line.set_ylabel("Baroclinicity ratio")


# ===== Per-column decade colorbars (thin, matching each scatter panel's palette) =====
decades_all = NAO_merge["decade"].values
_dec_norm = mpl.colors.Normalize(vmin=decades_all.min(), vmax=decades_all.max())

_sm_pos = mpl.cm.ScalarMappable(norm=_dec_norm, cmap="Oranges")
_sm_pos.set_array([])
_cbar_pos = fig.colorbar(_sm_pos, ax=axes[1, 0], orientation="horizontal", location="bottom",
                         fraction=0.035, shrink=0.95, pad=0.2, aspect=30)
_cbar_pos.set_label("Decade", fontsize=8.5, style="italic")
_cbar_pos.ax.tick_params(labelsize=7)

_sm_neg = mpl.cm.ScalarMappable(norm=_dec_norm, cmap="GnBu")
_sm_neg.set_array([])
_cbar_neg = fig.colorbar(_sm_neg, ax=axes[1, 1], orientation="horizontal", location="bottom",
                         fraction=0.035, shrink=0.95, pad=0.2, aspect=30)
_cbar_neg.set_label("Decade", fontsize=8.5, style="italic")
_cbar_neg.ax.tick_params(labelsize=7)

# --- size legend: real scatter markers so areas exactly match the panels (shared size_norm) ---
_orange = sns.color_palette("Oranges", 10)[6]
_blue = sns.color_palette("GnBu", 10)[7]
_ref_days = [25, 35, 45]


def _bubble_size_legend(ax, color, bbox, title):
    lax = ax.inset_axes(bbox)
    lax.set_xlim(0, 1)
    lax.set_ylim(0, 1)
    lax.axis("off")
    lax.patch.set_alpha(0)

    xs = [0.25, 0.45, 0.75]
    y = 0.55
    for x, v in zip(xs, _ref_days):
        s = 20 + (v - _size_vmin) / (_size_vmax - _size_vmin) * (400 - 20)  # matches sns sizes=(20, 400)
        lax.scatter(x, y, s=s, facecolors="none", edgecolors=color, linewidths=1.2, clip_on=False)
        lax.text(x, 0.3, f"{v}", fontsize=6.5, ha="center", va="bottom")
    lax.text(0.52, 0.95, title, fontsize=7, style="italic", ha="center", va="top")
    return lax


_bubble_size_legend(axes[1, 0], _orange, [0.03, 0.48, 0.42, 0.48], 'pos NAO extremes/day')
_bubble_size_legend(axes[1, 1], _blue, [0.55, 0.48, 0.42, 0.48], 'neg NAO extremes/day')


# plt.tight_layout()
plt.savefig("/work/mh0033/m300883/High_frequecy_flow/docs/plots/0after_defense/decade_scatter.pdf", dpi=300, bbox_inches='tight')
# %%
