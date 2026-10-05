# %%
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats

from src.data_helper import read_composite
import importlib


importlib.reload(read_composite)

read_EP_flux = read_composite.read_EP_flux
read_E_div = read_composite.read_E_div
read_comp_var = read_composite.read_comp_var


# %%
MODEL_DIR = "MPI_GE_CMIP6_allplev"


def _read_all(var_name, suffix = '', name=None, method="no_stat", phase = 'pos', chunks=None):
    """Read pos composites for all decades, concatenated along a 'decade' dimension.

    Returns an xarray object with a new 'decade' coordinate.
    """
    kwargs = dict(time_window="all", model_dir=MODEL_DIR)
    if method is not None:
        kwargs["method"] = method
    if name is not None:
        kwargs["name"] = name
    if chunks is not None:
        kwargs["chunks"] = chunks
    kwargs["comp_path"] = "0composite_alldec"
    kwargs["erase_zero_line"] = False
    decades = np.arange(1850, 2100, 10)
    datasets = [
        read_comp_var(var_name, phase, decade, suffix=suffix, **kwargs).assign_coords(decade=decade)
        for decade in decades
    ]
    # if plev.size is 1, dorp the plev dim
    if "plev" in datasets[0].dims and datasets[0].plev.size == 1:
        datasets = [ds.squeeze("plev", drop=True) for ds in datasets]
    return xr.concat(datasets, dim="event")


# ---- regression slope at each time step ----
def regression_slope_timeseries(jl, awb, decade_sel=None, window=10, standardize=True):
    """
    For each time step compute the OLS slope of awb ~ jet_lat across all events.

    Parameters
    ----------
    jl : DataArray (event, time)
    awb : DataArray (event, time)
    decade_sel : int or None  – filter to a single decade; None = all decades
    y_agg : 'sum' or 'mean'  – rolling aggregation for the y variable
    standardize : bool  – if True, z-score both variables before regression so
                          the slope equals the Pearson correlation coefficient
    """
    jl = jl.rolling(time=window, center=True).mean()
    awb = awb.rolling(time=window, center=True).mean()
    
    if decade_sel is not None:
        mask = jl.decade == decade_sel
        jl  = jl.where(mask, drop=True)
        awb = awb.where(mask, drop=True)
    
    times = jl.time.values
    slopes  = np.full(len(times), np.nan)
    ci_low  = np.full(len(times), np.nan)
    ci_high = np.full(len(times), np.nan)
    
    for i, t in enumerate(times):
        df = pd.DataFrame({
            'x': jl.sel(time=t).values.flatten(),
            'y': awb.sel(time=t).values.flatten(),
        }).dropna()
        if len(df) < 4:
            continue
        if standardize:
            x = (df['x'] - df['x'].mean()) / df['x'].std()
            y = (df['y'] - df['y'].mean()) / df['y'].std()
        else:
            x, y = df['x'], df['y']
        res = stats.linregress(x, y)
        slopes[i] = res.slope
        # 95 % CI:  slope ± t_{0.025, n-2} * stderr
        t_crit = stats.t.ppf(0.975, df=len(df) - 2)
        ci_low[i]  = res.slope - t_crit * res.stderr
        ci_high[i] = res.slope + t_crit * res.stderr
    
    return times, slopes, ci_low, ci_high


def compute_jpdf(df, x_col, y_col, x_bins, y_bins):
    """2D histogram normalized so the peak bin = 1 (relative probability density)."""
    H, _, _ = np.histogram2d(df[x_col], df[y_col], bins=[x_bins, y_bins], density=True)
    H = H.T
    if H.max() > 0:
        H = H / H.max()
    return np.ma.masked_where(H == 0, H)

# %%
jet_loc_pos = _read_all("jetloc", name = 'lat', method="no_stat", phase="pos")
# %%
awb_pos = _read_all("wb_anticyclonic_allisen", name = 'smooth_pv', method="no_stat", phase="pos")
# into percent
awb_pos = awb_pos * 100
#%%
baroc_neg = _read_all("eady_growth_rate", name = 'eady_growth_rate', method="no_stat", phase="neg")
baroc_neg = baroc_neg * 86400  # convert from 1/s to 1/day
#%%
blocking_neg = _read_all("zg_hat", name = 'zg', method="no_stat", phase="neg")
blocking_neg = blocking_neg / 1000 # convert to km
# %%
E2M_window = slice(-4, 5)  # 10 days, matching the rolling window used for slopes_pos/neg
M2E_window = slice(10, 20)

#%%
# ---- Positive phase: E2M and M2E windows ----
jet_loc_pos_E2M = jet_loc_pos.sel(time = E2M_window).mean(dim = 'time')
awb_pos_E2M = awb_pos.sel(time = E2M_window).mean(dim = 'time')
# 
jet_loc_pos_M2E = jet_loc_pos.sel(time = M2E_window).mean(dim = 'time')
awb_pos_M2E = awb_pos.sel(time = M2E_window).mean(dim = 'time')
# 
jet_loc_E2M_df = jet_loc_pos_E2M.to_dataframe().reset_index()
awb_E2M_df = awb_pos_E2M.to_dataframe('awb').reset_index()
# 
jet_loc_M2E_df = jet_loc_pos_M2E.to_dataframe().reset_index()
awb_M2E_df = awb_pos_M2E.to_dataframe('awb').reset_index()
#
E2M_pos_df = pd.merge(jet_loc_E2M_df, awb_E2M_df, on=['event', 'decade'])
M2E_pos_df = pd.merge(jet_loc_M2E_df, awb_M2E_df, on=['event', 'decade'])

#%%
# ---- Negative phase: E2M and M2E windows ----
blocking_neg_E2M = blocking_neg.sel(time = E2M_window).mean(dim = 'time')
baroc_neg_E2M    = baroc_neg.sel(time = E2M_window).mean(dim = 'time')

blocking_neg_M2E = blocking_neg.sel(time = M2E_window).mean(dim = 'time')
baroc_neg_M2E    = baroc_neg.sel(time = M2E_window).mean(dim = 'time')

blocking_E2M_df = blocking_neg_E2M.to_dataframe().reset_index()
baroc_E2M_df    = baroc_neg_E2M.to_dataframe().reset_index()

blocking_M2E_df = blocking_neg_M2E.to_dataframe().reset_index()
baroc_M2E_df    = baroc_neg_M2E.to_dataframe().reset_index()

E2M_neg_df = pd.merge(blocking_E2M_df, baroc_E2M_df, on=['event', 'decade'])
M2E_neg_df = pd.merge(blocking_M2E_df, baroc_M2E_df, on=['event', 'decade'])

#%%
times_pos, slopes_pos, ci_low_pos, ci_high_pos = regression_slope_timeseries(awb_pos, jet_loc_pos)
times_neg, slopes_neg, ci_low_neg, ci_high_neg = regression_slope_timeseries(blocking_neg, baroc_neg)

# %%

# --- Bin edges for positive phase ---
x_bins_pos = np.linspace(0, max(E2M_pos_df['awb'].max(), M2E_pos_df['awb'].max()), 150)
y_bins_pos = np.linspace(E2M_pos_df['lat'].min(), E2M_pos_df['lat'].max(), 60)
x_centers = (x_bins_pos[:-1] + x_bins_pos[1:]) / 2
y_centers = (y_bins_pos[:-1] + y_bins_pos[1:]) / 2
X, Y = np.meshgrid(x_centers, y_centers)

# Compute both JPDFs and find shared color range (positive)
H_E2M = compute_jpdf(E2M_pos_df, 'awb', 'lat', x_bins_pos, y_bins_pos)
H_M2E = compute_jpdf(M2E_pos_df, 'awb', 'lat', x_bins_pos, y_bins_pos)

# --- Bin edges for negative phase (blocking vs baroc) ---
x_bins_neg = np.linspace(
    min(E2M_neg_df['zg'].min(), M2E_neg_df['zg'].min()),
    max(E2M_neg_df['zg'].max(), M2E_neg_df['zg'].max()), 100)
y_bins_neg = np.linspace(
    min(E2M_neg_df['eady_growth_rate'].min(), M2E_neg_df['eady_growth_rate'].min()),
    max(E2M_neg_df['eady_growth_rate'].max(), M2E_neg_df['eady_growth_rate'].max()), 100)
x_centers_neg = (x_bins_neg[:-1] + x_bins_neg[1:]) / 2
y_centers_neg = (y_bins_neg[:-1] + y_bins_neg[1:]) / 2
X_neg, Y_neg = np.meshgrid(x_centers_neg, y_centers_neg)

# Compute both JPDFs and find shared color range (negative)
H_E2M_neg = compute_jpdf(E2M_neg_df, 'zg', 'eady_growth_rate', x_bins_neg, y_bins_neg)
H_M2E_neg = compute_jpdf(M2E_neg_df, 'zg', 'eady_growth_rate', x_bins_neg, y_bins_neg)

#%%
fill_levels    = np.logspace(-2, -0.1, 30)
contour_levels = fill_levels[18::4]

#%%
# --- Two-row figure: row 1 = NAO+, row 2 = NAO- ---
fig, (ax_slope_pos, ax_slope_neg) = plt.subplots(2, 1, figsize=(10, 9))

decade_colors = {1850: 'purple', 2090: 'gold'}

# ---- Row 1: Positive phase (jet_loc vs AWB) ----

ax_slope_pos.plot(times_pos, slopes_pos, color='k', linewidth=1.5, zorder = 100)
ax_slope_pos.fill_between(times_pos, ci_low_pos, ci_high_pos, color='k', alpha=0.15, zorder = 100)
ax_slope_pos.axvline(0, color='gray', linewidth=0.7, linestyle=':')
ax_slope_pos.axvline(15, color='gray', linewidth=0.7, linestyle=':')
# mark the value on the line at day 0/15
for _t in (0, 15):
    _y = slopes_pos[np.argmin(np.abs(times_pos - _t))]
    ax_slope_pos.plot(_t, _y, marker='o', markerfacecolor='none', markeredgecolor='k', markersize=6, zorder=101)
ax_slope_pos.set_xlabel('days relative to event onset')
ax_slope_pos.set_ylabel('Pearson correlation coefficient')
ax_slope_pos.set_ylim(0.42, 0.58)
ax_slope_pos.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.2f}'))
ax_slope_pos.set_xlim(-5, 20)
# remove upper and right spines
ax_slope_pos.spines['top'].set_visible(False)
ax_slope_pos.spines['right'].set_visible(False)
ax_slope_pos.spines['bottom'].set_visible(False)
# no x-ticks and tick labels on the upper plot
ax_slope_pos.tick_params(bottom=False, labelbottom=False, labelsize=10)
ax_slope_pos.set_xlabel('')  # remove x-axis label for the upper plot
ax_slope_pos.text(-0.0, 1.05, 'a', transform=ax_slope_pos.transAxes, fontsize=11,
                  fontweight='bold', va='top', ha='right')

# JPDF insets for positive phase
ax0 = ax_slope_pos.inset_axes([0.05, 0.56, 0.40, 0.44])   # upper left
ax1 = ax_slope_pos.inset_axes([0.55, 0.05, 0.40, 0.44])    # bottom right

for idx, (ax, H, label, df) in enumerate(zip([ax0, ax1], [H_E2M, H_M2E], ['ai', 'aii'], [E2M_pos_df, M2E_pos_df])):
    pcm = ax.contourf(X, Y, H, cmap='YlOrBr', levels=fill_levels,  extend='max')
    # pcl = ax.contour(X, Y, H, levels=contour_levels, colors='k', linewidths=0.5)
    ax.set_xlabel(r'awb / $\%$', fontsize=10)
    ax.set_ylabel(r'jet lat / $\degree$ N', fontsize=10)
    ax.set_xlim(0., 18)
    ax.tick_params(labelsize=10)
    ax.spines['top'].set_visible(False)
    ax.yaxis.set_label_position('right')
    ax.yaxis.tick_right()
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(True)
    ax.text(1.0, 1.1, label, transform=ax.transAxes, fontsize=10,
            fontweight='bold', va='top', ha='right')
    # linear regression line (standardized: slope = Pearson r, converted to data coords)
    _fit_df = df[['lat', 'awb']].dropna()
    _x_std = (_fit_df['awb'] - _fit_df['awb'].mean()) / _fit_df['awb'].std()
    _y_std = (_fit_df['lat'] - _fit_df['lat'].mean()) / _fit_df['lat'].std()
    _r, *_ = stats.linregress(_x_std, _y_std)
    _slope = _r * _fit_df['lat'].std() / _fit_df['awb'].std()
    _x0 = _fit_df['awb'].mean()
    _y0 = _fit_df['lat'].mean()
    ax.axline((_x0, _y0), slope=_slope, color='k', linewidth=1.2, linestyle='--')
    ax.text(0.97, 0.05, f'$r={_r:.2f}$', transform=ax.transAxes, fontsize=10,
            ha='right', va='bottom')
    if idx == 0:  # panel ai: extra r and slope for jet lat > 40
        _fit_sub = _fit_df[_fit_df['lat'] > 40]
        if len(_fit_sub) > 3:
            _xs = (_fit_sub['awb'] - _fit_sub['awb'].mean()) / _fit_sub['awb'].std()
            _ys = (_fit_sub['lat'] - _fit_sub['lat'].mean()) / _fit_sub['lat'].std()
            _r_sub, *_ = stats.linregress(_xs, _ys)
            _slope_sub = _r_sub * _fit_sub['lat'].std() / _fit_sub['awb'].std()
            ax.axline((_fit_sub['awb'].mean(), _fit_sub['lat'].mean()),
                      slope=_slope_sub, color='0.4', linewidth=1.2, linestyle='--')
            ax.text(0.97, 0.15, f'$r={_r_sub:.2f}$', transform=ax.transAxes,
                    fontsize=10, ha='right', va='bottom', color='0.4')


cbar_ax = ax_slope_pos.inset_axes([0.51, 0.56, 0.012, 0.44])
cbar = fig.colorbar(pcm, cax=cbar_ax, label='')
cbar.set_ticks([ 1e-2, 1e-1, 1e0])
cbar.set_ticklabels(['$10^{-2}$', '$10^{-1}$', '$10^{0}$'])
cbar.ax.tick_params(labelsize=10)
cbar_ax.set_title('JPDF', pad=4, fontsize=10)


# ---- Row 2: Negative phase (blocking vs baroc) ----
ax_slope_neg.plot(times_neg, slopes_neg, color='k', linewidth=1.5, zorder = 100)
ax_slope_neg.fill_between(times_neg, ci_low_neg, ci_high_neg, color='k', alpha=0.15, zorder = 100)
ax_slope_neg.axvline(0, color='gray', linewidth=0.7, linestyle=':')
ax_slope_neg.axvline(15, color='gray', linewidth=0.7, linestyle=':')
# mark the value on the line at day 0/15
for _t in (0, 15):
    _y = slopes_neg[np.argmin(np.abs(times_neg - _t))]
    ax_slope_neg.plot(_t, _y, marker='o', markerfacecolor='none', markeredgecolor='k', markersize=6, zorder=101)
ax_slope_neg.set_xlabel('days relative to event onset')
ax_slope_neg.set_ylabel('Pearson correlation coefficient')
ax_slope_neg.set_xlim(-5, 20)
ax_slope_neg.set_ylim(-0.65, -0.42)
ax_slope_neg.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.2f}'))
ax_slope_neg.spines['top'].set_visible(False)
ax_slope_neg.spines['right'].set_visible(False)
ax_slope_neg.tick_params(labelsize=10)
ax_slope_neg.text(-0.0, 1.05, 'b', transform=ax_slope_neg.transAxes, fontsize=11,
                  fontweight='bold', va='top', ha='right')

# JPDF insets for negative phase
ax2 = ax_slope_neg.inset_axes([0.08, 0.13, 0.40, 0.44])   # upper left
ax3 = ax_slope_neg.inset_axes([0.55, 0.58, 0.40, 0.44])    # bottom right

for idx, (ax, H, label, df) in enumerate(zip([ax2, ax3], [H_E2M_neg, H_M2E_neg], ['bi', 'bii'], [E2M_neg_df, M2E_neg_df])):
    pcm_neg = ax.contourf(X_neg, Y_neg, H, cmap='GnBu', levels=fill_levels,  extend='max')
    # pcl_neg = ax.contour(X_neg, Y_neg, H, levels=contour_levels, colors='k', linewidths=0.5)
    ax.set_xlabel('blocking (Z500) / km', fontsize=10)
    ax.set_ylabel('Eady growth rate / day$^{-1}$', fontsize=10)
    ax.tick_params(labelsize=10)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_ylim(2.2, 5.5)
    ax.text(-0.0, 1.1, label, transform=ax.transAxes, fontsize=10,
            fontweight='bold', va='top', ha='right')
    # linear regression line (standardized: slope = Pearson r, converted to data coords)
    _fit_df = df[['zg', 'eady_growth_rate']].dropna()
    _x_std = (_fit_df['zg'] - _fit_df['zg'].mean()) / _fit_df['zg'].std()
    _y_std = (_fit_df['eady_growth_rate'] - _fit_df['eady_growth_rate'].mean()) / _fit_df['eady_growth_rate'].std()
    _r, *_ = stats.linregress(_x_std, _y_std)
    _slope = _r * _fit_df['eady_growth_rate'].std() / _fit_df['zg'].std()
    _x0 = _fit_df['zg'].mean()
    _y0 = _fit_df['eady_growth_rate'].mean()
    ax.axline((_x0, _y0), slope=_slope, color='k', linewidth=1.2, linestyle='--')
    ax.text(0.05, 0.05, f'$r={_r:.2f}$', transform=ax.transAxes, fontsize=10,
            ha='left', va='bottom')

cbar_ax_neg = ax_slope_neg.inset_axes([0.47, 0.56, 0.012, 0.44])
cbar_neg = fig.colorbar(pcm_neg, cax=cbar_ax_neg, label='')
cbar_neg.ax.yaxis.set_ticks_position('left')
cbar_neg.ax.yaxis.set_label_position('left')
cbar_neg.set_ticks([1e-2, 1e-1, 1e0])
cbar_neg.set_ticklabels(['$10^{-2}$', '$10^{-1}$', '$10^{0}$'])
cbar_neg.ax.tick_params(labelsize=10)
cbar_ax_neg.set_title('JPDF', pad=4, fontsize=10)

plt.subplots_adjust(hspace=0.38, left=0.11, right=0.96, top=0.95, bottom=0.07)
plt.savefig("/work/mh0033/m300883/High_frequecy_flow/docs/plots/0after_defense/feedback_jpdf.pdf", dpi=300, bbox_inches='tight')


# %%

# %%
