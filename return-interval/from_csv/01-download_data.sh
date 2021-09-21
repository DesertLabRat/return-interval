#!/bin/bash

DLSTART=202101010000
DLEND=202108152359

VARS='air_temp,relative_humidity,wind_speed,wind_direction,wind_gust,precip_accum'

STIDS='NV019' #2021 FMS
#COUNTY='chelan'
#STATE='wa'

rm -r -f NVE_081721
mkdir NVE_081721 2> /dev/null

for STID in $STIDS; do
   wget -O ./NVE_081721/$STID.csv "https://api.mesowest.net/v2/stations/timeseries?stid=$STID&start=$DLSTART&end=$DLEND&vars=$VARS&timeformat=%Y-%m-%d_%H:%M&output=csv&units=speed|mph,precip|in,english&qc_flags=off&token=74df9291a38448fdbedcd394ed889b24&"
#   wget -O test_CA.csv  "https://api.mesowest.net/v2/stations/timeseries?state=ca&start=$DLSTART&end=$DLEND&vars=$VARS&timeformat=%Y-%m-%d_%H:%M&output=csv&units=speed|mph,precip|in,english&qc_flags=off&token=74df9291a38448fdbedcd394ed889b24&"
done

exit 0
