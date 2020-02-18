# SWIFT GFS python plotting code.

This document gives an overview of the setup required to run the SWIFT GFS python plotting code originally written by Alexander Roberts (NCAS and University of Leeds). This document will: (1) introduce the general structure of the code, (2) explain the supporting scripts including system requirements, (3) explain individual python plotting scripts and (4) describe the operation of the scripts together. This should give all the details needed to understand this repository and allow you to download and use the code for yourself.

## GitHub Repository

To begin with you should first clone the GitHub repository to do this navigate to your home directory (or where ever you wish to put the cloned repository) and run the following command.


`git clone git@github.com:earajr/GFS_plotting.git`


This should create a new directory named `GFS_plotting`. If for any reason this does not work then you click the "clone or download" button above and select to download a zipped version. Once downloaded you can unzip the repository and rename the directory from `GFS_plotting-master` to `GFS_plotting`. This is the exact same repository that you get by using the command above.


Once you have created this directory you should set an environment variable in your .bashrc file that describes the location of this directory. This will be important when running scripts later on.


`export SWIFT_GFS=full/path/to/GFS_plotting`

## Dependencies

There are a number of dependencies that you will need to make sure are installed properly on your system. Within the repository there is a `SWIFT_plotting_dependencies.sh` script which will install all the software that is required. This has been tested on a clean CentOS 7 install and works. If you are using a different Linux OS then you will have to modify the script accordingly. Despite the install procedure being different, the dependencies will be the same. The software that is installed is detailed below.

**epel repository (CentOS, Red Hat Enterprise Linux (RHEL), Scientific Linux, Oracle Linux)**

This is the Extra Packages for Enterprise Linux (EPEL) repository of packages you will have to activate before you can install certain pieces of software using yum in CentOS, (this is not available in other Linux OSs, if any of the software installed using yum is not available for your OS e.g. using apt get in Ubuntu then you will have to find another method of installation such as building the code from source).

**"Development tools"**

This group install will install a number of useful (and required) packages and make sure you have the compilers you will need to build the rest of the required software. The equivalent package in Ubuntu is “build-essentials”.

**ftp	wget	unzip	m4	curl	libcurl-devel	cmake3	python-devel	python3-devel	openjpeg2-tools**
