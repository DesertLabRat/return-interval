#!/bin/bash
#for additional fire weather filtering capabilities add Fosberg Fire Weather Index to csv data
DATADIR=./YOUR_DIRECTORY_HERE #location of downloaded wx data csv
OUTDIR=./fosberg #where updated csv with FFWI will be stored

CWD=$(pwd) #stash present working directory in variable

rm -f -r scratch #remove scratch directory and contents
mkdir scratch $OUTDIR 2> /dev/null #create scratch directory

HEADER='date,T,RH,WS,WG,meq,Pign,FFWI,MFFWI' #create header for csv, MODIFY IF VARIABLES DIFFERENT THAN LISTED
UNITS='-,F,%,mph,mph,%,%,-,-' #create units row for csv, MODIFY

for f in $DATADIR/*; do
   STID=`basename -s .csv $f`
   echo $STID
   tail -n +9 $DATADIR/$STID.csv > ./scratch/$STID.csv

   cut -d, -f2-5,7 ./scratch/$STID.csv --output-delimiter="," > ./scratch/${STID}_obsonly.csv

   NUM_LINES=`cat ./scratch/${STID}_obsonly.csv | wc -l`

   rm -f $OUTDIR/${STID}.csv
   fosberg_cli ./scratch/${STID}_obsonly.csv  $OUTDIR/${STID}.csv $NUM_LINES

   sed -i "1i$HEADER" $OUTDIR/${STID}.csv
   sed -i "2i$UNITS" $OUTDIR/${STID}.csv

done

rm -f -r scratch

exit 0
