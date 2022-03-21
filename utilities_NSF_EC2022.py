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
# Check if anything came back from the API or no data were found/an error was returned (to update):
def raw_check(d_raw,d_raw_type,writeFlag=False):
#     print(type(d_raw))
#     print(d_raw)
    try:
        if 'message' in d_raw.keys():
            if writeFlag:
                print(d_raw)
            return 0
    except:
        if d_raw_type=='list':
            return check_list(d_raw)
        elif d_raw_type=='list_of_lists':
            return check_list_of_list(d_raw)

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
########### The two functions below should be merged in one giving in input to the function the object type
def get_info_from_dict(d_dict,info_to_store):
    if isinstance(d_dict,dict):
        lst_out = []
        if any("lon" in s for s in info_to_store) or  any("lat" in s for s in info_to_store):
            geoloc = d_dict['geolocation']
            lon = geoloc['coordinates'][0]
            lat = geoloc['coordinates'][1]
                
        if any("cols_bySource" in s for s in info_to_store):
            isource = d_dict['source_info']
            bfr_source = []
            for jsource in isource:
                bfr_source = bfr_source+jsource.get('source')
                cols_bySource = select_color_byList(bfr_source)
        for i in info_to_store:
            eval('lst_out.append('+ i +')')
    return lst_out
    
def get_info_from_df(df,info_to_store):
    if isinstance(df,pd.DataFrame):
        lst_out = []
        if any("lon" in s for s in info_to_store) or  any("lat" in s for s in info_to_store):
            lon = []
            lat = []
            for geoloc in df.geolocation:
                lon.append(geoloc['coordinates'][0])
                lat.append(geoloc['coordinates'][1])

        if any("cols_bySource" in s for s in info_to_store):
            cols_bySource = []
            for isource in df.source_info:
                bfr_source = []
                for jsource in isource:
                    bfr_source = bfr_source+jsource.get('source')
                    cols_bySource.append(select_color_byList(bfr_source))
        for i in info_to_store:
            eval('lst_out.append('+ i +')')
    return lst_out
###########
# get metadata for variable
def get_metadata_for_var(var_tag,startDate,endDate,info_to_store,url_prefix,query_type='global',polygon=[],max_ids_in_query=3):
    list_of_days = create_list_of_days(startDate,endDate)
    info_ALL = []
    for i in np.arange(0,len(list_of_days)-1):
        #time.sleep(1)
        if query_type=='global':
            url = '/profiles/listID?startDate=' + list_of_days[i] + \
              '&endDate=' + list_of_days[i+1] + '&data=' + var_tag #+ \
        elif query_type=='inPolygon':
            url = '/profiles/listID?startDate=' + list_of_days[i] + \
              '&endDate=' + list_of_days[i+1] + '&data=' + var_tag+ \
              '&polygon=' + polygon

        d_raw = requests.get(url_prefix+url).json()

        if raw_check(d_raw=d_raw,d_raw_type='list') ==1:
            ind = np.arange(0,len(d_raw),max_ids_in_query)

            if len(ind)==1:
                 ind = np.append(ind,len(d_raw))
            # query using the ids (loop so that you don't query too many ids at a time)
            for i_ind in np.arange(0,len(ind)-1,1):
                if ind[i_ind+1]-1 == 0:
                    bfr_d_meta = requests.get(url_prefix+
                                    '/profiles?ids='+string_of_ids(d_raw[ind[i_ind]])).json()
                elif ind[i_ind+1]-1 > 0:
                    bfr_d_meta = requests.get(url_prefix+
                                    '/profiles?ids='+string_of_ids(d_raw[ind[i_ind]:ind[i_ind+1]-1])).json()

                if type(bfr_d_meta) is dict and 'message' in bfr_d_meta.keys():
                    continue
                else:
                    if len(bfr_d_meta)==1 and isinstance(bfr_d_meta[0],dict):
                        info_ALL.append(get_info_from_dict(d_dict=bfr_d_meta[0],info_to_store=info_to_store))
                    elif len(bfr_d_meta)>1:
                        info_ALL.append(get_info_from_df(df=pd.DataFrame(bfr_d_meta),info_to_store=info_to_store))
    return info_ALL

# create a list of days (in string format) from string dates in input, e.g.
#startDate='2021-05-01T00:00:00Z'
#endDate  ='2021-05-10T00:00:00Z'
def create_list_of_days(startDate,endDate):
    list_of_days = (pd.DataFrame(columns=['NULL'],
                            index=pd.date_range(startDate,endDate,
                                                freq='30T')) #'d'
                                   .between_time('00:00','23:59')
                                   .index.strftime('%Y-%m-%dT%H:%M:%SZ')
                                   .tolist()
                )
    #####list_of_days      = [datetime.strptime(ii,'%Y-%m-%dT%H:%M:%SZ') for ii in bfr_times]
    ## this should be added back if I am allowed to do more queries (UPDATE: IT MAY NOT BE NEEDED)
    #list_of_days.append(list_of_days[-1][0:11]+'23:59:59Z')
    return list_of_days

# create a string of ids in the format needed for an API query (the input is a list of lists from an API query)
def string_of_ids(d_raw):
    lst = ''
    for ilst in d_raw:
        lst = lst + ilst +','
    lst = lst[0:-2]
    return lst


# # create a list of panda dataFrames from a list of dictionaries coming from API queries
# def create_list_of_df_from_list_of_dict(d_lst_of_dict):
#     # check that you have a list of lists in input
#     if check_list_of_dict(lst=d_lst_of_dict)==1:
#         # convert all the lists in d_lst_of_lst into panda dataframes
#         data_list_of_df = []
#         for d in d_lst_of_dict:
#             data_list_of_df.append(pd.DataFrame(d))
#     else:
#         print('Function create_list_of_df: check the variable d and what type it is')  
#         print(type(d_lst_of_lst))
#         print(d_lst_of_lst)
#         stop
#     return data_list_of_df

##### this below may be outdated...
# # create a list of panda dataFrames from a list of lists coming from API queries
# def create_list_of_df(d_lst_of_lst):
#     # check that you have a list of lists in input
#     if check_list_of_list(lst=d_lst_of_lst)==1:
#         # convert all the lists in d_lst_of_lst into panda dataframes
#         data_list_of_df = []
#         # check if there is only one list in the list
#         for d in d_lst_of_lst:
#             if check_list(d)==1:
#                 data_list_of_df.append(pd.DataFrame(d))
#             else:
#                 print('Function create_list_of_df: check the variable d and what type it is') 
#                 print(type(d))
#                 print(d)
#                 stop
#     else:
#         print('Function create_list_of_df: check the variable d and what type it is')  
#         print(type(d_lst_of_lst))
#         print(d_lst_of_lst)
#         stop
#     return data_list_of_df

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
    