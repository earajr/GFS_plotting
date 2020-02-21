#!/bin/bash

if [ "$#" -eq  "1" ]
then
   SWIFT_GFS=$1
else
   echo "Attempting to use existing SWIFT_GFS environment variable"
fi

cd ${SWIFT_GFS}/python

export SWIFT_GFS=${SWIFT_GFS}
source ~/anaconda3/etc/profile.d/conda.sh #<-- Modify this line if you have anaconda installed anywhere but your home directory.

conda activate pyn_env

python3 plot.py 4

