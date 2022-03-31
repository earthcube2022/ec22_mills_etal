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
# check if there is an error message
def check_error_message(ans,writeFlag=False):
    if isinstance(ans,dict) and 'message' in ans.keys() and 'code' in ans.keys():
        if writeFlag:
            print(str(ans['code']) + ': ' + ans['message'])
        ##### NOTE: we should include here below all the codes that do not return data as the user expects
        if ans['code']==403 or ans['code']==400:
            print('Data were not returned')
            print(ans)
            ciao_no_data
        return ans['code']        
    elif ans:
        return np.nan
#         if ans['code']==403:
#             print(ans)
#             ciao_stop
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
def get_data_from_url(url,myAPIkey,writeFlag=False):
    try:
        d_raw = requests.get(url,headers={"x-argokey": myAPIkey}).json()
        ans = check_error_message(ans=d_raw,writeFlag=writeFlag)
    except:
        print(url)
        ciao_no_data
    # check that data are a list of dictionaries as expected
    if ans == 404:
        return []
    elif np.isnan(ans) and check_list_of_dict(lst=d_raw,writeFlag=writeFlag) == 1:
        if writeFlag:
            print(url)
        return d_raw
    else:
        print(ans)
        ciao_check_obj_type_and_err_code
#############
def create_url(startDate,endDate,url_prefix, \
               radius_km=[],center=[], \
               polygon=[],data='',presRange='', \
               source='',platform_id='',woceline=''):
    # what is not used with which queries
    # what does not make sense to query together
    # does this order matter in the url?
    # go-ship variable names: temp is not in 
    # https://docs.google.com/spreadsheets/d/1WmrEcUwem3PLjPpEjm4exZYIG3Pk73L_iTlGjn14buY/edit#gid=0
    # what is temp? how do we distinguish between temp_btl and temp_ctd for go-ship currently?
    #
    ### PLEASE NOTE: 
    ## for the metadata query (getData=False), presRange is not used even if specified
    ## url_prefix should also include the type of call, e.g. '/profiles?', '/platform?'
    #
    ### OTHER NOTES: 
    #
    #### HERE we should call a function that checks that the input the user sends in makes sense
    #### e.g. the user should not specify data and datavars at the same time
    #### (as another example they should not have polygon and radius_km at the same time... and if
    #### they have radius_km, they should have center): if they include input 
    #### that does not make sense or is confusing, a message
    #### should appear to tell e.g. that only datavars will be used. For now I will create a function
    #### that makes decisions without sending error messages:
    #### if users set writeFlag = True, then they will see the URL when get_data_from_url is called in get_data_for_timeRange
     
    # In Python 3.10, the part below should be using match/case
    url = url_prefix + '&startDate='+startDate+'&endDate='+endDate
    # regional queries
    if radius_km and center:
        url = url + '&radius=' + radius_km + '&center=' + center
    elif polygon:
        url = url + '&polygon=' + polygon
        
    # queries by variable data
    if data:
        url = url + '&data=' + data
    
    # queries by pressure range
    if presRange:
        url = url + '&presRange=' + presRange
    
    # queries by source
    if source:
        url = url + '&source=' + source
    
    # queries by platform id
    if platform_id:
        url = url + '&platform_id=' + platform_id
    
    # queries by woceline
    if woceline:
        url = url + '&woceline=' + woceline
        
    return url
#############
def get_data_for_timeRange(startDate,endDate,url_prefix, \
                     myAPIkey,\
                     radius_km=[],center=[], \
                     polygon=[],data='',presRange='', \
                     source='',platform_id='',woceline='', \
                     dt_tag='d',writeFlag=False):
    # returns a panda dataFrame
    ### PLEASE NOTE: 
    ## for the metadata query (getData=False), presRange is not used even if specified
    ## url_prefix should also include the type of call, e.g. '/profiles?'
       
    list_of_days = create_list_of_days(startDate,endDate,dt_tag=dt_tag)
    info_ALL = []
    for i in np.arange(0,len(list_of_days)-1):
        #time.sleep(.25)
        url_to_use = create_url(startDate=list_of_days[i], \
                               endDate=list_of_days[i+1], \
                               url_prefix=url_prefix, \
                               radius_km=radius_km,center=center, \
                               polygon=polygon,data=data,presRange=presRange, \
                               source=source,platform_id=platform_id,woceline=woceline)
        #print(url_to_use)
        info_ALL   = info_ALL + get_data_from_url(url=url_to_use,myAPIkey=myAPIkey,writeFlag=writeFlag)
                               
    info_ALL = pd.DataFrame(info_ALL)
    
    return info_ALL
#############
def get_info_from_df(df,info_to_store):
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
                for jsource in df.source_info[i]:
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
                ciao_check_length
            
        dict_info = {}
        for i,ival in zip(info_to_store,lst_out):
            if ival:
                dict_info[i] = ival
    return dict_info
##############
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
##################
def polygon_lon_lat(polygon_str):
    # convert the polygon shape to lon and lat and save in a dictionary
    polygon_lon_lat_dict = {'lon': [float(i) for i in ((polygon_str.replace('[','')).replace(']','')).split(',')[0::2]], \
                    'lat': [float(i) for i in ((polygon_str.replace('[','')).replace(']','')).split(',')[1::2]]
                   }
    return polygon_lon_lat_dict
##################
##################
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

    # im = plt.scatter(float_events_lon_i,float_events_lat_i,transform=ccrs.PlateCarree(),s=1000,marker='*',
    #                         color=my_colors[i], linewidth=3.5) 
###############
def set_map_and_plot_locations_withColor(lon,lat,cols,polygon_lon_lat_dict=[],markersz=10,dx=15,dy=15,central_long=-30, \
                                         delta_lonGrid=15,delta_latGrid=15,fnt_size=28, \
                                         fig_size=(10,10)):
    # set up the map
    fig = plt.figure(figsize=fig_size)
    lon_all = lon
    lat_all = lat
    if polygon_lon_lat_dict:
        lon_all = lon_all + polygon_lon_lat_dict['lon']
        lat_all = lat_all + polygon_lon_lat_dict['lat']
    ax, gl, usemap_proj = set_up_map(set_extent_info=[min(lon_all)-dx,max(lon_all)+dx,min(lat_all)-dy,max(lat_all)+dy],
                                     central_long=central_long,
                                     delta_lonGrid=delta_lonGrid,delta_latGrid=delta_latGrid,fnt_size=fnt_size,
                                     )
    # plot the locations of the porofiles and polygon
    if polygon_lon_lat_dict:
        plt.plot(polygon_lon_lat_dict['lon'],polygon_lon_lat_dict['lat'],'-k',transform=ccrs.PlateCarree()) 
    plot_locations_withColor(lon=lon,lat=lat, \
                             cols=cols,markersz=markersz,fnt_size=28)
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