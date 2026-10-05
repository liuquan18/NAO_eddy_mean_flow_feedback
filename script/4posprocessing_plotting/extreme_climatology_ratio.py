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
awb_pos = _read_all("wb_anticyclonic_allisen", name = 'smooth_pv', phase="pos", method='sum', M2E_window=(-5, 20))

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
awb_clim['smooth_pv'] = awb_clim['smooth_pv'] *1530*50 # sum than mean

baroc_clim = read_climatology("baroclinicity", "eady_growth_rate")
baroc_clim['eady_growth_rate'] = baroc_clim['eady_growth_rate'] * 86400 # convert from 1/s to 1/day

GB_clim = read_climatology("GB_index", "zg")
GB_clim['zg'] = GB_clim['zg'] / 1000 # convert to km


clim_pos_df = awb_clim.merge(jet_loc_clim, on = ['decade'])
clim_neg_df = baroc_clim.merge(GB_clim, on = ['decade'])


clim_pos_df = clim_pos_df.rename(columns={'smooth_pv': 'awb', 'lat': 'jet_lat'})
clim_neg_df = clim_neg_df.rename(columns={'eady_growth_rate': 'baroclinicity', 'zg': 'GB_index'})

# %%

# Compute difference dataframes
_ratio_pos = dec_pos_df.merge(clim_pos_df, on='decade', suffixes=('_dec', '_clim'))
_ratio_pos['awb_ratio'] = _ratio_pos['awb_dec'] / _ratio_pos['awb_clim']
_ratio_pos['jet_lat_ratio'] = _ratio_pos['jet_lat_dec'] / _ratio_pos['jet_lat_clim']

_ratio_neg = dec_neg_df.merge(clim_neg_df, on='decade', suffixes=('_dec', '_clim'))
_ratio_neg['baroclinicity_ratio'] = _ratio_neg['baroclinicity_dec'] / _ratio_neg['baroclinicity_clim']
_ratio_neg['GB_index_ratio'] = _ratio_neg['GB_index_dec'] / _ratio_neg['GB_index_clim']


#%%
# save ratio_data
_ratio_pos.to_csv("/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/0climatology_alldec/ratio_pos.csv", index=False)
_ratio_neg.to_csv("/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/0climatology_alldec/ratio_neg.csv", index=False)

# %%
