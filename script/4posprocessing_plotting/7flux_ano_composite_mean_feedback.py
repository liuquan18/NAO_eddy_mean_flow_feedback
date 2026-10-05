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
    kwargs = dict(time_window="all", model_dir=MODEL_DIR)
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


#%%
# --- Read composite data (pos/neg × 1850/2090) ---
#%%
# Convergence of transient eddy momentum flux
Fdiv_phi_transient = _read_all("Fdiv_phi_transient", suffix="_ano", name="div")
Fdiv_p_transient = _read_all("Fdiv_p_transient", suffix="_ano", name="div2")
#%%
# Convergence of steady eddy momentum flux
Fdiv_phi_steady = _read_all("Fdiv_phi_steady", suffix="_ano", name="div")
Fdiv_p_steady = _read_all("Fdiv_p_steady", suffix="_ano", name="div2")

#%%
eke = _read_all("eke", suffix="_ano", name="eke")

#%%
eke_high = _read_all("eke_high", suffix="_ano", name="eke")
#%%
# Baroclinicity (Eady growth rate)
baroc = _read_all("eady_growth_rate", suffix="_ano", name="eady_growth_rate")

#%%
# second meridional gradient of transient eddy heat flux
transient_eddy_heat_d2y2 = _read_all("transient_eddy_heat_d2y2", suffix="_ano", name="eddy_heat_d2y2")

# second meridional gradient of steady eddy heat flux
steady_eddy_heat_d2y2 = _read_all("steady_eddy_heat_d2y2", suffix="_ano", name="eddy_heat_d2y2")

#%%
#%%
def _zonal_mean(da, lon_min=-90, lon_max=40):
    """Zonal mean over [lon_min, lon_max], handling both 0-360 and -180-180 grids."""
    if da.lon.max() > 180:
        # Convert 0-360 to -180-180
        da = da.assign_coords(lon=(da.lon + 180) % 360 - 180).sortby("lon")
    return da.sel(lon=slice(lon_min, lon_max)).mean(dim="lon")


#  Save all variables to 0composite_feedback

save_dir = "/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/0composite_feedback/anomaly"
os.makedirs(save_dir, exist_ok=True)

_to_save = {
    # "ua_pos_1850":                    ua["pos_1850"],
    # "ua_neg_1850":                    ua["neg_1850"],
    # "ua_pos_2090":                    ua["pos_2090"],
    # "ua_neg_2090":                    ua["neg_2090"],
    # "ua_hat_pos_1850":                  ua_hat["pos_1850"],
    # "ua_hat_neg_1850":                  ua_hat["neg_1850"],
    # "ua_hat_pos_2090":                  ua_hat["pos_2090"],    
    # "ua_hat_neg_2090":                  ua_hat["neg_2090"],
    # "upvp_pos_1850":                  upvp["pos_1850"],
    # "upvp_neg_1850":                  upvp["neg_1850"],
    # "upvp_pos_2090":                  upvp["pos_2090"],
    # "upvp_neg_2090":                  upvp["neg_2090"],
    # "Fdiv_phi_transient_pos_1850":    Fdiv_phi_transient["pos_1850"],
    # "Fdiv_phi_transient_neg_1850":    Fdiv_phi_transient["neg_1850"],
    # "Fdiv_phi_transient_pos_2090":    Fdiv_phi_transient["pos_2090"],
    # "Fdiv_phi_transient_neg_2090":    Fdiv_phi_transient["neg_2090"],
    # "Fdiv_p_transient_pos_1850":      Fdiv_p_transient["pos_1850"],
    # "Fdiv_p_transient_neg_1850":      Fdiv_p_transient["neg_1850"],
    # "Fdiv_p_transient_pos_2090":      Fdiv_p_transient["pos_2090"],
    # "Fdiv_p_transient_neg_2090":      Fdiv_p_transient["neg_2090"],
    # "Fdiv_phi_steady_pos_1850":       Fdiv_phi_steady["pos_1850"],
    # "Fdiv_phi_steady_neg_1850":       Fdiv_phi_steady["neg_1850"],
    # "Fdiv_phi_steady_pos_2090":       Fdiv_phi_steady["pos_2090"],
    # "Fdiv_phi_steady_neg_2090":       Fdiv_phi_steady["neg_2090"],
    # "Fdiv_p_steady_pos_1850":         Fdiv_p_steady["pos_1850"],
    # "Fdiv_p_steady_neg_1850":         Fdiv_p_steady["neg_1850"],
    # "Fdiv_p_steady_pos_2090":         Fdiv_p_steady["pos_2090"],
    # "Fdiv_p_steady_neg_2090":         Fdiv_p_steady["neg_2090"],
    # "eady_growth_rate_pos_1850":      baroc["pos_1850"],
    # "eady_growth_rate_neg_1850":      baroc["neg_1850"],
    # "eady_growth_rate_pos_2090":      baroc["pos_2090"],
    # "eady_growth_rate_neg_2090":      baroc["neg_2090"],
    # "zg_steady_pos_1850":             steady["pos_1850"],
    # "zg_steady_neg_1850":             steady["neg_1850"],
    # "zg_steady_pos_2090":             steady["pos_2090"],
    # "zg_steady_neg_2090":             steady["neg_2090"],
    # "vsets_pos_1850":                 vsts["pos_1850"],
    # "vsets_neg_1850":                 vsts["neg_1850"],
    # "vsets_pos_2090":                 vsts["pos_2090"],
    # "vsets_neg_2090":                 vsts["neg_2090"],
    # "steady_eddy_heat_dy_pos_1850":   vstsdy["pos_1850"],
    # "steady_eddy_heat_dy_neg_1850":   vstsdy["neg_1850"],
    # "steady_eddy_heat_dy_pos_2090":   vstsdy["pos_2090"],
    # "steady_eddy_heat_dy_neg_2090":   vstsdy["neg_2090"],
    # "vpetp_pos_1850":                 vptp["pos_1850"],
    # "vpetp_neg_1850":                 vptp["neg_1850"],
    # "vpetp_pos_2090":                 vptp["pos_2090"],
    # "vpetp_neg_2090":                 vptp["neg_2090"],
    "eke_pos_1850":                  eke["pos_1850"],
    "eke_neg_1850":                  eke["neg_1850"],
    "eke_pos_2090":                  eke["pos_2090"],
    "eke_neg_2090":                  eke["neg_2090"],
    # "eke_high_pos_1850":                eke_high["pos_1850"],
    # "eke_high_neg_1850":                eke_high["neg_1850"],
    # "eke_high_pos_2090":                eke_high["pos_2090"],
    # "eke_high_neg_2090":                eke_high["neg_2090"],
    # "transient_eddy_heat_d2y2_pos_1850": transient_eddy_heat_d2y2["pos_1850"],
    # "transient_eddy_heat_d2y2_neg_1850": transient_eddy_heat_d2y2["neg_1850"],
    # "transient_eddy_heat_d2y2_pos_2090": transient_eddy_heat_d2y2["pos_2090"],
    # "transient_eddy_heat_d2y2_neg_2090": transient_eddy_heat_d2y2["neg_2090"],
    # "steady_eddy_heat_d2y2_pos_1850": steady_eddy_heat_d2y2["pos_1850"],
    # "steady_eddy_heat_d2y2_neg_1850": steady_eddy_heat_d2y2["neg_1850"],
    # "steady_eddy_heat_d2y2_pos_2090": steady_eddy_heat_d2y2["pos_2090"],
    # "steady_eddy_heat_d2y2_neg_2090": steady_eddy_heat_d2y2["neg_2090"],
    # "zg_hat_pos_1850": zg_hat["pos_1850"],
    # "zg_hat_neg_1850": zg_hat["neg_1850"],
    # "zg_hat_pos_2090": zg_hat["pos_2090"],
    # "zg_hat_neg_2090": zg_hat["neg_2090"],
}

for fname, da in _to_save.items():
    path = os.path.join(save_dir, f"{fname}.nc")
    _zonal_mean(da).to_netcdf(path)
    print(f"Saved {path}")

# %%

