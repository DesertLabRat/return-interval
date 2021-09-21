#!/usr/bin/env python
# coding: utf-8

#import libraries
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

#path to .csv files for analysis
path, dirs, files = next(os.walk("./YOUR_FILE_PATH_HERE"))
file_count = len(files) #count number of files 
print(file_count) #and return

Tall = [0.25, 0.5, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50] #return intervals of interest, ex: 3 months, 6 months, 1 yr, 2 yr, etc.

#import csv into dataframe
for i in range(file_count): #for each file in path do this
    #print(i)
    first = files[i][:1] #create variable for first letter of filename
        
    if first == 'K': #if first is a 'K', then station is NWS/FAA at an airport and ID is only 4 characters
        print('airport')
        name = files[i][:4]
    else: #station is RAWS or some other network and ID is 5 characters
        print('raws')
        name = files[i][:5]
        
    if os.stat(path+files[i]).st_size == 0: #if csv is empty, we want to know for troubleshooting
        print('blank csv: ', name)
    else: #otherwise here we go....
        temp_df = pd.read_csv("./YOUR_FILE_PATH_HERE"+files[i], skiprows=2) #read csv into dataframe format
        #print(temp_df.shape)
        result = temp_df.shape[1] #stash number of columns in dataframe into a variable
        #print(result)
        
        if result == 10: #if there are 10 columns, MODIFY IF DIFFERENT WX VARIABLES REQUESTED
            print('artifact')
            temp_df.columns=['Date','T','RH','WS','WG', 'meq', 'Pign', 'FFWI', 'MMFWI','fact']
            del temp_df['fact']
        elif result == 9: #otherwise, MODIFY
            print('no artifact')
            temp_df.columns=['Date', 'T', 'RH', 'WS', 'WG', 'meq', 'Pign', 'FFWI', 'MMFWI']
    #data cleaning section       
    try:
        del temp_df['Pign'] #remove extraneous columns
        del temp_df['MMFWI']
        
        temp_df['Date'] = pd.to_datetime(temp_df['Date'], format='%Y-%m-%d_%H:%M') #change datatype of Date column
        df1 = temp_df[temp_df['FFWI'].between(0,35)] #filter by FFWI
        df2 = df1[df1['WG'].between(0,80)] #filter by Wind Gust
        df3 = df2.sort_values(by=['WG'], ascending=False) #sort data by Wind Gust, high to low
        n = df3.shape[0] #stash number of rows in variable
        df3.insert(0, 'Rank', range(1, 1+n)) #insert Rank column in position 0 ranging from 1 to 1+n
    #these are exceptions I routinely ran into creating this script    
    except IndexError:
        print('triggered IndexError: ', name)
    except KeyError:
        print('triggered KeyError: ', name)
    #intermediate check that nothing screwy got inserted or deleted
    if temp_df.shape[1]+1 != df3.shape[1]:
        print('cleaned df off by more than 1')
    else:
        pass
    #data analysis section
    try:
        Dmin = min(df3['Date']) #stash earliest Date
        Dmax = max(df3['Date']) #stash last Date
        Y = round((Dmax - Dmin) / np.timedelta64(1, 'Y'), 0) #calculate this station's period of record based on Dmin and Dmax
        #print(Y)
        df3.insert(8, 'Return Interval', (Y + 1) / df3['Rank']) #insert column determining Wind Gust Return Interval based on period of record and Rank
            
        for count, value in enumerate(Tall, start=0): #for the Return Intervals of interest [Tall]
            #print('count: ', count, 'and value: ', value)
            if value <= Y: #if the value of interest is within the station's period of record
                if count == 0: #and if count is zero
                    included = [value] #initiate list of values within the period of record
                    excluded = [] #initiate list of values external to period of record
                else: #otherwise
                    included.append(value) #add value to existing list
            else: #otherwise
                if count == 0: #very first csv data is outside period of record
                    excluded = [value] #create list of values external to period of record
                else: #otherwise
                    excluded.append(value) #add value to existing list
        #print('included: ', included)
        idx1 = 0 #create counter variable for inside next for loop
        for value in included:
            y_interp = interp1d(df3['Return Interval'], df3['WG'], kind='linear', fill_value='extrapolate') #linearly interpolate Wind Gust value from Return Interval for missing data
            outcome = y_interp(value).round(0) #perform interpolation and round to zero decimal places
            #print(outcome)
            if idx1 == 0: #on first iteration
                gSpd_arr = [outcome] #create list
            else: #every other iteration
                gSpd_arr.append(outcome) #add to list
            
            idx1 = idx1 + 1 #increase counter
        #print('gSpd_arr:', gSpd_arr)
        
        eis = pd.DataFrame(gSpd_arr) #convert list to dataframe
        eis.insert(0, 'Return Interval', included) #insert Return Interval column at position zero
        eis.columns = ['RI (yrs)', 'Gust (mph)'] #assign column labels
        #display(eis.head())
        #display(eis.tail())
        
        #export to csv
        eis.to_csv('./YOUR_OUTPUT_PATH_HERE'+name+'.csv', sep=',', header=True, index=False)
    except ValueError:
        print('triggered ValueError: ', name)
        
print('End of script')        
