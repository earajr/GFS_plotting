#!/bin/bash
#
# Script for downloading GFS forecast data (GRIB files).
#

#If GFS_NWP directory does not exist create it and navigate to it

if [ ! -d ${SWIFT_GFS}/GFS_NWP ];
then
   mkdir ${SWIFT_GFS}/GFS_NWP
fi

cd ${SWIFT_GFS}/GFS_NWP

#Date for today
YYYY=`date -u --date='today' +%Y`
MM=`date -u --date='today' +%m`
DD=`date -u --date='today' +%d`
HH=`date -u --date='today' +%H`
YYYYMMDD=`date -u --date='today' +%Y%m%d`

# Depending on time find last viable GFS initialisation time (and date)
if [ "$HH" -gt  3 ] && [ "$HH" -le  9 ]
then
   HH="00"
elif [ "$HH" -gt  9 ] && [ "$HH" -le  15 ]
then
   HH="06"
elif [ "$HH" -gt  15 ] && [ "$HH" -le  21 ]
then
   HH="12"
elif [ "$HH" -gt  21 ] && [ "$HH" -le  23 ]
then
   HH="18"
elif [ "$HH" -le  3 ]
then
   YYYY=`date -u --date='yesterday' +%Y`
   MM=`date -u --date='yesterday' +%m`
   DD=`date -u --date='yesterday' +%d`
   HH="18"
fi

HHcode="t"$HH"0"

#create directory for latest initialisation code
mkdir ${YYYYMMDD}${HH}
cd ${YYYYMMDD}${HH}

# name FTP batch file for latest date and time
FTP_BATCH=get_GFS.batch${YYYYMMDD}${HH}

#Forecast terms (hours) and model resolution (degrees)
FORE_TERMS="000 "$( cat ${SWIFT_GFS}/controls/namelist | grep "fore:" | awk -F: '{print $2}' | tr ',' ' ')
RESOL=0p50

EMAIL="your_email_here"

# echo commands to connect to NCEP to download latest GFS data to the FTP batch file named above make the FTP batch fiel executable and run it
echo ftp -v -n ftp.ncep.noaa.gov \<\< \\FINFTP > $FTP_BATCH
echo user anonymous $EMAIL >> $FTP_BATCH
echo bin >> $FTP_BATCH
echo prompt >> $FTP_BATCH
echo cd pub/data/nccf/com/gfs/prod >> $FTP_BATCH
echo cd gfs.$YYYYMMDD >> $FTP_BATCH
echo cd $HH >> $FTP_BATCH
for f in $FORE_TERMS
do
  echo get gfs.t${HH}z.pgrb2.${RESOL}.f${f} >> $FTP_BATCH
done
echo close >> $FTP_BATCH
echo FINFTP >> $FTP_BATCH

chmod 775 $FTP_BATCH
./$FTP_BATCH

#set counter for attempts to download GFS data
i="0"

# Start loop to check if all requested files are present after first attempt.
while [ ${i} -lt 24 ]
do
   flag="0"
   echo ${flag}
   for f in $FORE_TERMS
   do
      if [ ${flag} == "0" ]
      then
         if ! [[ -f gfs.t${HH}z.pgrb2.${RESOL}.f${f} ]]
         then
            flag="1"
         fi
      fi
   done

   if [ ${flag} == "1" ]
   then
      rm -rf $FTP_BATCH
      echo ftp -v -n ftp.ncep.noaa.gov \<\< \\FINFTP > $FTP_BATCH
      echo user anonymous $EMAIL >> $FTP_BATCH
      echo bin >> $FTP_BATCH
      echo prompt >> $FTP_BATCH
      echo cd pub/data/nccf/com/gfs/prod >> $FTP_BATCH
      echo cd gfs.$YYYYMMDD >> $FTP_BATCH
      echo cd $HH >> $FTP_BATCH
      for f in $FORE_TERMS
      do
         if ! [ -f gfs.t${HH}z.pgrb2.${RESOL}.f${f} ]
         then
            echo get gfs.t${HH}z.pgrb2.${RESOL}.f${f} >> $FTP_BATCH
         fi
      done
      echo close >> $FTP_BATCH
      echo FINFTP >> $FTP_BATCH
      chmod 775 $FTP_BATCH
      sleep 5m
      ./$FTP_BATCH
      i=$(($i + 1))
      echo $i
   else
      i="24"
   fi
done

rm $FTP_BATCH
