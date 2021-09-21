#!/bin/bash

DLSTART=199701010000 #start date for data download, format %Y%m%d%H%M
DLEND=202108310000 #end date for data download, format %Y%m%d%H%M

VARS='air_temp,relative_humidity,wind_speed,wind_direction,wind_gust,precip_accum' #variables to be downloaded

STIDS='SMDC1 HMDC1' #list of station IDs to be donwloaded, example: Stampede and Homewood RAWS

rm -r -f YOUR_DIRECTORY_HERE #remove previously downloaded directory and contents
mkdir YOUR_DIRECTORY_HERE 2> /dev/null #create directory for api request downloads

for STID in $STIDS; do
   wget -O ./YOUR_DIRECTORY_HERE/$STID.csv "https://api.mesowest.net/v2/stations/timeseries?stid=$STID&start=$DLSTART&end=$DLEND&vars=$VARS&timeformat=%Y-%m-%d_%H:%M&output=csv&units=speed|mph,precip|in,english&qc_flags=off&token=74df9291a38448fdbedcd394ed889b24&"
   #see Synoptic Labs for api request options: https://developers.synopticdata.com/mesonet/
done

exit 0
