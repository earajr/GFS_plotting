#!/bin/bash

if [ "$#" -eq  "1" ]
then
   SWIFT_GFS=$1
else
   echo "Attempting to use existing SWIFT_GFS environment variable"
fi

#Date for today (format YYYYMMDD)
YYYY=`date -u --date='today' +%Y`
MM=`date -u --date='today' +%m`
DD=`date -u --date='today' +%d`
HH=`date -u --date='today' +%H`
YYYYMMDD=`date -u --date='today' +%Y%m%d`

if [ "$HH" -ge  3 ] && [ "$HH" -lt  9 ] 
then
   HH="00"
elif [ "$HH" -ge  9 ] && [ "$HH" -lt  15 ]
then
   HH="06"
elif [ "$HH" -ge  15 ] && [ "$HH" -lt  21 ]
then
   HH="12"
elif [ "$HH" -ge  21 ] && [ "$HH" -lt  23 ]
then
   HH="18"
elif [ "$HH" -lt  3 ]
then
   YYYY=`date -u --date='yesterday' +%Y`
   MM=`date -u --date='yesterday' +%m`
   DD=`date -u --date='yesterday' +%d`
   HH="18"
fi

sed -i "s/init:.*/init: $YYYY$MM$DD$HH/g" ${SWIFT_GFS}/controls/namelist

