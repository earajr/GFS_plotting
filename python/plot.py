###################################################################################################
# Project           : Global Challenges Research Fund (GCRF) African SWIFT (Science for Weather
#                     Information and Forecasting Techniques.
#
# Program name      : plot.py 
#
# Author            : Alexander J. Roberts, University of Leeds, NCAS
# 
# Date created      : Jan 2019
#
# Purpose           : Reads in namelist variables and creates list of plotting commands to be exceuted
#                     as part of the SWIFT GFS python plotting repository. Jobs are then run in
#                     parallel by submitting to a pool.
#
# Revision History  :
#
# Usage             : Can be used as part of wider plotting repository or independently e.g.
#                     "python3 CAPE_CIN.py time lat lon lat lon"
#                     where time is in the initialisation time in the form YYYYMMDDHH 
###################################################################################################

# worker function that submits the commands to be processed in the background

def worker( x ):
   import subprocess
   import os

   print ("Running %s %s %s %s %s %s %s %s" % (x["pyver"],x["var"],x["time"], x["lev"], x["lat1"], x["lon1"], x["lat2"], x["lon2"]))
   command = [x["pyver"],x["var"],x["time"], x["lev"], x["lat1"], x["lon1"], x["lat2"], x["lon2"]]
   p = subprocess.Popen([x["pyver"], x["var"], x["time"], x["lev"], x["lat1"], x["lon1"], x["lat2"], x["lon2"]])
   print(p.communicate())
   return  # ({"out":out})

# main function that reads in initiation times from init_dt, variables and levels from m_lev_vars and variables (on single levels) from s_lev_vars
# commands are then constructed and submitted to a pool to be run in parallel on a user specified number of cores "n_cores"

if __name__ == "__main__":
   
   from multiprocessing.pool import Pool
   import os
   import sys

# define working and current directory

   diri = "/nfs/a37/earajr/SWIFT/CaseStudies/plot_py"
   image_diri = diri+'/MARTIN'

   if not (os.path.isdir(image_diri)):
      os.mkdir(image_diri)

   if not (os.path.isdir(image_diri+'/GFS')):
      os.mkdir(image_diri+'/GFS')

# Read namelist and extract initiation times, vars, levels and regions
   
   a = open(diri+"/namelist")
   content = a.readlines()

   init_dt = ((next((s for s in content if "init" in s), None)).rstrip().split(":"))[1].split(",")
   m_lev_vars = ((next((s for s in content if "m_lev_vars" in s), None)).rstrip().split(":"))[1].split(",")
   split_m_lev_vars = m_lev_vars[0].split()
   s_lev_vars = ((next((s for s in content if "s_lev_vars" in s), None)).rstrip().split(":"))[1].split(",")
   region = ((next((s for s in content if "region" in s), None)).rstrip().split(":"))[1].split(",")

# loop through namelist contents and create directory structure for images and list of commands

   for i in range(len(region)):
      b = open(diri+"/domains")
      domains_content = b.readlines()

      lat_lon = ((next((s for s in domains_content if region[i].lstrip() in s), None)).rstrip().split(":"))[1].split(",")
      print(lat_lon)

      lat_range = [lat_lon[0], lat_lon[2]]
      lon_range = [lat_lon[1], lat_lon[3]]
     
      if not (os.path.isdir(image_diri+'/GFS'+'/'+region[i].lstrip())):
         os.mkdir(image_diri+'/GFS'+'/'+region[i].lstrip())

      for j in range(len(init_dt)):

         if not (os.path.isdir(image_diri+'/GFS'+'/'+region[i].lstrip()+'/'+init_dt[j].lstrip())):
            os.mkdir(image_diri+'/GFS'+'/'+region[i].lstrip()+'/'+init_dt[j].lstrip())

         for k in range(len(m_lev_vars)):
            print(m_lev_vars[k].split())
            split_m_lev_vars = m_lev_vars[k].split()
            m_lev_vars2 = split_m_lev_vars[0].lstrip()
            levs = split_m_lev_vars[1:]
            print(region[i])
#            if region[i].strip() == "EA":
#               if "850" in levs:
#                  levs.remove("850")
#               if "650" in levs:
#                  levs.remove("650")
#            else:
#               if "800" in levs:
#                  levs.remove("800")
#               if "600" in levs:
#                  levs.remove("600")
               
            for l in range(len(levs)):
               if not (os.path.isdir(image_diri+'/GFS'+'/'+region[i].lstrip()+'/'+init_dt[j].lstrip()+'/'+m_lev_vars2+'_'+levs[l].lstrip())):
                  os.mkdir(image_diri+'/GFS'+'/'+region[i].lstrip()+'/'+init_dt[j].lstrip()+'/'+m_lev_vars2+'_'+levs[l].lstrip())
               try:
                  command_temp = {"pyver":"python3", "var":m_lev_vars2+".py", "time":init_dt[j].lstrip(), "lat1":lat_range[0], "lon1":lon_range[0],"lat2":lat_range[1],"lon2":lon_range[1], "lev":levs[l].lstrip()}
                  command.append(command_temp)
               except NameError:
                  command = []
                  command_temp = {"pyver":"python3", "var":m_lev_vars2+".py", "time":init_dt[j].lstrip(), "lat1":lat_range[0], "lon1":lon_range[0],"lat2":lat_range[1],"lon2":lon_range[1], "lev":levs[l].lstrip()}
                  command.append(command_temp)

         for k in range(len(s_lev_vars)):
            if not (os.path.isdir(image_diri+'/GFS'+'/'+region[i].lstrip()+'/'+init_dt[j].lstrip()+'/'+s_lev_vars[k].lstrip())):
                  os.mkdir(image_diri+'/GFS'+'/'+region[i].lstrip()+'/'+init_dt[j].lstrip()+'/'+s_lev_vars[k].lstrip())
            try:
               command_temp = {"pyver":"python3", "var":s_lev_vars[k].lstrip()+".py", "time":init_dt[j].lstrip(), "lat1":lat_range[0], "lon1":lon_range[0],"lat2":lat_range[1],"lon2":lon_range[1], "lev":""}
               command.append(command_temp)
            except NameError:
               command = []
               command_temp = {"pyver":"python3", "var":s_lev_vars[k].lstrip()+".py", "time":init_dt[j].lstrip(), "lat1":lat_range[0], "lon1":lon_range[0],"lat2":lat_range[1],"lon2":lon_range[1], "lev":""}
               command.append(command_temp)

   n_cores = 12

   if n_cores > 1:
      print("--pooling starts now--")
      pool = Pool( processes=n_cores )
      # Calls the 'worker' function in parallel using the 'par' list. 
      # Each entry will be used once as a task to start a process.
      r = pool.map_async(worker, command)
      r.wait() # Wait for the results
      print("--pooling ended--")
      if not r.successful():
         print(r._value, sys.exit("Parallelization not successful"))
