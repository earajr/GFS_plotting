#!/bin/bash

FORE_TERMS="000 "$( cat ${SWIFT_GFS}/controls/namelist | grep "fore:" | awk -F: '{print $2}' | tr ',' ' ')

dir=${SWIFT_GFS}/GFS_NWP

for order in ${dir}/tape/*/
do
   order=$( basename ${order} )
   cd ${dir}/tape/${order}
   for fil in ${dir}/tape/${order}/*
   do
      fil=$( basename ${fil} )
      YYYY=${fil:6:4}
      MM=${fil:10:2}
      DD=${fil:12:2}
      HH=${fil:14:2}
  
      mkdir ${dir}/${YYYY}${MM}${DD}${HH}

      for fore in ${FORE_TERMS}
      do
         tar -xvf ${fil} gfs_4_${YYYY}${MM}${DD}_${HH}00_${fore}.grb2 
         mv gfs_4_${YYYY}${MM}${DD}_${HH}00_${fore}.grb2 ${dir}/${YYYY}${MM}${DD}${HH}/gfs.t${HH}z.pgrb2.0p50.f${fore}
      done
   done
   rm -rf ${dir}/tape/${order}
done
