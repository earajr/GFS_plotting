#!/bin/bash

SWIFT_GFS_path=~/SWIFT_GFS_plotting/install

if [ ! -d ${SWIFT_GFS_path} ]
then
   mkdir -p ${SWIFT_GFS_path}
fi

sudo yum install epel-release
sudo yum groupinstall "Development tools"
sudo yum install ftp wget unzip m4 curl libcurl-devel cmake3 python-devel python3-devel openjpeg2-tools zlib zlib-devel

#   download, compile and install --> hdf5
cd $SWIFT_GFS_path
wget -O hdf5-1.10.5.tar.gz 'https://www.hdfgroup.org/package/hdf5-1-10-5-tar-gz/?wpdmdl=13571&refresh=5e3961217b7321580818721'
tar -xzvf hdf5-1.10.5.tar.gz
cd hdf5-1.10.5
./configure --enable-threadsafe --with-pthread=/usr --with-zlib=/usr --enable-unsupported --prefix=/usr
make && sudo make install

#   download, compile and install --> netCDF
cd $SWIFT_GFS_path
wget https://www.unidata.ucar.edu/downloads/netcdf/ftp/netcdf-c-4.7.3.tar.gz
tar -xzvf netcdf-c-4.7.3.tar.gz
cd netcdf-c-4.7.3
cmake3 -G "Unix Makefiles" -DENABLE_NETCDF_4=ON -DENABLE_DAP=ON -DBUILD_SHARED_LIBS=ON -DENABLE_TESTS=ON  -DCMAKE_INSTALL_PREFIX=/usr  ./
make && sudo make install

sudo yum install ncl eccodes-devel jasper

#   download, compile and install --> cdo
cd $SWIFT_GFS_path
wget https://code.mpimet.mpg.de/attachments/download/16435/cdo-1.9.3.tar.gz
tar -xvzf cdo-1.9.3.tar.gz
cd cdo-1.9.3
./configure --with-grib_api=no --with-netcdf=yes --with-hdf5=yes --with-eccodes=yes --with-jasper=yes --with-zlib=yes -prefix=/usr
make && sudo make install

# Ensure shared libraries are wired up
sudo ldconfig
