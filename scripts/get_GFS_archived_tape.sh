#!/bin/bash
#
# Script for downloading archived GFS forecast data (GRIB files) from tape
#

# all script arguments will be treated as orders to be downloaded from the HAS tape storage retreival system
orders=$*

if [ ! -d ${SWIFT_GFS}/GFS_NWP/tape ];
then
   mkdir -p ${SWIFT_GFS}/GFS_NWP/tape
fi

cd ${SWIFT_GFS}/GFS_NWP/tape

for order in ${orders}
do
   
   wget -erobots=off -nv -m -np -nH --cut-dirs=3 --reject "index.html*" https://www1.ncdc.noaa.gov/pub/has/model/${order}/

done
