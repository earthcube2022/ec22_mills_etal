#data processing
import requests, copy, math
import numpy as np
import pandas as pd
import scipy.interpolate

#data visualization
import matplotlib.pylab as plt
from matplotlib import ticker

#used for map projections
import cartopy.crs as ccrs
import cartopy.feature as cft
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

import warnings
warnings.filterwarnings('ignore')

########### data processing #################

def get_info_from_df(df,info_to_store):
    # df: dataframe as returned by ie get_data_for_timeRange
    # info_to_store: list of strings indicating variables of interest
    # returns dictionary packing of listed info from dataframe

    if isinstance(df,pd.DataFrame):
        lon  = []
        lat  = []
        date = []
        cols_bySource=[]
        ids  = []
        woce_line = []
        
        lst_out = []
        
        for i in np.arange(0,len(df),1):
            #
            if any("lon" in s for s in info_to_store) or  any("lat" in s for s in info_to_store):
                lon.append(df.geolocation[i]['coordinates'][0])
                lat.append(df.geolocation[i]['coordinates'][1])
            #
            if any("date" in s for s in info_to_store):
                date.append(df.timestamp[i][0:-5]+'Z')
            #
            if any("ids" in s for s in info_to_store):
                ids.append(df._id[i])
            #
            if any("cols_bySource" in s for s in info_to_store):
                bfr_source= []
                for jsource in df.source[i]:
                    bfr_source = bfr_source + jsource['source']
                cols_bySource.append(select_color_byList(lst_in=bfr_source))
            # 
            if any("woce_line" in s for s in info_to_store):
                if "woce_line" in df.keys():
                    woce_line.append(df.woce_line[i])
                    
        for i in info_to_store:
            if len(eval(i)) ==len(df) or not eval(i):
                eval('lst_out.append('+ i +')')
            else:
                raise Exception('check length')
            
        dict_info = {}
        for i,ival in zip(info_to_store,lst_out):
            if ival:
                dict_info[i] = ival
    return dict_info

def polygon_lon_lat(polygon_str):
    # polygon_str: string value of polygon search parameter, ie "[[lon0,lat0],[lon1,lat1],...,[lon0,lat0]]"
    # convert the polygon shape to lon and lat and save in a dictionary
    polygon_lon_lat_dict = {'lon': [float(i) for i in ((polygon_str.replace('[','')).replace(']','')).split(',')[0::2]], \
                    'lat': [float(i) for i in ((polygon_str.replace('[','')).replace(']','')).split(',')[1::2]]
                   }
    return polygon_lon_lat_dict
######
########### data visualization #################
# set up a map
def set_up_map(set_extent_info,central_long=180,delta_lonGrid=30,delta_latGrid=30,fnt_size=28):
    # set_extent_info: [min lon, max lon, min lat, max lat] for mapping region
    # central_long: central longitude for map projection
    # delta_lonGrid: how close in degrees to space longitude ticks
    # delta_latGrid: how close in degrees to space latitude ticks
    # fnt_size: x/y axis label font size

    # this declares a recentered projection for Pacific areas
    usemap_proj = ccrs.PlateCarree(central_longitude=central_long)
    usemap_proj._threshold /= 20.  # to make greatcircle smooth

    ax = plt.axes(projection=usemap_proj)
    # set appropriate extents: (lon_min, lon_max, lat_min, lat_max)
    ax.set_extent(set_extent_info, crs=ccrs.PlateCarree())

    gl = ax.gridlines(draw_labels=True,color='black')
    gl.xlabels_top = False
    gl.ylabels_right = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlocator = ticker.FixedLocator(np.arange(-180,180,delta_lonGrid))
    gl.ylocator = ticker.FixedLocator(np.arange(-90,90,delta_latGrid))

    gl.xlabel_style = {'size': fnt_size}
    gl.ylabel_style = {'size': fnt_size}

    ax.coastlines()
    ax.add_feature(cft.LAND)#, color='lightgray'
    ax.add_feature(cft.OCEAN)
    ax.add_feature(cft.COASTLINE)
    ax.add_feature(cft.BORDERS, linestyle=':')

    geodetic = ccrs.Geodetic()
    return ax, gl, usemap_proj
######
def plot_locations_withColor(lon,lat,cols,markersz=10,fnt_size=28):
    # plot a map with profile locations: if cols is only 1 string, then the same color is used for all the dots
    # if cols is a list of strings of the same length as e.g. lon, then one col per lon is used
    # else 'k' is used for color

    for i in np.arange(0,len(lon),1):
        if len(cols) == len(lon):
            col = cols[i]
        elif isinstance(col,str):
            col = cols
        else:
            col = 'k'
        plt.plot(lon[i],lat[i],marker='o',markersize=markersz,color=col,transform=ccrs.PlateCarree()) # cols_bySource[i]
######
def set_map_and_plot_locations_withColor(lon,lat,cols,polygon_lon_lat_dict=[],markersz=10,dx=15,dy=15,central_long=-30, \
                                         delta_lonGrid=15,delta_latGrid=15,fnt_size=28, \
                                         fig_size=(10,10)):
    # lon: list of all longitudes of interest
    # lat: list of all latitudes of interest
    # polygon_lon_lat_dict: dictionary of longitudes and latitudes describing polygon region, see polygon_lon_lat function
    # markersz: scatterplot marker size
    # dx: degrees of margin space in longitude
    # dy: degrees of margin space in latitude
    # central_long, delta_lonGrid, delta_latGrid, fnt_size: see set_up_map
    # fig_size: matplotlib figure size

    # set up the map
    fig = plt.figure(figsize=fig_size)
    lon_all = lon
    lat_all = lat
    if polygon_lon_lat_dict:
        lon_all = lon_all + polygon_lon_lat_dict['lon']
        lat_all = lat_all + polygon_lon_lat_dict['lat']
    ax, gl, usemap_proj = set_up_map(set_extent_info=[(min(lon_all)-dx)%360,(max(lon_all)+dx)%360,min(lat_all)-dy,max(lat_all)+dy],
                                     central_long=central_long,
                                     delta_lonGrid=delta_lonGrid,delta_latGrid=delta_latGrid,fnt_size=fnt_size,
                                     )
    # plot the locations of the porofiles and polygon
    if polygon_lon_lat_dict:
        plt.plot(polygon_lon_lat_dict['lon'],polygon_lon_lat_dict['lat'],'-k',transform=ccrs.PlateCarree()) 
    plot_locations_withColor(lon=lon,lat=lat, \
                             cols=cols,markersz=markersz,fnt_size=28)
#######

# pick color based on list of sources
def select_color_byList(lst_in):
    if any("argo_bgc" in s for s in lst_in) and any("argo_deep" in s for s in lst_in):
        col = 'r'
    elif any("argo_bgc" in s for s in lst_in):
        col = 'g'
    elif any("argo_deep" in s for s in lst_in):
        col = 'b'
    elif any("argo_core" in s for s in lst_in):
        col = 'y'
    elif any("cchdo_go" in s for s in lst_in):
        col = 'k'
    else:
        col = 'gray'
    return col   
######    
# pick label
def set_ax_label(str_in):
    if str_in=='psal':
        ax_lab = 'Salinity [psu]'
    elif str_in=='temp':
        ax_lab = 'Temperature [degC]'
    elif str_in=='pres':
        ax_lab = 'Pressure [dbar]'
    elif str_in=='doxy':
        ax_lab = 'Oxygen, micromole/kg'
    else:
        ax_lab = str_in
    return ax_lab
#######
def qc_suffix(profile):
    # given a <profile> object 
    # return what the corresponding QC variable suffix.

    qcsuffix = None
    if 'argo' in profile['source'][0]['source'][0]:
        qcsuffix = '_argoqc'
    else:
        qcsuffix = '_woceqc'

    return qcsuffix    
#######
def qc(profile, qc_levels=[]):
    # given a <profile> and a list <qc_levels> of tuples (<variable>, <[allowed qcs]>),
    # Suppress all measurements that don't pass the specified QC.
    # If any measurements have qc present in <profiles.data> but don't have a level set in <qc_levels>,
    # require QC==1 for argo data and ==2 for CCHDO.

    qcsuffix = qc_suffix(profile)        
    qclookup = dict(qc_levels)
    
    if 'data' in profile and 'data_keys' in profile:
        for k in profile['data_keys']:
            if qcsuffix not in k: 
                # insist all data comes with qc
                if k+qcsuffix not in profile['data_keys']:
                    print(k, 'present without its QC; please add', k+qcsuffix, 'to your data query.')
                    return None
                if k in qclookup:
                    profile = mask_QC(profile, k, qclookup[k])
                elif qcsuffix == '_argoqc':
                    profile = mask_QC(profile, k, [1]) # default QC==1 for Argo 
                elif qcsuffix == '_woceqc':
                    profile = mask_QC(profile, k, [2]) # default QC==1,2 for CCHDO
    return profile
######            
def mask_QC(profile, variable, allowed_qc):
    # given a <profile> object, set <variable> to None if its QC flag is not in the list <allowed_qc>, 
    # and return the resulting profile object

    qcsuffix = qc_suffix(profile)  

    # helper for masking a single level dict; missing QC info == failed
    def m(level, var,qc,allowed_qc):
        if qc not in level or not level[qc] or level[qc] not in allowed_qc:
            level[var] = None
        return level


    masked_profile = copy.deepcopy(profile) # don't mutate the original
    if 'data' in masked_profile and variable in masked_profile['data_keys'] and variable+qcsuffix in masked_profile['data_keys']:
        masked_profile['data'] = [m(level,variable,variable+qcsuffix,allowed_qc) for level in masked_profile['data']]

    return masked_profile
######
def simple_plot(profile, variable, variable_qc=None):

    if 'data' in profile and variable in profile['data_keys']:
        if variable_qc and variable_qc in profile['data_keys']:
            d = [x for x in profile['data'] if variable in x and variable_qc in x]
            plt.scatter([x[variable] for x in d],[y['pressure'] for y in d], c=[c[variable_qc] for c in d])
            plt.colorbar()
        else:
            d = [x for x in profile['data'] if variable in x]
            plt.scatter([x[variable] for x in d],[y['pressure'] for y in d])
    
    plt.xlabel(variable)
    plt.ylabel('pressure')
    plt.gca().invert_yaxis()
######
def interpolate(profile, levels, method='pchip'):
    # given a <profile> and a list of desired pressure <levels>,
    # return a profile with profile.data levels at the desired pressure levels, with all available data interpolated to match
    # drop all QC and note `data_interpolated` in profile.data_warnings

    if method not in ['pchip', 'linear', 'nearest']:
        print('method must be one of pchip, linear or nearest')
        return None
    
    data_names = ['pressure']
    interpolated_data = [levels]
    for key in profile['data_keys']:
        if '_argoqc' not in key and '_woceqc' not in key and key!='pressure':
            finites = [(level['pressure'], level[key]) for level in profile['data'] if level['pressure'] is not None and level[key] is not None and not math.isnan(level['pressure']) and not math.isnan(level[key])]
            pressure = [x[0] for x in finites]
            data = [x[1] for x in finites]
            data_names.append(key)
            if method == 'pchip':
                interpolated_data.append(scipy.interpolate.pchip_interpolate(pressure, data, levels))
            elif method == 'linear':
                f = scipy.interpolate.interp1d(pressure, data, kind='linear', fill_value='extrapolate')
                interpolated_data.append([f(x) for x in levels])
            elif method == 'nearest':
                f = scipy.interpolate.interp1d(pressure, data, kind='nearest', fill_value='extrapolate')
                interpolated_data.append([f(x) for x in levels])
    
    interpolated_levels = list(zip(*interpolated_data))
    data = [{data_names[i]:d[i] for i in range(len(data_names))} for d in interpolated_levels]
    interpolated_profile = copy.deepcopy(profile) # don't mutate the original
    interpolated_profile['data'] = data
    if 'data_warnings' in interpolated_profile:
        interpolated_profile['data_warnings'].append('data_interpolated')
    else:
        interpolated_profile['data_warnings'] = ['data_interpolated']
    return interpolated_profile
