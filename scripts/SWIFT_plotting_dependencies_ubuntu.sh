#!/bin/bash

SWIFT_GFS_path=${SWIFT_GFS}/install

if [ ! -d ${SWIFT_GFS_path} ]
then
   mkdir -p ${SWIFT_GFS_path}
fi

sudo apt update -y
sudo apt-get install -y build-essential 
sudo apt-get install -y ftp wget unzip m4 curl libcurl4-openssl-dev cmake python-dev python3-dev libopenjp2-tools zlib1g zlib1g-dev imagemagick gcc-6-base libgfortran3

#   download, compile and install --> hdf5
cd $SWIFT_GFS_path
wget -O hdf5-1.10.5.tar.gz 'https://www.hdfgroup.org/package/hdf5-1-10-5-tar-gz/?wpdmdl=13571&refresh=5e3961217b7321580818721'
tar -xzvf hdf5-1.10.5.tar.gz
cd hdf5-1.10.5
./configure --enable-threadsafe --with-pthread=/usr --with-zlib=/usr --enable-unsupported --prefix=/usr
make && make check && sudo make install
#
#   download, compile and install --> netCDF
cd $SWIFT_GFS_path
wget https://www.unidata.ucar.edu/downloads/netcdf/ftp/netcdf-c-4.7.3.tar.gz
tar -xzvf netcdf-c-4.7.3.tar.gz
c
netcdf-c-4.7.3
cmake -G "Unix Makefiles" -DENABLE_NETCDF_4=ON -DENABLE_DAP=ON -DBUILD_SHARED_LIBS=ON -DENABLE_TESTS=ON  -DCMAKE_INSTALL_PREFIX=/usr  ./
make && sudo make install

# incall ncl 
sudo apt-get install -y libeccodes-dev jasper cdo

cd ${SWIFT_GFS_path}
wget https://www.earthsystemgrid.org/dataset/ncl.662.dap/file/ncl_ncarg-6.6.2-Debian9.8_64bit_gnu630.tar.gz
sudo tar -xzvf ncl_ncarg-6.6.2-Debian9.8_64bit_gnu630.tar.gz -C /usr

# Ensure shared libraries are wired up
sudo ldconfig
