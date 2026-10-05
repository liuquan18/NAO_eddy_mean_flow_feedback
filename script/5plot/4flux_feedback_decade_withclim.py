#%%
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.patches import Ellipse
from matplotlib.lines import Line2D
from matplotlib.ticker import FormatStrFormatter
from scipy import stats
from src.data_helper.read_NAO_extremes import read_NAO_extremes


from src.data_helper import read_composite
import importlib
xr.set_options(use_numbagg=False)

importlib.reload(read_composite)

read_comp_var = read_composite.read_comp_var


# %%
MODEL_DIR = "MPI_GE_CMIP6_allplev"


def _read_all(var_name, suffix = '', name=None, phase = 'pos', chunks=None, method = 'mean', M2E_window = (5, 20)
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
#%%
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

# %%
jet_loc_pos = _read_all("jetloc", name = 'lat', phase="pos")

# %%
awb_pos = _read_all("wb_anticyclonic_allisen", name = 'smooth_pv', phase="pos", method='mean')
# into percent
awb_pos = awb_pos *100 # percent

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
jet_loc_clim = read_climatology("jet_latitude", 'lat')

awb_clim = read_climatology("awb_index", "smooth_pv")
awb_clim['smooth_pv'] = awb_clim['smooth_pv'] * 100 # percent

baroc_clim = read_climatology("baroclinicity", "eady_growth_rate")
baroc_clim['eady_growth_rate'] = baroc_clim['eady_growth_rate'] * 86400 # convert from 1/s to 1/day

GB_clim = read_climatology("GB_index", "zg")
GB_clim['zg'] = GB_clim['zg'] / 1000 # convert to km


clim_pos_df = awb_clim.merge(jet_loc_clim, on = ['decade'])
clim_neg_df = baroc_clim.merge(GB_clim, on = ['decade'])


clim_pos_df = clim_pos_df.rename(columns={'smooth_pv': 'awb', 'lat': 'jet_lat'})
clim_neg_df = clim_neg_df.rename(columns={'eady_growth_rate': 'baroclinicity', 'zg': 'GB_index'})

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
# ===== Difference plot: second row shows (NAO composite - climatology) =====

# Compute difference dataframes
_ratio_pos = dec_pos_df.merge(clim_pos_df, on='decade', suffixes=('_dec', '_clim'))
_ratio_pos['awb_ratio'] = _ratio_pos['awb_dec'] / _ratio_pos['awb_clim']
_ratio_pos['jet_lat_ratio'] = _ratio_pos['jet_lat_dec'] / _ratio_pos['jet_lat_clim']
_ratio_pos['days_pos'] = _ratio_pos['days_pos']

_ratio_neg = dec_neg_df.merge(clim_neg_df, on='decade', suffixes=('_dec', '_clim'))
_ratio_neg['baroclinicity_ratio'] = _ratio_neg['baroclinicity_dec'] / _ratio_neg['baroclinicity_clim']
_ratio_neg['GB_index_ratio'] = _ratio_neg['GB_index_dec'] / _ratio_neg['GB_index_clim']
_ratio_neg['days_neg'] = _ratio_neg['days_neg']

#%%
fig, axes = plt.subplots(2, 2, figsize=(8, 9))
fig.subplots_adjust(bottom=0.2, wspace=0.35, hspace=0.35)


sns.scatterplot(
    data=dec_pos_df,
    x="awb",
    y="jet_lat",
    ax=axes[0, 0],
    hue="decade",
    size = "days_pos",
    sizes = (20, 400),
    palette = "Oranges",
    legend=False,
)
# add climatology scatter point
sns.scatterplot(
    data=clim_pos_df,
    x="awb",
    y="jet_lat",
    ax=axes[0, 0],
    hue = "decade",
    sizes = (20, 400),
    palette = "Oranges",
    legend=False,
    marker = "X",
)

sns.scatterplot(
    data=dec_neg_df,
    x="GB_index",
    y="baroclinicity",
    ax=axes[0, 1],
    hue="decade",
    size = "days_neg",
    sizes = (20, 400),
    palette = "GnBu",
    legend=False,
)

# add climatology scatter point
sns.scatterplot(
    data=clim_neg_df,
    x="GB_index",
    y="baroclinicity",
    ax=axes[0, 1],
    hue = "decade",
    sizes = (20, 400),
    palette = "GnBu",
    legend=False,
    marker = "X",

)



# --- ratio scatter plots ---
sns.scatterplot(
    data=_ratio_pos, x="awb_ratio", y="jet_lat_ratio", ax=axes[1, 0],
    hue="decade", size="days_pos", sizes=(20, 400), palette="Oranges", legend=False, marker = "^"
)
sns.scatterplot(
    data=_ratio_neg, x="GB_index_ratio", y="baroclinicity_ratio", ax=axes[1, 1],
    hue="decade", size="days_neg", sizes=(20, 400), palette="GnBu", legend=False, marker = "v"
)


# Add legends to scatter panels
_orange = sns.color_palette("Oranges", 10)[6]
axes[0, 0].legend(
    handles=[
        Line2D([0], [0], marker='o', color='w', markerfacecolor=_orange, markersize=8, label='pos NAO'),
        Line2D([0], [0], marker='X', color='w', markerfacecolor=_orange, markersize=8, label='climatology'),
        Line2D([0], [0], marker='^', color='w', markerfacecolor=_orange, markersize=8, label='ratio'),
    ],
    loc='upper left',
)

_blue = sns.color_palette("GnBu", 10)[7]
axes[0, 1].legend(
    handles=[
        Line2D([0], [0], marker='o', color='w', markerfacecolor=_blue, markersize=8, label='neg NAO'),
        Line2D([0], [0], marker='X', color='w', markerfacecolor=_blue, markersize=8, label='climatology'),
        Line2D([0], [0], marker='v', color='w', markerfacecolor=_blue, markersize=8, label='ratio'),
    ],
    loc='best',
)

# remove upper and right spines
for ax in axes.flatten():
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    # add a, b, c, d labels to the corners
axes[0, 0].text(-0.08, 1.1, "a", transform=axes[0, 0].transAxes,
                ha="left", va="top", fontsize=12, fontweight="bold")
axes[0, 1].text(-0.08, 1.1, "b", transform=axes[0, 1].transAxes,
                ha="left", va="top", fontsize=12, fontweight="bold")
axes[1, 0].text(-0.08, 1.1, "c", transform=axes[1, 0].transAxes,
                ha="left", va="top", fontsize=12, fontweight="bold")
axes[1, 1].text(-0.08, 1.1, "d", transform=axes[1, 1].transAxes,
                ha="left", va="top", fontsize=12, fontweight="bold")



axes[0, 0].set_ylabel("Jet Latitude (°N)")
axes[0, 0].set_xlabel("AWB occurrence / $\%$")
axes[0, 1].set_xlabel("GB Index / km")
axes[0, 1].set_ylabel("Eady growth rate / $day^{-1}$")
axes[0, 1].xaxis.set_major_formatter(FormatStrFormatter("%.1f"))

axes[1, 0].set_ylabel("Jet Latitude ratio")
axes[1, 0].set_xlabel("AWB ratio")
axes[1, 1].set_xlabel("GB Index ratio")
axes[1, 1].set_ylabel("Eady growth rate ratio")

# ===== Combined bubble-colorband legend =====
# Left panel: colored blocks + bubbles for every decade
# Right panel: reference scale for bubble size (NAO days)

decades_all = NAO_merge["decade"].values
_colors = sns.color_palette("Greys", n_colors=len(decades_all))
# --- size scaling (match seaborn sizes=(20,300)) ---
_days_pos_dec = NAO_merge.set_index("decade")["days_pos"].reindex(decades_all.astype(int)).values
_days_neg_dec = NAO_merge.set_index("decade")["days_neg"].reindex(decades_all.astype(int)).values
_days_avg = (_days_pos_dec + _days_neg_dec) / 2
_s_vmin, _s_vmax = _days_avg.min(), _days_avg.max()
def _msize(v):
    return 20 + (v - _s_vmin) / (_s_vmax - _s_vmin) * (300 - 20)

# --- colorband axis (color + decade labels only) ---
_grey_colors = sns.color_palette('Greys', n_colors=len(decades_all))

leg_ax = fig.add_axes([0.09, 0.04, 0.7, 0.08])
leg_ax.set_xlim(1843, 2097)
leg_ax.set_ylim(-1.5, 1.2)
leg_ax.axis("off")

# draw colored band (rectangles)
_band_y, _band_h = 0.0, 0.8
for i, dec in enumerate(decades_all):
    leg_ax.add_patch(
        plt.Rectangle((dec - 5, _band_y), 10, _band_h,
                      color=_colors[i], zorder=3, clip_on=False)
    )
# outer border around the entire colorband
leg_ax.add_patch(
    plt.Rectangle((1845, _band_y), 250, _band_h,
                  fill=False, edgecolor='black', linewidth=0.5, zorder=100, clip_on=False)
)

# decade labels below band (every other decade)
for dec in decades_all[::2]:
    leg_ax.text(dec, _band_y - 0.15, str(int(dec)),
                ha="center", va="top", fontsize=7, rotation=45)

leg_ax.text(0.5, 1.15, "Decade",
            ha="center", va="top", transform=leg_ax.transAxes,
            fontsize=8.5, style="italic")

# --- size reference axis (right) ---
ref_ax = fig.add_axes([0.80, 0.04, 0.16, 0.08])
ref_ax.set_xlim(-0.5, 3.5)
ref_ax.set_ylim(-1.5, 1.2)
ref_ax.axis("off")

_ref_days = [round(_s_vmin), round((_s_vmin + _s_vmax) / 2), round(_s_vmax)]
for j, rd in enumerate(_ref_days):
    ref_ax.scatter(j * 1.1, 0.4, s=_msize(rd), color="grey",
                   edgecolors="white", linewidths=0.4, clip_on=False)
    ref_ax.text(j * 1.1, _band_y - 0.15, str(rd),
                ha="center", va="top", fontsize=7)
ref_ax.text(0.4, 1.15, "NAO extremes/day",
            ha="center", va="top", transform=ref_ax.transAxes,
            fontsize=8.5, style="italic")


# plt.tight_layout()
plt.savefig("/work/mh0033/m300883/High_frequecy_flow/docs/plots/0after_defense/decade_scatter_ratio.pdf", dpi=300, bbox_inches='tight')

# %%

#%%
clim_pos_ano_df = clim_pos_df
clim_pos_ano_df['awb'] = clim_pos_ano_df['awb'] - clim_pos_ano_df[clim_pos_ano_df['decade'] == 1850]['awb'].values[0]
clim_pos_ano_df['jet_lat'] = clim_pos_ano_df['jet_lat'] - clim_pos_ano_df[clim_pos_ano_df['decade'] == 1850]['jet_lat'].values[0]

dec_pos_ano_df = dec_pos_df
dec_pos_ano_df['awb'] = dec_pos_ano_df['awb'] - dec_pos_ano_df[dec_pos_ano_df['decade'] == 1850]['awb'].values[0]
dec_pos_ano_df['jet_lat'] = dec_pos_ano_df['jet_lat'] - dec_pos_ano_df[dec_pos_ano_df['decade'] == 1850]['jet_lat'].values[0]
# %%
clim_neg_ano_df = clim_neg_df
clim_neg_ano_df['baroclinicity'] = clim_neg_ano_df['baroclinicity'] - clim_neg_ano_df[clim_neg_ano_df['decade'] == 1850]['baroclinicity'].values[0]
clim_neg_ano_df['GB_index'] = clim_neg_ano_df['GB_index'] - clim_neg_ano_df[clim_neg_ano_df['decade'] == 1850]['GB_index'].values[0]

dec_neg_ano_df = dec_neg_df
dec_neg_ano_df['baroclinicity'] = dec_neg_ano_df['baroclinicity'] - dec_neg_ano_df[dec_neg_ano_df['decade'] == 1850]['baroclinicity'].values[0]
dec_neg_ano_df['GB_index'] = dec_neg_ano_df['GB_index'] - dec_neg_ano_df[dec_neg_ano_df['decade'] == 1850]['GB_index'].values[0]
# %%
                                                                                                               
fig3, axes3 = plt.subplots(1, 2, figsize=(9, 5))
fig3.subplots_adjust(bottom=0.25, wspace=0.35)

sns.scatterplot(
    data=dec_pos_ano_df,
    x="awb",
    y="jet_lat",
    ax=axes3[0],
    hue="decade",
    size = "days_pos",
    sizes = (20, 400),
    palette = "Oranges",
    legend=False,
)
# add climatology scatter point
sns.scatterplot(
    data=clim_pos_ano_df,
    x="awb",
    y="jet_lat",
    ax=axes3[0],
    hue = "decade",
    sizes = (20, 400),
    palette = "Oranges",
    legend=False,
    marker = "X",
)

sns.scatterplot(
    data=dec_neg_ano_df,
    x="GB_index",
    y="baroclinicity",
    ax=axes3[1],
    hue="decade",
    size = "days_neg",
    sizes = (20, 400),
    palette = "GnBu",
    legend=False,
)

# add climatology scatter point
sns.scatterplot(
    data=clim_neg_ano_df,
    x="GB_index",
    y="baroclinicity",
    ax=axes3[1],
    hue = "decade",
    sizes = (20, 400),
    palette = "GnBu",
    legend=False,
    marker = "X",
)

# Legends
_orange = sns.color_palette("Oranges", 10)[6]
axes3[0].legend(
    handles=[
        Line2D([0], [0], marker='o', color='w', markerfacecolor=_orange, markersize=8, label='pos NAO'),
        Line2D([0], [0], marker='X', color='w', markerfacecolor=_orange, markersize=8, label='climatology'),
    ],
    loc='upper left',
)

_blue = sns.color_palette("GnBu", 10)[7]
axes3[1].legend(
    handles=[
        Line2D([0], [0], marker='o', color='w', markerfacecolor=_blue, markersize=8, label='neg NAO'),
        Line2D([0], [0], marker='X', color='w', markerfacecolor=_blue, markersize=8, label='climatology'),
    ],
    loc='best',
)

# Spines and panel labels
for ax in axes3.flatten():
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
for ax, lbl in zip(axes3, ['a', 'b']):
    ax.text(-0.08, 1.1, lbl, transform=ax.transAxes,
            ha="left", va="top", fontsize=12, fontweight="bold")


axes3[0].set_ylabel("$\Delta$ Jet Latitude (°N)")
axes3[0].set_xlabel("$\Delta$ AWB occurrence / $\%$")
axes3[1].set_xlabel("$\Delta$ GB Index / km")
axes3[1].set_ylabel("$\Delta$ Eady growth rate / $day^{-1}$")


# %%
