# SWIFT GFS python plotting code.

This document gives an overview of the setup required to run the SWIFT GFS python plotting code originally written by Alexander Roberts (NCAS and University of Leeds). This document will: (1) introduce the general structure of the code, (2) explain the supporting scripts including system requirements, (3) explain individual python plotting scripts and (4) describe the operation of the scripts together. This should give all the details needed to understand this repository and allow you to download and use the code for yourself.

## GitHub Repository

The GitHub repository for the python plotting routines can be found here (https://github.com/earajr/GFS_plotting). A guide similar to this one can be found as the README file within the GitHub repository. Both documents will guide you through the installation of software that is required on your system as well as the use of bash scripts and python plotting scripts to produce plots for research or operational meteorological purposes.


To begin with you should first clone the GitHub repository to do this navigate to your home directory (or where ever you wish to put the cloned repository) and run the following command.


git clone git@github.com:earajr/GFS_plotting.git


This should create a new directory named GFS_plotting. If for any reason this does not work then you can visit the repository online at https://github.com/earajr/GFS_plotting. On the right hand side of the screen you should see an option to download a zipped version of the repository. Once downloaded you can unzip the repository and rename the directory from GFS_plotting-master to GFS_plotting. This is the exact same repository that you get by using the command above.


Once you have created this directory you should set an environment variable in your .bashrc file that describes the location of this directory. This will be important when running scripts later on.


export SWIFT_GFS=full/path/to/GFS_plotting
