#!/usr/bin/env python
# coding: utf-8

# In[1]:


#data processing
import requests
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, date
import dateutil.parser

#import xarray as xr
import os

#data visualization
get_ipython().run_line_magic('matplotlib', 'inline')
import matplotlib.pylab as plt
from matplotlib import ticker
get_ipython().run_line_magic('matplotlib', 'inline')

#used for map projections
import cartopy.crs as ccrs
import cartopy.feature as cft
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

# #widgets for user interaction
# import ipywidgets as widgets

import warnings
warnings.filterwarnings('ignore')
from dateutil import parser


# In[2]:


##### import local functions
# for data processing
from utilities_NSF_EC2022 import create_list_of_days,string_of_ids,                                     raw_check,check_list_of_list,check_list,                                     get_info_from_dict,get_info_from_df,get_metadata_for_var
# for data visualization
from utilities_NSF_EC2022 import set_up_map,select_color_byList


# In[3]:


# set parameters that will be used later for API queries

# prefix to use with all API queries
url_prefix = 'https://argovis-apix-atoc-argovis-dev.apps.containers02.colorado.edu'

# shape defining the region of interest (copy and paste from the browser, i.e. current "shape" parameter in the url)
# i.e. 
# 1. visit argovis.colorado.edu
# 2. draw a shape
# 3. click on the purple shaded area of the region of interest (not on a dot)
# 4. from the pop up window, go "to Selection page"
# 5. from the url of the selection shape, copy the shape, i.e. [...] after 'shape='
# Example url once the shape has been drawn in step 2. above (if you visit the url, you can follow the remaining steps):
#
# https://argovis.colorado.edu/ng/home?mapProj=WM&presRange=%5B0,2000%5D&selectionStartDate=2022-03-06T03:09:16Z&selectionEndDate=2022-03-20T03:09:16Z&threeDayEndDate=2022-03-18T03:09:16&shapes=%5B%5B%5B-9.968851,-188.4375%5D,%5B42.032974,-189.316406%5D,%5B43.316276,-181.068685%5D,%5B43.400281,-180%5D,%5B43.400281,-180%5D,%5B43.985697,-172.552544%5D,%5B44.012922,-163.936245%5D,%5B43.396764,-155.404774%5D,%5B42.163403,-147.128906%5D,%5B-9.449062,-143.964844%5D,%5B-9.425184,-150.646206%5D,%5B-9.275622,-157.324219%5D,%5B15.961329,-160.664062%5D,%5B16.136471,-166.90164%5D,%5B16.130262,-173.144531%5D,%5B-10.833306,-174.199219%5D,%5B-10.545911,-180%5D,%5B-10.545911,-180%5D,%5B-10.480104,-181.328268%5D,%5B-9.968851,-188.4375%5D%5D%5D&includeRealtime=true&onlyBGC=false&onlyDeep=false&threeDayToggle=false
# polygon = '[[171.5625,-9.968851],[170.683594,42.032974],[178.931315,43.316276],[-180,43.400281],'+     \
#           '[-180,43.400281],[-172.552544,43.985697],[-163.936245,44.012922],[-155.404774,43.396764],'+  \
#           '[-147.128906,42.163403],[-143.964844,-9.449062],[-150.646206,-9.425184],[-157.324219,-9.275622],'+ \
#           '[-160.664062,15.961329],[-166.90164,16.136471],[-173.144531,16.130262],[-174.199219,-10.833306],'+ \
#           '[-180,-10.545911],[-180,-10.545911],[178.671732,-10.480104],[171.5625,-9.968851]]'

polygon = '[[-51.152344,48.922499],[-62.929688,60.239811],[-61.523438,64.396938],[-55.898438,65.730626],[-50.625,61.856149],[-46.054688,58.904646],[-42.539062,58.539595],[-51.152344,48.922499]]'
# [[-71.499,38.805],[-68.071,38.719],[-69.807,41.541],[-71.499,38.805]]


# In[4]:


####################### Let's now look at some metadata queries


# In[5]:


### for profiles containing a certain variable, plot all the profile locations for a time
### period of interest, color coded by source or month of the year
#
##?? later to do for actual data in the profiles
max_ids_in_query = 3;
query_type='global'

startDate='2021-05-01T00:00:00Z'
endDate  ='2021-05-01T12:00:00Z'
#endDate  ='2021-05-02T00:00:00Z'
var_tag  ='doxy' #'temp'

# loop through each day of the period of interest and store the output of each
# d_meta = []

# startDate,endDate,info_to_store,url_prefix,query_type='global',polygon=[],max_ids_in_query=3

# find a list of days in the time range of interest
info_to_store = ['lon', 'lat', 'cols_bySource']

info_ALL = get_metadata_for_var(var_tag=var_tag,startDate=startDate,endDate=endDate,                                 info_to_store=info_to_store,url_prefix=url_prefix,                                 query_type='global',polygon=[],max_ids_in_query=3)

for iind in np.arange(0,len(info_to_store),1):
    exec(info_to_store[iind] + " = []")
    for i in info_ALL:
        if isinstance(i[iind], (int, float)) or isinstance(i[iind], str):
            eval(info_to_store[iind]+'.append(i[iind])')
        elif len(i[iind])>1:
            for j in i[iind]:
                eval(info_to_store[iind]+'.append(j)')        

# print('Start date: '+list_of_days[0])
# print('End date: '+list_of_days[-1])


# In[6]:


dx=10
dy=10

# data_df = create_list_of_df(d_lst_of_lst=d_meta)
        
# plot a map with profile locations: if more than one source, color the dots by source
fig = plt.figure(figsize=(20,7))

ax, gl, usemap_proj = set_up_map(set_extent_info=[min(lon)-dx,max(lon)+dx,min(lat)-dy,max(lat)+dy],
                                 central_long=180,
                                 delta_lonGrid=90,delta_latGrid=45,fnt_size=28)

for i in np.arange(0,len(lon),1):
    plt.plot(lon[i],lat[i],marker='o',color=cols_bySource[i],transform=ccrs.PlateCarree())

# im = plt.scatter(float_events_lon_i,float_events_lat_i,transform=ccrs.PlateCarree(),s=1000,marker='*',
#                         color=my_colors[i], linewidth=3.5) 
            
plt.show()
