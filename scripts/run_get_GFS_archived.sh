#!/bin/bash

INIT=$( cat ${SWIFT_GFS}/controls/namelist | grep "init:" | awk -F: '{print $2}' | tr ',' ' ')

for i in ${INIT}
do
   YYYY=${i:0:4}
   MM=${i:4:2}
   DD=${i:6:2}
   HH=${i:8:2}

   /bin/bash ${SWIFT_GFS}/scripts/get_GFS_archived.sh ${HH} ${YYYY}${MM}${DD}

done
