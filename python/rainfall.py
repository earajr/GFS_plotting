###################################################################################################
# Project           : Global Challenges Research Fund (GCRF) African SWIFT (Science for Weather
#                     Information and Forecasting Techniques.
#
# Program name      : rainfall.py 
#
# Author            : Alexander J. Roberts, University of Leeds, NCAS
# 
# Date created      : Jan 2019
#
# Purpose           : Plot rainfall images as part of SWIFT_GFSplotting.
#
# Revision History  :
#
# Usage             : Can be used as part of wider plotting repository or independently e.g.
#                     "python3 rainfall.py time lat lon lat lon"
#                     where time is in the initialisation time in the form YYYYMMDDHH 
###################################################################################################

import numpy as np
import Nio as nio
import Ngl as ngl
import glob
import datetime as dt
import sys
import os
import datetime

GFS_dir = os.environ['SWIFT_GFS']

###################################################################################################

# Main script to plot rainfall

# define directory

diri = (os.getcwd())+"/"

# forecast times (currently set to plot 0 to 48 hours)

fore = (os.popen("cat %s/controls/namelist | grep 'fore:' | awk -F: '{print $2}' | tr ',' ' '"%(GFS_dir))).read().split()
fore = [np.int(f) for f in fore]

# accept initialisation time and dates as an argument

init_dt = (sys.argv[1])

# read in domains and accept lat and lon limits as arguments

b = open(GFS_dir+"/controls/domains")
domains_content = b.readlines()

key_list = []
latlon_list = []

for domain in domains_content:
   key_list.append(domain.split(":")[0])
   latlon_str = (domain.split(":")[1]).strip().split(",")
   latlon_flt = []
   for ll in latlon_str:
      latlon_flt.append(float(ll))
   latlon_list.append(latlon_flt)
   del(latlon_flt)

domains_dict = dict(zip(key_list,latlon_list))

latbl = float(sys.argv[3])
lonbl = float(sys.argv[4])
lattr = float(sys.argv[5])
lontr = float(sys.argv[6])

region = "unnamedregion"

for domain in domains_dict.keys():
   if ((latbl == domains_dict[domain][0] and lattr == domains_dict[domain][2]) or (latbl == domains_dict[domain][2] or lattr == domains_dict[domain][0])) and ((lonbl == domains_dict[domain][1] and lontr == domains_dict[domain][3]) or (lonbl == domains_dict[domain][3] and lontr == domains_dict[domain][1])):
      region = domain

# arrange lat and lon values to get bottom left and top right lat lon values

if latbl == lattr or lonbl == lontr:
   sys.exit('lat and lon values must be different')
else:
   if latbl < lattr:
      latbl, lattr = lattr, latbl
   if lonbl > lontr:
      lonbl, lontr = lontr, lonbl

# open forecast file

f_fili = "GFS_forecast_%s_%s.nc" % (init_dt[:8], init_dt[8:10])
forecast = nio.open_file(diri+f_fili)

# read in lat

lat1 = forecast.variables["lat_0"]
lat_temp = lat1[:]

latbl_idx = (np.abs(lat_temp-latbl)).argmin()
lattr_idx = (np.abs(lat_temp-lattr)).argmin()

if latbl_idx == lattr_idx:
   sys.exit('lat values are not different enough, they must have relate to different grid points')
elif latbl_idx > 1 and lattr_idx < len(lat_temp)-2:
   lat_box1 = latbl_idx-2
   lat_box2 = lattr_idx+2
   lat = lat_temp[lat_box1:lat_box2]
else:
   lat_box1 = latbl_idx
   lat_box2 = lattr_idx
   lat = lat_temp[lat_box1:lat_box2]

del(latbl_idx)
del(lattr_idx)
del(lat1)
del(lat_temp)

# read in lon

lon1 = forecast.variables["lon_0"]

# check to see if box crosses Greenwich Meridian. If so then the lon values must be modified for plot to work.

if (np.sign(lonbl) + np.sign(lontr)) >= -1 and (np.sign(lonbl) + np.sign(lontr)) <= 1:

   lonbl, lontr = lontr, lonbl

   lon_temp = np.where(lon1[:]>=180.0, lon1[:]-360.0, lon1[:])

   lonbl_idx = (np.abs(lon_temp-lonbl)).argmin()
   lontr_idx = (np.abs(lon_temp-lontr)).argmin()

   if lonbl_idx == lontr_idx:
      sys.exit('lon values are not different enough, they must have relate to different grid points')
   elif lontr_idx > len(lon_temp)/2 and lonbl_idx <= len(lon_temp)/2:
      lon_box1 = lonbl_idx+2
      lon_box2 = lontr_idx-2
      lon_box3 = len(lon_temp)-1

      lon_temp1 = lon_temp[0:lon_box1]
      lon_temp2 = lon_temp[lon_box2:lon_box3]
   else:
      lon_box1 = lonbl_idx
      lon_box2 = lontr_idx
      lon_box3 = len(lon_temp)-1

      lon_temp1 = lon_temp[0:lon_box1]
      lon_temp2 = lon_temp[lon_box2:lon_box3]


   lon = np.append(lon_temp2, lon_temp1)

   del(lon_temp1)
   del(lon_temp2)
   del(lonbl_idx)
   del(lontr_idx)
   del(lon_temp)

else:

   lon_temp = lon1[:]

   lonbl_idx = (np.abs(lon_temp-lonbl)).argmin()
   lontr_idx = (np.abs(lon_temp-lontr)).argmin()

   if lonbl_idx == lontr_idx:
      sys.exit('lon values are not different enough, they must have relate to different grid points')
   elif lonbl_idx > 1 and lontr_idx < len(lon_temp)-2:
      lon_box1 = lonbl_idx-2
      lon_box2 = lontr_idx+2
      lon = lon_temp[lon_box1:lon_box2]
   else:
      lon_box1 = lonbl_idx
      lon_box2 = lontr_idx
      lon = lon_temp[lon_box1:lon_box2]

# create 2d lat and lon

lat2d = np.zeros((len(lat),len(lon)))
lon2d = np.zeros((len(lat),len(lon)))

for i in range(0, len(lon)):
   lat2d[:,i] = lat

for i in range(0, len(lat)):
   lon2d[i,:] = lon

# loop through forecast times

for i in range(0, len(fore)):

# create string for valid time

   valid_date = (datetime.datetime(int(init_dt[:4]), int(init_dt[4:6]), int(init_dt[6:8]), int(init_dt[8:10])) + datetime.timedelta(hours=int(fore[i]))).strftime("%Y%m%d%H")

# read in PRATE, checking whether box crosses Greenwich Meridian.

   var_name = [key for key in forecast.variables.keys() if "PRATE" in key][0]

   if (np.sign(lonbl) + np.sign(lontr)) >= -1 and (np.sign(lonbl) + np.sign(lontr)) <= 1:

      PRATE1 = forecast.variables[var_name][i,:,:]*3600.0
      PRATE_temp1 = PRATE1[lat_box1:lat_box2,0:lon_box1]
      PRATE_temp2 = PRATE1[lat_box1:lat_box2,lon_box2:lon_box3]
      PRATE = np.concatenate((PRATE_temp2,PRATE_temp1),axis=1)
      del PRATE1
      del PRATE_temp1
      del PRATE_temp2

   else:

      PRATE1 = forecast.variables[var_name][i,:,:]*3600.0
      PRATE = PRATE1[lat_box1:lat_box2,lon_box1:lon_box2]
      del PRATE1

# open workspace for forecast plots

   wks_type = "png"
   wks_res = ngl.Resources()
   wks_res.wkBackgroundOpacityF = 0.0
   wks = ngl.open_wks(wks_type, "GFSforecast_%s_%s_PRATE_SNGL_%s_%03d" % (region, valid_date, init_dt[0:10], fore[i]), wks_res)

# define resources for forecast plots

   res = ngl.Resources()
   res.nglDraw  = False
   res.nglFrame = False

   res.vpWidthF  = 0.9
   res.vpHeightF = 0.6

   cmap = ngl.read_colormap_file("WhiteBlueGreenYellowRed")

   res.mpGridAndLimbOn        = False

   res.tiMainFontHeightF          = 0.015
   res.cnInfoLabelOn              = False
   res.cnFillOn                   = True
   res.cnFillPalette              = cmap
   res.cnInfoLabelOn              = False
   res.cnLineLabelsOn             = False
   res.cnLinesOn                  = False
   res.cnMonoLineLabelFontColor   = True

   res.lbAutoManage          = False
   res.lbLabelFontHeightF         = 0.005
   res.lbOrientation              = "horizontal"
   res.lbLabelAngleF              = 45
   res.pmLabelBarOrthogonalPosF = -1.
   res.pmLabelBarParallelPosF = 0.25
   res.pmLabelBarWidthF      = 0.3
   res.pmLabelBarHeightF     = 0.1
   res.lbTitleString         = "Precipitation rate"
   res.lbTitleFontHeightF   = 0.0125

   res.sfXArray = lon2d
   res.sfYArray = lat2d

   res.pmTickMarkDisplayMode = "Never"
   res.mpProjection              = "CylindricalEquidistant"
   res.mpLimitMode = "LatLon"    # Limit the map view.
   res.mpMinLonF   = lontr
   res.mpMaxLonF   = lonbl
   res.mpMinLatF   = lattr
   res.mpMaxLatF   = latbl
   res.mpOutlineBoundarySets     = "AllBoundaries"
   res.mpNationalLineColor       = "gray40"
   res.mpNationalLineThicknessF  = 1.5
   res.mpGeophysicalLineColor    = "gray40"
   res.mpGeophysicalLineThicknessF = 1.5
   res.cnMonoLineColor           = True

   res.cnLevelSelectionMode = "ExplicitLevels"
   res.cnLevels = [0.1, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 3.0, 3.5, 4.0, 5.0]
   res.cnFillColors = [-1, 6, 21, 36, 51, 66, 81, 96, 111, 126, 141, 156, 171, 186, 201, 216]


# create PRATE plots for forecast times

   PRATE_plot = ngl.contour_map(wks,PRATE,res)

   del res.mpProjection
   del res.mpLimitMode
   del res.mpMinLonF
   del res.mpMaxLonF
   del res.mpMinLatF
   del res.mpMaxLatF
#   del res.mpPerimOn
   del res.mpOutlineBoundarySets
   del res.mpNationalLineColor
   del res.mpNationalLineThicknessF
   del res.mpGeophysicalLineColor
   del res.mpGeophysicalLineThicknessF
   del res.mpGridAndLimbOn
   
   ngl.maximize_plot(wks, PRATE_plot)
   ngl.draw(PRATE_plot)
   ngl.frame(wks)

   ngl.destroy(wks)
   del res
   del PRATE

os.system('mogrify -trim *'+region+'_*PRATE_SNGL_'+init_dt[0:10]+'*.png')
#if region == "WA" or region == "unknownWA":
#   os.system('mogrify -resize 886x600 *'+region+'_*PRATE_SNGL_'+init_dt[0:10]+'*.png')
#elif region == "EA" or region == "unknownEA":
#   os.system('mogrify -resize 600x733 *'+region+'_*PRATE_SNGL_'+init_dt[0:10]+'*.png')

os.system('mv *'+region+'_*PRATE_SNGL_'+init_dt[0:10]+'*.png %s/MARTIN/GFS/'%(GFS_dir)+region+'/'+init_dt[0:10]+'/rainfall')
