#!/bin/bash
#
# Script for downloading archived GFS forecast data (GRIB files).
#

#Check if there are 2 arguments for the get_GFS_archived.sh script, if not then this error will be displayed and the script will exit.
if [ $# -lt 2 ]
then
  echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
  echo "Usage: ./get_GFS HH DATE"
  echo "       HH is the required cycle runtime: 00 06 12 18"
  echo "       DATE is date for wich forecast is required e.g. 20180601"
  echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
  exit 1
fi

HH=$1
YYYYMMDD=$2

#If GFS_NWP directory does not exist create it and navigate to it

if [ ! -d ${SWIFT_GFS}/GFS_NWP ];
then
   mkdir ${SWIFT_GFS}/GFS_NWP
fi

cd ${SWIFT_GFS}/GFS_NWP

#create directory for latest initialisation code
mkdir ${YYYYMMDD}${HH}
cd ${YYYYMMDD}${HH}

#Forecast terms (hours)
FORE_TERMS="000 "$( cat ${SWIFT_GFS}/controls/namelist | grep "fore:" | awk -F: '{print $2}' | tr ',' ' ')

#Date breakdown (format YYYYMMDD)
YYYY=${YYYYMMDD:0:4}
MM=${YYYYMMDD:4:2}

#Connect to NCEP to download NWP-GFS files
missing_flag="0"
for f in $FORE_TERMS
do
   if curl --no-keepalive --output /dev/null --silent --head --fail "ftp://nomads.ncdc.noaa.gov/GFS/Grid4/${YYYY}${MM}/${YYYYMMDD}/gfs_4_${YYYYMMDD}_${HH}00_${f}.grb2"
   then
      curl --no-keepalive "ftp://nomads.ncdc.noaa.gov/GFS/Grid4/${YYYY}${MM}/${YYYYMMDD}/gfs_4_${YYYYMMDD}_${HH}00_${f}.grb2" -o "gfs.t${HH}z.pgrb2.0p50.f${f}"
   elif curl --no-keepalive --output /dev/null --silent --head --fail curl "https://www.ncei.noaa.gov/thredds/fileServer/gfs-004-files/"$YYYY$MM"/"$YYYYMMDD"/gfs_4_"$YYYYMMDD"_"$HH"00_"$f".grb2"
   then
      curl --no-keepalive "https://www.ncei.noaa.gov/thredds/fileServer/gfs-004-files/"$YYYY$MM"/"$YYYYMMDD"/gfs_4_"$YYYYMMDD"_"$HH"00_"$f".grb2" -o "gfs.t${HH}z.pgrb2.0p50.f${f}"
   else
      echo "gfs.t${HH}z.pgrb2.0p50.f${f} not in archive"
      missing_flag="1"
   fi
done

if [ ${missing_flag} == "1" ]
then
   echo ""
   echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
   echo "Some of the files you requested are not available from"
   echo "the http or ftp archives supplied by NOAA. To download"
   echo "GFS files manually visit"
   echo "https://www.ncdc.noaa.gov/data-access/model-data/model-datasets/global-forcast-system-gfs"
   echo "and select HAS from the Data Access Links section of"
   echo "the GFS Forecasts table. You can then create and order"
   echo "that you can download once the data had been retrieved"
   echo "from NOAAs elastic tape storage."
   echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
   echo ""
   rm -rf ${SWIFT_GFS}/GFS_NWP/${YYYYMMDD}${HH}
fi
