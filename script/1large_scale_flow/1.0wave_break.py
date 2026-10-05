# %%
import wavebreaking as wb
import numpy as np
import pandas as pd
import xarray as xr
import metpy.calc as mpcalc
import metpy.units as mpunits
import cartopy.crs as ccrs
from cdo import *  # python version
import os
import sys
import glob
import logging
import itertools
from scipy.spatial import distance as dist
from shapely.geometry import box

logging.basicConfig(level=logging.INFO)

# %%
def remap(ifile, var="ua", plev=None):
    cdo = Cdo()

    ofile = cdo.remapnn("r192x96", input=ifile, options="-f nc", returnXArray=var)
    if plev is not None:
        ofile = ofile.sel(plev=plev)

    return ofile


#%%
def filter_events_by_tracking(
    events, time_range=120, method="by_overlap", buffer=0, overlap=0.1, distance=1000
):
    """
    Filter events to only keep those that satisfy the temporal tracking conditions.

    Parameters
    ----------
        events : geopandas.GeoDataFrame
        time_range : int or float, optional
        method : {"by_overlap", "by_distance"}, optional
        buffer : float, optional
        overlap : float, optional
        distance : int or float, optional

    Returns
    -------
        filtered_events : geopandas.GeoDataFrame
            Only events that are part of a tracked pair.
    """

    # reset index of events
    events = events.reset_index(drop=True)

    # detect time range
    if time_range is None:
        date_dif = events.date.diff()
        time_range = date_dif[date_dif > pd.Timedelta(0)].min().total_seconds() / 3600

    # select events that are in range of time_range
    def get_range_combinations(events, index):
        if events.date.dtype == np.dtype("datetime64[ns]"):
            diffs = (events.date - events.date.iloc[index]).dt.total_seconds() / 3600
        else:
            diffs = abs(events.date - events.date.iloc[index])
        check = (diffs > 0) & (diffs <= time_range)
        return [(index, close) for close in events[check].index]

    range_comb = np.asarray(
        list(
            set(
                itertools.chain.from_iterable(
                    [get_range_combinations(events, index) for index in events.index]
                )
            )
        )
    )

    if len(range_comb) == 0:
        return events.iloc[[]]  # return empty DataFrame

    if method == "by_distance":
        com1 = np.asarray(list(events.iloc[range_comb[:, 0]].com))
        com2 = np.asarray(list(events.iloc[range_comb[:, 1]].com))
        dist_com = np.asarray(
            [dist.pairwise(np.radians([p1, p2]))[0, 1] for p1, p2 in zip(com1, com2)]
        )
        check_com = dist_com * 6371 < distance
        combine = range_comb[check_com]
    elif method == "by_overlap":
        geom1 = events.iloc[range_comb[:, 0]].geometry.buffer(buffer).make_valid()
        geom2 = events.iloc[range_comb[:, 1]].geometry.buffer(buffer).make_valid()
        inter = geom1.intersection(geom2, align=False)
        check_overlap = (
            inter.area.values
            / (geom2.area.values + geom1.area.values - inter.area.values)
            > overlap
        )
        combine = range_comb[check_overlap]
    else:
        raise ValueError(f"Method {method} not supported.")

    # Only keep events that are in at least one valid pair
    indices = np.unique(combine.flatten())
    filtered_events = events.iloc[indices].copy()
    return filtered_events


# %%
def filter_events_by_latitude_fraction(events, lat_threshold=40, fraction=0.5):
    """
    Filter events to only keep those where the area above a latitude threshold
    is at least a given fraction of the total event area.

    Parameters
    ----------
        events : geopandas.GeoDataFrame
        lat_threshold : float, optional
            Latitude threshold (default: 40)
        fraction : float, optional
            Minimum fraction of area above threshold (default: 0.5)

    Returns
    -------
        filtered_events : geopandas.GeoDataFrame
            Only events meeting the area fraction criterion.
    """
    # Assume geometry is in PlateCarree (lon/lat)
    def area_above_lat(geom):
        # Intersect with everything north of lat_threshold
        north_box = box(0, lat_threshold, 360, 90)
        inter = geom.intersection(north_box)
        return inter.area if not inter.is_empty else 0.0

    # Ensure all geometries are valid before processing
    events = events.copy()
    events['geometry'] = events['geometry'].apply(lambda geom: geom if geom.is_valid else geom.buffer(0))

    total_areas = events.geometry.area
    above_areas = events.geometry.apply(area_above_lat)
    frac_above = above_areas / total_areas
    filtered_events = events[frac_above > fraction].copy()
    return filtered_events

# %%
def wavebreaking(pv, mflux, mf_var="upvp"):
    pv = pv * 1e6
    pv = remap(pv, var = 'pv')
    mflux = remap(mflux, var = mf_var, plev = 25000)
    # contour_levels = [-2*1e-6, 2*1e-6]
    contour_levels = [-2, 2]
    
    smoothed = wb.calculate_smoothed_field(data=pv,
                                        passes=5,
                                        weights=np.array([[0, 1, 0], [1, 2, 1], [0, 1, 0]]), # optional
                                        mode="wrap") # optional
    # smooth the mflux
    mflux = wb.calculate_smoothed_field(data=mflux,
                                        passes=5,
                                        weights=np.array([[0, 1, 0], [1, 2, 1], [0, 1, 0]]), # optional
                                        mode="wrap") # optional

    # make sure that the time of the smoothed data is the same as the mflux
    mflux['time'] = smoothed['time']


    contours = wb.calculate_contours(data=smoothed,
                                    contour_levels=contour_levels,
                                    periodic_add=120, # optional
                                    original_coordinates=False) # optional

    # calculate streamers
    streamers = wb.calculate_streamers(data=smoothed,
                                    contour_levels=contour_levels,
                                    contours=contours, #optional
                                    geo_dis=800, # optional
                                    cont_dis=1200, # optional
                                    intensity=mflux, # optional
                                    periodic_add=120) # optional


    # classify
    events = streamers
    # stratospheric and tropospheric (only for streamers and cutoffs)
    # stratospheric = events[events.mean_var >= contour_levels[1]]
    # tropospheric = events[events.mean_var < contour_levels[1]]


    # anticyclonic and cyclonic by intensity for the Northern Hemisphere
    anticyclonic = events[events.intensity > 0]
    cyclonic = events[events.intensity < 0]
    
    # Filter anticyclonic events based on tracking conditions
    filtered_anticyclonic = filter_events_by_tracking(
        anticyclonic,
        time_range=72,
        method="by_overlap",
        buffer=0,
        overlap=0.2,
    )

    filtered_cyclonic = filter_events_by_tracking(
        cyclonic,
        time_range=72,
        method="by_overlap",
        buffer=0,
        overlap=0.2,
    )

    # filter by latitude fraction above 40 degrees
    filtered_anticyclonic = filter_events_by_latitude_fraction(
        filtered_anticyclonic, lat_threshold=30, fraction=0.5
    )
    filtered_cyclonic = filter_events_by_latitude_fraction(
        filtered_cyclonic, lat_threshold=30, fraction=0.5
    ) 


    # make sure the geometry is valid
    filtered_anticyclonic.geometry = filtered_anticyclonic.geometry.apply(lambda geom: geom if geom.is_valid else geom.buffer(0))
    filtered_cyclonic.geometry = filtered_cyclonic.geometry.apply(lambda geom: geom if geom.is_valid else geom.buffer(0))


    if not filtered_anticyclonic.empty:
        filtered_anticyclonic_array = wb.to_xarray(
            data=smoothed, events=filtered_anticyclonic
        )
    else:
        filtered_anticyclonic_array = xr.zeros_like(smoothed)

    if not filtered_cyclonic.empty:
        filtered_cyclonic_array = wb.to_xarray(data=smoothed, events=filtered_cyclonic)
    else:
        filtered_cyclonic_array = xr.zeros_like(smoothed)

    return filtered_anticyclonic_array, filtered_cyclonic_array

# %%
node = sys.argv[1]
ens = int(node)
logging.info(f"Processing ensemble {ens}")
mf_var = "upvp"  # can change to transient flux
isen_level = 330  # K


# %%
#%%
try:
    from mpi4py import MPI

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()  # [0,1,2,3,4,5,6,7,8,9]
    size = comm.Get_size()  # 10
except:
    logging.warning("::: Warning: Proceeding without mpi4py! :::")
    rank = 0
    size = 1


# %%
pv_path = f"/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6/pv_daily/r{ens}i1p1f1/"
upvp_path = f"/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6_allplev/upvp_daily/r{ens}i1p1f1/"  # change to transient flux

awb_path = f"/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6/wb_anticyclonic_daily/r{ens}i1p1f1/"
cwb_path = f"/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6/wb_cyclonic_daily/r{ens}i1p1f1/"


stratospheric_path = f"/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6/wb_stratospheric_daily/r{ens}i1p1f1/"
tropospheric_path = f"/work/mh0033/m300883/High_frequecy_flow/data/MPI_GE_CMIP6/wb_tropospheric_daily/r{ens}i1p1f1/"


if rank == 0:
    if not os.path.exists(awb_path):
        os.makedirs(awb_path)

    if not os.path.exists(cwb_path):
        os.makedirs(cwb_path)

    if not os.path.exists(stratospheric_path):
        os.makedirs(stratospheric_path)
    if not os.path.exists(tropospheric_path):
        os.makedirs(tropospheric_path)
# %%
all_decades = np.arange(1850, 2100, 10)
single_decades = np.array_split(all_decades, size)[rank]

# %%
for i, dec in enumerate(single_decades):
    logging.info(f"rank {rank} Processing {i+1}/{len(single_decades)}")


    pv_file = glob.glob(pv_path + f"*{dec}*.nc")
    pv = xr.open_dataset(pv_file[0])
    pv = pv.pv.sel(isentropic_level=isen_level)

    upvp_file = glob.glob(upvp_path + f"*{dec}*.nc")
    upvp = xr.open_dataset(upvp_file[0])['upvp']

    anticyclonic_array, cyclonic_array = wavebreaking(pv, upvp, mf_var='upvp')


    # save the data
    anticyclonic_array.to_netcdf(awb_path + f"wb_anticyclonic_{ens}_{dec}.nc")
    cyclonic_array.to_netcdf(cwb_path + f"wb_cyclonic_{ens}_{dec}.nc")
# %%
