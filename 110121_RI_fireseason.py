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
import param
import calendar


# In[2]:


Tall = [0.25, 0.5, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50] #return intervals of interest


# In[3]:


#path to .csv files for analysis
root, dirs, files = next(os.walk("./Desktop/ubuntu_share/IPC/B2H_1025/originals/"))
file_count = len(files) #count number of files 
print('file count: ', file_count) #and return


# In[30]:


def loadFiles(i, files):
    first = files[i][:1]        
    if first == 'K':
        #print('airport')
        name = files[i][:4]
    else:
        #print('raws')
        name = files[i][:5]
#print(name)
    if os.stat(root+files[i]).st_size == 0:
        print('blank csv: ', name)
    else:
        temp_df = pd.read_csv(root+files[i], skiprows=8, header=None) #read .csv to dataframe format REMOVED skiprow=2 070821
    if temp_df.shape[1] == 7:
        temp_df.columns=['STID', 'Date','T','RH','WS','WDir', 'WG']
    elif temp_df.shape[1] == 8:
        temp_df.columns=['STID', 'Date','T','RH','WS','WDir', 'WG', 'PA']
    else:
        pass
    return temp_df
    
def fosberg(temp_df):    

    conditions = [(temp_df['RH'] < 10),
                  (temp_df['RH'] >= 10) & (temp_df['RH'] < 50),
                  (temp_df['RH'] >= 50)]
            
    values = [0.03 + 0.28 * temp_df['RH'] - 0.00058 * temp_df['RH'] * temp_df['T'],
              2.23 + 0.16 * temp_df['RH'] - 0.0148 * temp_df['T'],
              21.1 - 0.4944 * temp_df['RH'] + 0.00557 * (temp_df['RH']**2) - 0.00035 * temp_df['RH'] * temp_df['T']]
      
    temp_df['Meq'] = np.select(conditions, values)
    #temp_df['Meq'] = temp_df['Meq'].map('{:.2f}'.format)
    temp_df['eta'] = 1 - 2 * (temp_df['Meq']/30) + 1.5 * ((temp_df['Meq']/30)**2) - 0.5 * ((temp_df['Meq']/30)**3)
    #temp_df['eta'] = temp_df['eta'].map('{:.2f}'.format)
    temp_df['FFWI'] = temp_df['eta'] * ((1 + temp_df['WS']**2)**0.5) / 0.3002
    #temp_df['FFWI'] = temp_df['FFWI'].map('{:.2f}'.format)
    #print(temp_df.head())
    
    return(temp_df)

class ParamClass(param.Parameterized):
    a = param.Integer(5, bounds=(1,11), doc='first month')
    b = param.Integer(11, bounds=(2,12), doc='second month')
    title = param.String(default='setting fire season', doc='Title for result')
    
    def __call__(self):
        return self.title + ": " + str(self.a) + ', ' + str(self.b)
    
def setFireSeason():
    fs1 = int(input('Start month: '))
    fs2 = int(input('End month: '))
    #print(type(fs2))
    o1 = ParamClass(a=fs1, b=fs2)
    
    return o1

def makeList(new):
    frames = [new.T]
    labels = [name]        
    return (frames, labels)

def addList(new, frames, labels):
    frames.append(new.T)
    labels.append(name)
    return (frames, labels)

def calcRI(name, getback, fss, fse):
    #name = getback.iloc[1,0]
    getback['Date'] = pd.to_datetime(getback['Date'], format='%Y-%m-%d_%H:%M')
            
    fsFilter = getback[(getback['Date'].dt.month > 5) | (getback['Date'].dt.month < 10)]
                              
    df1 = fsFilter[fsFilter['FFWI'].between(0,35)]
    df2 = df1[df1['WS'].between(0,80)]
    df3 = df2.sort_values(by=['WS'], ascending=False)
    n = df3.shape[0]
    df3.insert(0, 'Rank', range(1, 1+n))               
        
    if temp_df.shape[1]+1 != df3.shape[1]:
        print('cleaned df off by more than 1')
    else:
        pass
    try:
        Dmin = min(df3['Date'])
        Dmax = max(df3['Date'])
        Y = round((Dmax - Dmin) / np.timedelta64(1, 'Y'), 0)
        print('Period of record: ', Y)
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
        idx1 = 0
        for value in included:
            y_interp = interp1d(df3['Return Interval'], df3['WS'], kind='linear', fill_value='extrapolate')
            outcome = y_interp(value).round(0)
            #print(outcome)
            if idx1 == 0:
                gSpd_arr = [outcome]
            else:
                gSpd_arr.append(outcome)
            idx1 = idx1 + 1       

        eis = pd.DataFrame(gSpd_arr)
        eis.insert(0, 'Return Interval', included)
        eis.columns = ['RI (yrs)', 'Wind Speed (mph)']
    except ValueError:
        print('triggered ValueError: ', name)
    return eis
    print('End of calcRI()')


# In[32]:


for i in range(file_count): #for each file up to the total number of files do
    name = files[i][:5]
    print(name)
    temp_df = loadFiles(i, files)
    getback = fosberg(temp_df)
    #display(getback.tail())
    if i == 0:
        r = setFireSeason()
        r()
        fss = r.a
        fse = r.b
    else:
        pass
    t = calcRI(name, getback, fss, fse)
    #display(t.head())
    new = t.copy()
    new.set_index(['RI (yrs)'], inplace=True)
    if i == 0 :
        frames = [new.T]
        labels = [name]
    else:
        frames.append(new.T)
        labels.append(name)

MUTANT = reduce(lambda x,y: x.append(y, ignore_index=True), frames)
MUTANT.index = labels
    
MUTANT.to_csv('./Desktop/ubuntu_share/IPC/testing/'+name+'.csv', sep=',', header=True, index=True) 
print('Done running')

