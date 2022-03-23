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
import time

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
from utilities_NSF_EC2022 import create_list_of_days,string_of_ids,                                     check_list_of_list,check_list, check_list_of_dict,                                     get_info_from_df,get_data_for_var,                                     check_error_message #,get_metadata_for_var
# for data visualization
from utilities_NSF_EC2022 import set_up_map,select_color_byList,plot_locations_withColor


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
# to add based on data availability
#
lon_min = -50
lon_max = 16
lat_min = -31
lat_max = -25
polygon = '[['+str(lon_min)+','+str(lat_max)+'],['+str(lon_min)+','+str(lat_min)+'],['+            str(lon_max)+','+str(lat_min)+'],['+str(lon_max)+','+str(lat_max)+'],['+str(lon_min)+','+str(lat_max)+']]'


# In[4]:


startDate = '2011-09-25T00:00:00Z'
endDate   = '2011-11-01T12:00:00Z'
# endDate   = '2011-11-01T12:00:00Z'
var_tag   = 'temp' #,temp_ctd,temp_btl
presRange = '3000,3150'

query_type = 'inPolygon'

info_to_store = ['lon','lat','date','cols_bySource']


# In[5]:


info_metaALL        = get_data_for_var(var_tag=var_tag,startDate=startDate,endDate=endDate,                             url_prefix=url_prefix,                             query_type=query_type,polygon=polygon,presRange='',dt_tag='10d',                            getData=False,writeTag=True)
info_metaALL        = get_data_for_var(var_tag=var_tag,startDate=startDate,endDate=endDate,                             url_prefix=url_prefix,                             query_type=query_type,polygon=polygon,presRange=presRange,dt_tag='10d',                             getData=False,writeTag=True)

info_select_dict = get_info_from_df(df=pd.DataFrame(info_metaALL),info_to_store=info_to_store)
plot_locations_withColor(lon=info_select_dict['lon'],lat=info_select_dict['lat'],                          cols=info_select_dict['cols_bySource'],dx=30,dy=30,central_long=-30,                          markersz=10,fnt_size=28)


# In[6]:


info_ALL        = get_data_for_var(var_tag=var_tag,startDate=startDate,endDate=endDate,                             url_prefix=url_prefix,                             query_type=query_type,polygon=polygon,presRange='',dt_tag='10d',                             getData=True,writeTag=True)
info_ALL        = get_data_for_var(var_tag=var_tag,startDate=startDate,endDate=endDate,                             url_prefix=url_prefix,                             query_type=query_type,polygon=polygon,presRange=presRange,dt_tag='10d',                             getData=True,writeTag=True)

info_select_dict = get_info_from_df(df=pd.DataFrame(info_ALL),info_to_store=info_to_store)
plot_locations_withColor(lon=info_select_dict['lon'],lat=info_select_dict['lat'],                          cols=info_select_dict['cols_bySource'],dx=30,dy=30,central_long=-30,                          markersz=10,fnt_size=28)


# In[7]:


#### for each of the points along a woce line, plot nearby Argo profiles


# In[8]:


# dictOne = {"Column A":[1, 2],"Column B":[4, 5, 6],"Column C":[7]}
# dictTwo = {"Column A":[1, 2],"Column B":[4, 5, 6],"Column D":[4, 5, 6,4, 5, 6]}
# lst = [dictOne,dictTwo]
# pd.DataFrame(lst)


# In[ ]:




