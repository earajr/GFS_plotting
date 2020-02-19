# SWIFT GFS python plotting code.

This document gives an overview of the setup required to run the SWIFT GFS python plotting code originally written by Alexander Roberts (NCAS and University of Leeds). This document will: (1) introduce the general structure of the code, (2) explain the supporting scripts including system requirements, (3) explain individual python plotting scripts and (4) describe the operation of the scripts together. This should give all the details needed to understand this repository and allow you to download and use the code for yourself.

## GitHub Repository

To begin with you should first clone the GitHub repository, to do this navigate to your home directory (or where ever you wish to put the cloned repository) and run the following command.


`git clone git@github.com:earajr/GFS_plotting.git`


This should create a new directory named `GFS_plotting`. If for any reason this does not work then you click the "clone or download" button above and select to download a zipped version. Once downloaded you can unzip the repository and rename the directory from `GFS_plotting-master` to `GFS_plotting`. This is the exact same repository that you get by using the command above.


Once you have created this directory you should set an environment variable in your .bashrc file that describes the location of this directory. This will be important when running scripts later on. Open your .bashrc file and specify the location of your new directory as the environment variable `SWIFT_GFS`.


`export SWIFT_GFS=full/path/to/GFS_plotting`

Once you have modified your .bashrc source it to update your current console.

`source ~/.bashrc`

## Dependencies

There are a number of dependencies that you will need to make sure are installed properly on your system. Within the repository (in the scripts directory) there is a `SWIFT_plotting_dependencies.sh` script which will install all the software that is required. This has been tested on a clean CentOS 7 install and works. If you are using a different Linux OS then you will have to modify the script accordingly. Despite the install procedure being different, the dependencies will be the same. The software that is installed is detailed below.

### epel repository (CentOS, Red Hat Enterprise Linux (RHEL), Scientific Linux, Oracle Linux)

This is the Extra Packages for Enterprise Linux (EPEL) repository of packages you will have to activate before you can install certain pieces of software using yum in CentOS, (this is not available in other Linux OSs, if any of the software installed using yum is not available for your OS e.g. using apt get in Ubuntu then you will have to find another method of installation such as building the code from source).

### "Development tools"

This group install will install a number of useful (and required) packages and make sure you have the compilers you will need to build the rest of the required software. The equivalent package in Ubuntu is “build-essentials”.

### Other software required
**ftp**  
**wget**  
**unzip**  
**m4**  
**curl**  
**libcurl-devel**  
**cmake3**  
**python-devel**  
**python3-devel**  
**openjpeg2-tools**  
**zlib**  
**zlib-devel**  
**hdf5** (with threadsafe and unsupported enabled to allow for using POSIX thread, also built with zlib)  
**netCDF** (with netCDF 4 enabled)  
**ncl**  
**eccodes-devel**  
**jasper**  
**cdo**  

### Running the script

When running the `SWIFT_plotting_dependencies.sh` script first make sure that you have internet access and that the script is executable.

`chmod +x SWIFT_plotting_dependencies.sh`

The script will require you to have sudo access, however **do not run the script using sudo**. This affects the make commands and can cause the install of several packages to fail. The script will create an `install` directory in the `GFS_plotting` directory you created earlier (**you must have set the location of this directory as an environment variable and sourced your updated .bashrc**).

`./SWIFT_plotting_dependencies.sh`

While running there will be several prompts, some of these will ask for your sudo password while others will merely ask you to agree to the installations being made. As the script can take quite a while to install everything you might be asked for your sudo password more than once. The installation of hdf5 in particular takes a while, try to remember to keep an eye out for the sudo password prompt, if you leave it too long the script times out and quits without completing.

## Python
To run the python code there are a number of python library dependencies. To make sure that we have everything that we need it makes sense to set up a virtual environment in which to run the plotting code. Here I will describe how to do this using anaconda. However, if you are familiar and confident with another method of setting up a virtual environment feel free to do that.

### anaconda
To download the anaconda installer script visit the anaconda website (https://www.anaconda.com/). In the top right corner you should see a link labelled “Download”. Click on this link and scroll down. You should see two options to download the python 3 and python 2 versions of anaconda. Select the python 3 version and download the installer.

Navigate to the location of the installer script. Before being able to install anaconda you need to make sure that the script is executable.

`chmod +x Anaconda3-2019.10-Linux-x86_64.sh`

Now run the install script.

`./Anaconda3-2019.10-Linux-x86_64.sh`

```
Welcome to Anaconda3 2019.10

In order to continue the installation process, please review the license
agreement.
Please, press ENTER to continue
>>>
===================================
Anaconda End User License Agreement
===================================
…
…
…
…
Do you accept the license terms? [yes|no]
```

Accept the license terms and select a location to install anaconda. If you are happy for anaconda to be installed in your home directory just press ENTER to confirm the location.

Anaconda will now begin to unpack into your chosen directory. Once complete you will be asked whether you wish to initialize anaconda. Enter yes and your .bashrc file will be updated to include the conda initialisation. For this to take effect you will have to open a new console window or source your .bashrc from your current window.

`source ~/.bashrc`

### pyn_env environment

We could go through the process of setting up a conda environment from scratch. However, instead of doing this I have created a .yml environment file that will replicate the conda environment that I use to run the GFS plotting routines (in the `scripts` directory). This is a simple way of replicating a conda environment so that it should work in exactly the same way as the operational plotting for SWIFT. The .yml file (`pyn_env.yml`) can be used to create a conda environment called pyn_env (pyngl environment). This will provide all the python packages required to create the GFS images.

`conda create -f pyn_env.yml`

## GFS plotting scripts

The python plotting scripts can be found in the python directory of your downloaded repository. Broadly speaking these are split into 2 different types of scripts: (1) job creation and parallelisation and (2) data manipulation and image production. These are discussed in more detail below.

### plot.py

The `plot.py` script interrogates the control files (namelist and domains files that can be found in the `controls` directory) to find the initialisation times, multiple and single level variables to be plotted, regions and forecast times. From this information the first step is to produce all the output directories to receive the imagery that is produced. The location of the output is dictated by the `SWIFT_GFS` environment variable set earlier. The next step is to generate a list of dictionaries that contain the commands and arguments that are to be run to produce the GFS imagery. Once complete this list of commands is then passed to a “worker” command via a threadpool. This submits the commands created earlier in parallel to allow for more rapid generation of imagery. The number of cores for the python code to run on is automatically set to 4, however this can be overridden by providing the number of cores you wish to use as an argument to the `plot.py` script.

### Individual plotting scripts

The python scripts that are invoked by `plot.py` are similarly found in the `python` directory. These are a mixture of scripts that work to produce images for a wide variety of forecast relevant meteorological fields. It is imagined that future development of scripts of this type (produced by editing existing code) will allow the plotting of a wider variety of useful metrics. Once created a script of this type can be added to the namelist by adding the name of the script (minus the .py) to the appropriate part of the namelist file. Scripts that work to plot a single level should be included in the single level variables (`s_lev_vars`) section separated by a comma from other variables to be plotted.

`s_lev_vars: CAPE_CIN, dewpoint_HL, mean_vwinds_950_600, mslp`

Variables that can be plotted for multiple pressure levels such as temperature, winds or humidity should be added to the multiple level variables section (`m_lev_vars`), each script name should be followed by the the pressure level it should be plotted on and be seperated from other script titles by a comma.

`m_lev_vars: geo 925 850 650 600 500 200, winds 925 850 700 600 200, streamlines 925 850 700 600, rel_humidity 850 700 500, temperature 500`

Generally the structure of the potting scripts is as follows. The forecast times to be plotted are read from the namelist file in order to describe the forecast loop when plotting. The initialisation time is supplied as an argument. The domains file is read so that the lat and lon values supplied as arguments can be checked and images named appropriately. This is a check that is made as the plotting scripts can be run independently without being invoked by plot.py, if the lat lon values supplied match values in the domains file then the images will be assigned the correct region name, otherwise the images are assigned the region name “unnamedregion”. The analysis file is opened and if a specific pressure level is requested the level dimensions of one of the variables is read. These levels are then compared to the requested level in order to determine the required level indices. The latitude and longitude are read from the analysis file also with modifications made depending on whether the box requested crosses the Greenwich meridian (this prevents contour plots having a discontinuity which shows up as a blank line on plotting). The analysis file is read, any required calculations performed and a plot created. After this a loop is started for repeating this process for the requested forecast times. Once the images have been generated the whitespace around them is trimmed and they are moved to the directories created by plot.py.

The plotting scripts are written using python but are heavily reliant on the pynio and pyngl libraries. These libraries are the pythonised version of NCL. As such anyone with experience writing analysis and plotting code in NCL might be familiar with these sections of code. In particular the creation of a workstation (wks) and the selection of resources that modify the way in which plotting occurs.

You should now be ready to move onto acquiring GFS data and attempting to create plots.

## Downloading and preprocessing GFS data

Included in the `GFS_plotting` repository are scripts for: (1) downloading the latest operational data, (2) downloading archive data and (3) preprocessing the data into netcdf files that are can be easily read by the GFS plotting code.

As before these scripts rely on you having set a `SWIFT_GFS` environment variable in your .bashrc file.

### Download latest GFS NWP data

To download the latest available GFS NWP data you can use the provided `get_GFS_operational.sh` script in the scripts directory. This script creates a new directory in your `GFS_plotting` directory called `GFS_NWP`, within this directory another directory for the latest available GFS initialisation time will also be created. On completion this will include all the grib2 files we download. The script uses the information provided in namelist file that can be found in the `controls` directory to determine which forecast times are to be downloaded. If you are running the plotting code operationally you might want to download GFS data as soon as possible. This can sometimes mean that (if there is a delay in the production of GFS, as sometimes happens) the files will not be present to download. To mitigate this problem the script has been designed to check that all expected files are present. If there are any files missing it will create a new FTP download script and wait 5 minutes before attempting to download the missing files. This occurs a maximum of 25 times at which point at least 2 hours will have passed (not including download times) and all GFS files you might want should be available.

To run the script navigate to the `scripts` directory and attempt to download the latest available GFS data. Before running the script, open it and make sure to edit the email entry to your email address. This is used by the NCEP NOAA ftp server in place of a password, it is not used for any other purpose but the ftp server will reject a connection that attempts to access data with an empty password field. The download will take some time (depending on your internet speed) and you will see the progress of the downloads as each new download starts. It will look something like this.

`./get_GFS_operational.sh`

```
Connected to ftp.ncep.noaa.gov (140.90.101.48).
220-******************************************************************
220-                 **WARNING**WARNING**WARNING**
220-This is a United States (Agency) computer system, which may be accessed
220-and used only for official Government business by authorized personnel.
220-Unauthorized access or use of this computer system may subject violators
220-to criminal, civil, and/or administrative action.
220-All information on this computer system may be intercepted, recorded,
220-read, copied, and disclosed by and to authorized personnel for official
220-purposes, including criminal investigations. Access or use of this
220-computer system by any person whether authorized or unauthorized,
220-constitutes consent to these terms.
220-                **WARNING**WARNING**WARNING**
220-******************************************************************
220-
220 
331 Please specify the password.
230 Login successful.
200 Switching to Binary mode.
Interactive mode off.
250 Directory successfully changed.
250 Directory successfully changed.
250 Directory successfully changed.
local: gfs.t06z.pgrb2.0p50.f000 remote: gfs.t06z.pgrb2.0p50.f000
227 Entering Passive Mode (140,90,101,48,19,219).
150 Opening BINARY mode data connection for gfs.t06z.pgrb2.0p50.f000 (89991066 bytes).
89991066 bytes received in 10.2 secs (8792.53 Kbytes/sec)
local: gfs.t06z.pgrb2.0p50.f003 remote: gfs.t06z.pgrb2.0p50.f003
227 Entering Passive Mode (140,90,101,48,21,198).
150 Opening BINARY mode data connection for gfs.t06z.pgrb2.0p50.f003 (97934603 bytes).
97934603 bytes received in 15.7 secs (6229.33 Kbytes/sec)
local: gfs.t06z.pgrb2.0p50.f006 remote: gfs.t06z.pgrb2.0p50.f006
227 Entering Passive Mode (140,90,101,48,28,248).
150 Opening BINARY mode data connection for gfs.t06z.pgrb2.0p50.f006 (99217334 bytes).
226 Transfer complete.
99217334 bytes received in 15.8 secs (6268.40 Kbytes/sec)
…
…
…
… 
local: gfs.t06z.pgrb2.0p50.f063 remote: gfs.t06z.pgrb2.0p50.f063
227 Entering Passive Mode (140,90,101,48,128,48).
150 Opening BINARY mode data connection for gfs.t06z.pgrb2.0p50.f063 (99094605 bytes).
226 Transfer complete.
99094605 bytes received in 17.2 secs (5765.24 Kbytes/sec)
local: gfs.t06z.pgrb2.0p50.f066 remote: gfs.t06z.pgrb2.0p50.f066
227 Entering Passive Mode (140,90,101,48,130,119).
150 Opening BINARY mode data connection for gfs.t06z.pgrb2.0p50.f066 (97657812 bytes).
226 Transfer complete.
97657812 bytes received in 13.9 secs (7015.87 Kbytes/sec)
local: gfs.t06z.pgrb2.0p50.f069 remote: gfs.t06z.pgrb2.0p50.f069
227 Entering Passive Mode (140,90,101,48,134,77).
150 Opening BINARY mode data connection for gfs.t06z.pgrb2.0p50.f069 (99036649 bytes).
226 Transfer complete.
99036649 bytes received in 14.4 secs (6893.28 Kbytes/sec)
local: gfs.t06z.pgrb2.0p50.f072 remote: gfs.t06z.pgrb2.0p50.f072
227 Entering Passive Mode (140,90,101,48,144,143).
150 Opening BINARY mode data connection for gfs.t06z.pgrb2.0p50.f072 (100641438 bytes).
226 Transfer complete.
100641438 bytes received in 15.2 secs (6619.75 Kbytes/sec)
221 Goodbye.
```
