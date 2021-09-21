#!/bin/bash

DATADIR=./IPC_recur_int
OUTDIR=./fosberg

CWD=$(pwd)

rm -f -r scratch
mkdir scratch $OUTDIR 2> /dev/null

#STATIONS='CRZC1 ATRC1 TR173'
#STATIONS='KYCN2'
#STATIONS='KTVL'

HEADER='date,T,RH,WS,WG,meq,Pign,FFWI,MFFWI'
UNITS='-,F,%,mph,mph,%,%,-,-'

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
