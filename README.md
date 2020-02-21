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

## Control files
The files within the `controls` directory are read by various scripts in order to inform their behaviour. Therefore you should familiarise yourself with what is contained within these files before running any download or preprocessing scripts.

### Domains
The domains file simply defines the lat lon corners of regions that can be plotted using the python code. The domains file is not interrogated for information until the running of python code, therefore it will not influence the behaviour of the data download or preprocessing scripts.

Domains are described as follows

`Name: lower_Lat, left_Lon, upper_Lat, right_Lon`

e.g. The West Africa domain supplied in the repository

`WA: -2.5, -32.0, 36.0, 28.0`

### Namelist
In contrast to the domains file the namelist file (also found in the `controls` directory) is used by the data download and preprocessing scripts as a source of information. In particular the date-times of GFS initialisation and the forecast times that are requested are read from the file to inform the downloading of archive data and the untarring data from the tape archive. Therefore, if you change the values of init and fore between downloading your data and running the python code you might find that the data you wish to plot is not available and causes failure of the python plotting scripts.

The namelist file contains 5 categories that can be edited to control the running of the bash and python scripts. These are initialisation time (`init`), multiple level variables (`m_lev_vars`), single level variables (`s_lev_vars`), regions (`region`) and forecast times to be plotted (`fore`). This file allows for a great deal of control on the plotting of GFS data without having to edit any of the python scripts.

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

### Download recent archived GFS data
There is an online archive of GFS data that can be accessed in a similar way to the operational GFS data. These files are hosted online by NOAA (on both ftp and http servers) and can be browsed using this website (https://www.ncdc.noaa.gov/data-access/model-data/model-datasets/global-forcast-system-gfs). In the `GFS_plotting` repository there are a number of scripts supplied that deal with the downloading of archive data. For data that is in the near past (last year or so) the scripts `get_GFS_archived.sh` and `run_get_GFS_archived.sh` are the ones you should use. The `run_get_GFS_archived.sh` script interrogates the initialisation dates and times that you have entered in the `init` variable of the namelist file (found in the `controls` directory). This, in turn runs the `get_GFS_archived.sh` script with the appropriate date and time arguments. This script uses curl to check the existence of the files in the ftp and http archives and if present downloads them and stores them in the same way as discussed earlier. On running the `run_get_GFS_archived.sh` script you should see something like this appear on your console (assuming data is present).

```
% Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 57.4M  100 57.4M    0     0  6473k      0  0:00:09  0:00:09 --:--:-- 13.1M
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 62.9M  100 62.9M    0     0  7882k      0  0:00:08  0:00:08 --:--:-- 12.3M
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 63.8M  100 63.8M    0     0  9240k      0  0:00:07  0:00:07 --:--:-- 13.8M
…
…
…
…
```

If there is data that you are attempting to download that is not in the online archive you will receive a message informing you that your requested data cannot be found. However, this data is likely to be available and you can see if it is on the NOAA tape storage.

### Download older archived GFS data

To browse the available periods go to the NOAA GFS webpage (https://www.ncdc.noaa.gov/data-access/model-data/model-datasets/global-forcast-system-gfs). You should scroll down to the GFS Forecast section of the site and on the right hand side click on the HAS link for the 004/0.5 degree grid (this is in line with the data that the operational data download script downloads). You will then be able to select the initialisation time and dates that you wish to download. Then all you need to do is select the files you wish to download and enter an email address. This email address will be used to inform when your order has been retrieved from tape storage and is ready to download. Be aware that data from the tape archive will be slow to download. This is because the number of forecast times included is significantly higher than the 0-72 period we have been downloading so far (a single initialisation time is ~6 GB of data). Once you have received an email to tell you that your order/orders are ready you can use the `get_GFS_archived_tape.sh` script to download them. To do so you should run the script with all the order numbers you wish to download as arguments.

`/get_GFS_archived_tape.sh HAS011462403 HAS011462405 HAS011462407`

When the files from your order have been downloaded you can run the untarring script (`untar_tape_data.sh`) that is included in the `scripts` directory of the repository. This will untar the forecast files specified in your namelist file and move the resulting files from the order subdirectory of your tape directory into appropriately named initialisation directories in the `GFS_NWP` directory. The order tar files will automatically be deleted on untarring. Therefore, if you wish to produce archive images for a different range of forecast times then you should modify your namelist first.

`./untar_tape_data.sh`

### Converting GRIB2 to netCDF

To make the data easier to access and interrogate outside of the python plotting routines I chose to convert the data into netCDF format. The script to do this is included in the `scripts` directory and is called `convert_GFS.sh`. The script loops through all the directories in the GFS_NWP directory (apart from the tape directory) and first converts the GRIB2 files to netCDFs. Then renames the analysis file, selects the required variables from the files and concatenates all the forecast files into a single netCDF. The selection of a subset of variables was required as an update to the structure of GFS files in 2019 prevented the concatenation of the forecast files. This was due to some forecast files containing variables that were not present in others. It is a quirk of the process that has become necessary to avoid heavily modifying the way in which the python scripts work. In the future I hope to modify the methods used to mean that the GFS forecast files are not subset in this way.

`./convert_GFS.sh`

Once this step is complete it marks the end of the preprocessing. You should now see that there are symbolic links present in the python directory which will enable the plotting routines to access the data stored in the `GFS_NWP` subdirectories.

## Using the python plotting scripts

As already discussed the files within the `controls` directory are read by various scripts in order to influence their behaviour. In particular the `namelist` file controls what data is downloaded from the NCEP archive if running the plotting code for past events and which files are concatenated into the GFS forecast netCDFs. Therefore it is sensible to set up the `namelist` file fully before running any data download or preprocessing steps.

As long as you are not editing the `init` or `fore` fields of the `namelist` file then you can subsequently make decisions on which variables and domains to run the python code for. As mentioned earlier the `namelist` file is read by the `plot.py` script and used to generate all the commands to run the potting scripts in parallel.

Before running the `plot.py` script you should make sure that in the `python` directory you have symbolic links to all the netCDF files you are going to reading data from. Once you are satisfied that this is the case you can activate the conda environment we set up earlier.

`conda activate pyn_env`

Now you can run the `plot.py` script, this will run a number of other python scripts in turn and produce the output images.

`python plot.py`

The `plot.py` script automatically parallelizes the running of the plotting scripts with 4 parallel processes. If you want to alter the number of processes, this can be achieved by including an argument to the `plot.py` command. First you should check the number of CPUs you have available.

`lscpu`

This should show you something like this

```
Architecture:          x86_64
CPU op-mode(s):        32-bit, 64-bit
Byte Order:            Little Endian
CPU(s):                4
On-line CPU(s) list:   0-3
Thread(s) per core:    2
Core(s) per socket:    2
…
…
…
```

In this case the number of CPUs is 4 so there is no advantage to attempting to run more processes, however on the system I run the GFS plotting on operationally I have 40 CPUs available so I can run the plotting scripts on a much higher number of CPUs and therefore produce them faster.

```
Architecture:          x86_64
CPU op-mode(s):        32-bit, 64-bit
Byte Order:            Little Endian
CPU(s):                40
On-line CPU(s) list:   0-39
Thread(s) per core:    2
Core(s) per socket:    10
…
…
…
```
e.g. to run 20 processes in parallel the command looks like this

`python plot.py 20`

Once running the commands that are being run are printed to the screen and there are generally some minor warnings issued by the plotting scripts (don’t worry if your output looks like this).


