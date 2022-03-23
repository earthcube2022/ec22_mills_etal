#data processing
import requests
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, date
import dateutil.parser

#import xarray as xr
import os
import time

#data visualization
# %matplotlib inline
import matplotlib.pylab as plt
from matplotlib import ticker
# %matplotlib inline

#used for map projections
import cartopy.crs as ccrs
import cartopy.feature as cft
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

# #widgets for user interaction
# import ipywidgets as widgets

import warnings
warnings.filterwarnings('ignore')
from dateutil import parser

########### data processing #################
#
########### checks for objects coming back from API queries
def check_list(lst,writeFlag=False):
    if lst and isinstance(lst,list):
        if writeFlag:
            print('Number of items: '+str(len(lst)))
        return 1
    else:
        if writeFlag:
            print(lst) 
        return 0
####
def check_list_of_list(lst,writeFlag=False):
    if lst and isinstance(lst,list):
        if all(isinstance(i, list) for i in lst):
            if writeFlag:
                print('Number of items: '+str(len(lst)))
            return 1
        else:
            if writeFlag:
                print(lst) 
            return 0
    else:
        if writeFlag:
            print(lst) 
        return 0
###
####
def check_list_of_dict(lst,writeFlag=False):
    if lst and isinstance(lst,list):
        if all(isinstance(i, dict) for i in lst):
            if writeFlag:
                print('Number of items: '+str(len(lst)))
            return 1
        else:
            if writeFlag:
                print(lst) 
            return 0
    else:
        if writeFlag:
            print(lst) 
        return 0 
#############
def get_data_for_var(var_tag,startDate,endDate,url_prefix, \
                     query_type='global',polygon=[],presRange='',dt_tag='d',getData=False,writeTag=False):
    # for the metadata query (getData=False), presRange is not used even if specified
    list_of_days = create_list_of_days(startDate,endDate,dt_tag=dt_tag)
    info_ALL = []
    for i in np.arange(0,len(list_of_days)-1):
        time.sleep(.25)
        if query_type=='global':
            if getData:
                url = '/profiles?startDate='+list_of_days[i]+'&endDate='+list_of_days[i+1]+ \
                      '&data='+var_tag+',pres'
            else:
                url = '/profiles?startDate='+list_of_days[i]+'&endDate='+list_of_days[i+1]+ \
                      '&datavars='+var_tag+',pres'
        elif query_type=='inPolygon':
            if getData:
                url = '/profiles?startDate='+list_of_days[i]+'&endDate='+list_of_days[i+1]+ \
                  '&polygon='+ polygon + \
                  '&data='+var_tag+',pres'
            else:
                url = '/profiles?startDate='+list_of_days[i]+'&endDate='+list_of_days[i+1]+ \
                      '&polygon='+ polygon + \
                      '&datavars='+var_tag+',pres'
        if presRange:
            url = url + '&presRange=' + presRange
        try:
            d_raw = requests.get(url_prefix+url).json()
            ans = check_error_message(ans=d_raw,writeFlag=True)
            if ans == 404:
                # print(url_prefix+url)
                continue
        except:
            print(url_prefix+url)
            ciao_stop
        # print(str(len(d_raw)) + ': ' + str(type(d_raw)))
        if check_list_of_dict(lst=d_raw,writeFlag=True) == 1:
            if writeTag:
                print(url_prefix+url)
            info_ALL = info_ALL + d_raw
        else:
            ciao_type
    return info_ALL
##############
def get_info_from_df(df,info_to_store):
    if isinstance(df,pd.DataFrame):
        lon  = []
        lat  = []
        date = []
        cols_bySource=[]

        lst_out = []
        for i in np.arange(0,len(df),1):
            #
            if any("lon" in s for s in info_to_store) or  any("lat" in s for s in info_to_store):
                lon.append(df.geolocation[i]['coordinates'][0])
                lat.append(df.geolocation[i]['coordinates'][1])
            #
            if any("date" in s for s in info_to_store):
                date.append(df.timestamp[i])
            #
            if any("cols_bySource" in s for s in info_to_store):
                bfr_source= []
                for jsource in df.source_info[i]:
                    bfr_source = bfr_source + jsource['source']
                cols_bySource.append(select_color_byList(lst_in=bfr_source))
        for i in info_to_store:
            eval('lst_out.append('+ i +')')
            
        dict_info = {}
        for i,ival in zip(info_to_store,lst_out):
            dict_info[i] = ival
    return dict_info
##############
# check if there is an error message
def check_error_message(ans,writeFlag=False):
    if isinstance(ans,dict) and 'message' in ans.keys() and 'code' in ans.keys():
        if writeFlag:
            print(str(ans['code']) + ': ' + ans['message'])
        if ans['code']==403:
            print('Data were not returned')
            ciao403
        return ans['code']        
    elif ans:
        return np.nan
#         if ans['code']==403:
#             print(ans)
#             ciao_stop
##########                
# create a list of days (in string format) from string dates in input, e.g.
#startDate='2021-05-01T00:00:00Z'
#endDate  ='2021-05-10T00:00:00Z'
def create_list_of_days(startDate,endDate,dt_tag='d'): 
    # dt_tag could be '30T', 'd', ...
    list_of_days = (pd.DataFrame(columns=['NULL'],
                            index=pd.date_range(startDate,endDate,
                                                freq=dt_tag)) #'d'
                                   .between_time('00:00','23:59')
                                   .index.strftime('%Y-%m-%dT%H:%M:%SZ')
                                   .tolist()
                )
    #####list_of_days      = [datetime.strptime(ii,'%Y-%m-%dT%H:%M:%SZ') for ii in bfr_times]
    ## this should be added back if I am allowed to do more queries (UPDATE: IT MAY NOT BE NEEDED)
    if list_of_days[-1] != endDate:
        list_of_days.append(endDate[0:11]+'23:59:59Z')
    return list_of_days

# create a string of ids in the format needed for an API query (the input is a list of lists from an API query)
def string_of_ids(d_raw):
    lst = ''
    for ilst in d_raw:
        lst = lst + ilst +','
    lst = lst[0:-2]
    return lst

########### data visualization #################
# set up a map
def set_up_map(set_extent_info,central_long=180,delta_lonGrid=30,delta_latGrid=30,fnt_size=28):
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
    #plate_carree = ccrs.PlateCarree(central_longitude=central_long)
    return ax, gl, usemap_proj

###############
def plot_locations_withColor(lon,lat,cols,dx=30,dy=30,central_long=180,markersz=10,fnt_size=28):

    # plot a map with profile locations: if cols is only 1 string, then the same color is used for all the dots
    # if cols is a list of strings of the same length as e.g. lon, then one col per lon is used
    # else 'k' is used for color
    fig = plt.figure(figsize=(20,7))

    ax, gl, usemap_proj = set_up_map(set_extent_info=[min(lon)-dx,max(lon)+dx,min(lat)-dy,max(lat)+dy],
                                     central_long=central_long,
                                     delta_lonGrid=90,delta_latGrid=45,fnt_size=28)

    for i in np.arange(0,len(lon),1):
        if len(cols) == len(lon):
            col = cols[i]
        elif isinstance(col,str):
            col = cols
        else:
            col = 'k'
        plt.plot(lon[i],lat[i],marker='o',markersize=markersz,color=col,transform=ccrs.PlateCarree()) # cols_bySource[i]

    # im = plt.scatter(float_events_lon_i,float_events_lat_i,transform=ccrs.PlateCarree(),s=1000,marker='*',
    #                         color=my_colors[i], linewidth=3.5) 

    plt.show()
###############
# pick color based on string
def select_color_byString(str_in):
    if str_in == 'argo_core':
        col = 'y'
    elif str_in == 'argo_bgc':
        col = 'g'
    elif str_in == 'argo_deep':
        col = 'b'
    elif str_in == 'cchdo_go-ship':
        col = 'r'
    else:
        col = 'k'
    return col
        
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
    