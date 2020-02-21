#!/bin/bash


tim_mins=4320

if [ "$#" -eq  "1" ]
then
   SWIFT_GFS=$1
else
   echo "Attempting to use existing SWIFT_GFS environment variable"
fi

cd ${SWIFT_GFS}/GFS_NWP

for dir in */
do
   if ! [ $( basename ${dir} ) == "tape" ]
   then
      find . -mmin +${tim_mins} -type d -name "$( basename ${dir} )" -exec rm {} \;
   fi
done

cd ${SWIFT_GFS}/python

find . -mmin +${tim_mins} -type l -name "*.nc" -exec unlink {} \;

cd ${SWIFT_GFS}/MARTIN

find . -mindepth 3 -maxdepth 3 -type d -mmin +${tim_mins} -exec rm {} \;
