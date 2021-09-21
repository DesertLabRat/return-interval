#!/usr/bin/env python
# coding: utf-8

# In[1]:


#import libraries
import matplotlib.pyplot as plt
import os
import pandas as pd
import math
import numpy as np
from scipy.interpolate import interp1d
import urllib
from urllib.parse import urlencode, quote_plus
import json
from datetime import date, datetime, timedelta
import itertools
from functools import reduce


# In[2]:


#path to .csv files for analysis
path, dirs, files = next(os.walk("./Desktop/ubuntu_share/IPC/fosberg/"))
file_count = len(files) #count number of files 
print(file_count) #and return


# In[3]:


Tall = [0.25, 0.5, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50] #return intervals of interest


# In[10]:


#import .csv into dataframe
for i in range(file_count): #for each file up to the total number of files do
    #print(i)
    first = files[i][:1]
        
    if first == 'K':
        print('airport')
        name = files[i][:4]
    else:
        print('raws')
        name = files[i][:5]
        
    if os.stat(path+files[i]).st_size == 0:
        print('blank csv: ', name)
    else:
        temp_df = pd.read_csv("./Desktop/ubuntu_share/IPC/fosberg/"+files[i], skiprows=2) #read .csv to dataframe format REMOVED skiprow=2 070821
        #print(temp_df.shape)
        result = temp_df.shape[1]
        #print(result)
        
        if result == 10:
            print('artifact')
            temp_df.columns=['Date','T','RH','WS','WG', 'meq', 'Pign', 'FFWI', 'MMFWI','fact']
            del temp_df['fact']
        elif result == 9:
            print('no artifact')
            temp_df.columns=['Date', 'T', 'RH', 'WS', 'WG', 'meq', 'Pign', 'FFWI', 'MMFWI']
            
    try:
        del temp_df['Pign']
        del temp_df['MMFWI']
        
        temp_df['Date'] = pd.to_datetime(temp_df['Date'], format='%Y-%m-%d_%H:%M')
        df1 = temp_df[temp_df['FFWI'].between(0,35)]
        df2 = df1[df1['WG'].between(0,80)]
        df3 = df2.sort_values(by=['WG'], ascending=False)
        n = df3.shape[0]
        df3.insert(0, 'Rank', range(1, 1+n))
        
    except IndexError:
        print('triggered IndexError: ', name)
    except KeyError:
        print('triggered KeyError: ', name)
        
    if temp_df.shape[1]+1 != df3.shape[1]:
        print('cleaned df off by more than 1')
    else:
        pass
    
    try:
        Dmin = min(df3['Date'])
        Dmax = max(df3['Date'])
        Y = round((Dmax - Dmin) / np.timedelta64(1, 'Y'), 0)
        #print(Y)
        df3.insert(8, 'Return Interval', (Y + 1) / df3['Rank'])
            
        for count, value in enumerate(Tall, start=0):
            #print('count: ', count, 'and value: ', value)
            if value <= Y:
                if count == 0:
                    included = [value]
                    excluded = []
                else:
                    included.append(value)
            else:
                if count == 0:
                    excluded = [value]
                else:
                    excluded.append(value)
        #print('included: ', included)
        idx1 = 0
        for value in included:
            y_interp = interp1d(df3['Return Interval'], df3['WG'], kind='linear', fill_value='extrapolate')
            outcome = y_interp(value).round(0)
            #print(outcome)
            if idx1 == 0:
                gSpd_arr = [outcome]
            else:
                gSpd_arr.append(outcome)
            
            idx1 = idx1 + 1
        #print('gSpd_arr:', gSpd_arr)
        
        eis = pd.DataFrame(gSpd_arr)
        eis.insert(0, 'Return Interval', included)
        eis.columns = ['RI (yrs)', 'Gust (mph)']
        #display(eis.head())
        #display(eis.tail())
        
        #export to csv
        eis.to_csv('./Desktop/ubuntu_share/IPC/out/'+name+'.csv', sep=',', header=True, index=False)
    except ValueError:
        print('triggered ValueError: ', name)
        
print('End of script')        

