###################################################################################################
# Project           : Global Challenges Research Fund (GCRF) African SWIFT (Science for Weather
#                     Information and Forecasting Techniques.
#
# Program name      : mslp.py 
#
# Author            : Alexander J. Roberts, University of Leeds, NCAS
# 
# Date created      : Jan 2019
#
# Purpose           : Plot mean sea level pressure images as part of SWIFT_GFSplotting.
#
# Revision History  :
#
# Usage             : Can be used as part of wider plotting repository or independently e.g.
#                     "python3 mslp.py time lat lon lat lon"
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

#####################################################################################################

#  9-point smoother function, required to make the geopotential contours look better.
#
def smth9(x,p,q):
#
#  Run a 9-point smoother on the 2D numpy.array x using weights
#  p and q.  Return the smoothed array.
#

#
#  Get array dimensions and check on sizes.
#
  ni = x.shape[0]
  nj = x.shape[1]
  if (ni < 3 or nj < 3):
    print("smth9: both array dimensions must be at least three.")
    sys.exit()

#
#  Smooth.
#
  po4 = p/4.
  qo4 = q/4.

  output = np.zeros([ni,nj],'f')
  for j in range(1,nj-1):
    for i in range(1,ni-1):
      jm1 = j-1
      jp1 = j+1
      im1 = i-1
      ip1 = i+1
      term1 = po4*(x[im1,j]+x[i,jm1]+x[ip1,j]+x[i,jp1]-4.*x[i,j])
      term2 = qo4*(x[im1,jp1]+x[im1,jm1]+x[ip1,jm1]+x[ip1,jp1]-4.*x[i,j])
      output[i,j] = float(x[i,j]) + term1 + term2

#
#  Set the perimeter values to the original x values.
#
  output[0,:]    = x[0,:]
  output[ni-1,:] = x[ni-1,:]
  output[:,0]    = x[:,0]
  output[:,nj-1] = x[:,nj-1]

#
#  Return smoothed array.
#
  return output

###################################################################################################

# Main script to plot mslp

# define directory

diri = (os.getcwd())+"/"

# forecast times (currently set to plot 0 to 48 hours)

fore = (os.popen("cat %s/controls/namelist | grep 'fore:' | awk -F: '{print $2}' | tr ',' ' '"%(GFS_dir))).read().split()
fore = [np.int(f) for f in fore]

# read text file with initialisation time and dates

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

# read in analysis files
 
a_fili = "analysis_gfs_4_%s_%s00_000.nc" % (init_dt[:8], init_dt[8:10])

# open analysis file

analysis = nio.open_file(diri+a_fili)

# read in lat

lat1 = analysis.variables["lat_0"]
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

lon1 = analysis.variables["lon_0"]

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

# read in mslp, checking whether box crosses Greenwich Meridian.

if (np.sign(lonbl) + np.sign(lontr)) >= -1 and (np.sign(lonbl) + np.sign(lontr)) <= 1:

   mslp1 = analysis.variables["PRMSL_P0_L101_GLL0"][:,:]/100.0
   mslp_temp1 = mslp1[lat_box1:lat_box2,0:lon_box1]
   mslp_temp2 = mslp1[lat_box1:lat_box2,lon_box2:lon_box3]
   mslp = np.concatenate((mslp_temp2,mslp_temp1),axis=1)
   del mslp1
   del mslp_temp1
   del mslp_temp2
   mslp = smth9(mslp, 0.5, 0.25)

else:

   mslp1 = analysis.variables["PRMSL_P0_L101_GLL0"][:,:]/100.0
   mslp = mslp1[lat_box1:lat_box2,lon_box1:lon_box2]
   del mslp1
   mslp = smth9(mslp, 0.5, 0.25)

# create 2d lat and lon

lat2d = np.zeros((len(lat),len(lon)))
lon2d = np.zeros((len(lat),len(lon)))

for i in range(0, len(lon)):
   lat2d[:,i] = lat

for i in range(0, len(lat)):
   lon2d[i,:] = lon
   
# open workspace for analysis plot

wks_type = "png"
wks_res = ngl.Resources()
wks_res.wkBackgroundOpacityF = 0.0
wks = ngl.open_wks(wks_type, "GFSanalysis_%s_%s_mslp_SNGL" % (region, init_dt[0:10]), wks_res)

# define resources for analysis plot

res = ngl.Resources()
res.nglDraw  = False
res.nglFrame = False

res.mpGridAndLimbOn        = False
res.pmTickMarkDisplayMode = "Never"

res.cnInfoLabelOn              = False
res.cnLineLabelsOn             = True
res.cnFillOn                   = False
res.cnHighLabelBackgroundColor = -1
res.cnHighLabelFontColor       = "Black"
res.cnHighLabelFontHeightF     = 0.015
res.cnHighLabelPerimOn         = False
res.cnHighLabelPerimThicknessF = 2.5
res.cnHighLabelsOn             = True
res.cnHighLowLabelOverlapMode  = "AdjustVPOmitOverHL"
res.cnInfoLabelOn              = False
res.cnLineLabelBackgroundColor = -1
res.cnLineLabelDensityF        = 0.8
res.cnLineLabelFontColor       = "Black"
res.cnLineLabelFontHeightF     = 0.015
res.cnLineLabelPerimOn         = False
res.cnLineLabelsOn             = True
res.cnLinesOn                  = True
res.cnLowLabelBackgroundColor  = -1
res.cnLowLabelFontColor        = "Black"
res.cnLowLabelFontHeightF      = 0.015
res.cnLowLabelPerimOn          = False
res.cnLowLabelsOn              = True
res.cnMonoLineLabelFontColor   = True

res.sfXArray = lon2d
res.sfYArray = lat2d

res.mpProjection              = "CylindricalEquidistant"
res.mpLimitMode = "LatLon"    # Limit the map view.
res.mpMinLonF   = lontr
res.mpMaxLonF   = lonbl
res.mpMinLatF   = lattr
res.mpMaxLatF   = latbl
res.mpPerimOn   = True
res.mpOutlineBoundarySets     = "AllBoundaries"
res.mpNationalLineColor       = "gray40"
res.mpNationalLineThicknessF  = 1.5
res.mpGeophysicalLineColor    = "gray40"
res.mpGeophysicalLineThicknessF = 1.5
res.cnMonoLineColor           = True

max_cont = (2.0*round(np.max(mslp/2.0),0))+10.0
min_cont = (2.0*round(np.min(mslp/2.0),0))-10.0

res.cnLevelSelectionMode = "ManualLevels"
res.cnMinLevelValF       = min_cont
res.cnMaxLevelValF       = max_cont
res.cnLevelSpacingF      = 2.
res.cnLineThicknessF     = 2.5 

# create plot for analysis data

mslp_plot = ngl.contour_map(wks,mslp,res)

ngl.maximize_plot(wks, mslp_plot)
ngl.draw(mslp_plot)
ngl.frame(wks)

ngl.destroy(wks)
del res

###################################################################################################

# open forecast file

f_fili = "GFS_forecast_%s_%s.nc" % (init_dt[:8], init_dt[8:10])
forecast = nio.open_file(diri+f_fili)

# loop through forecast times

for i in range(0, len(fore)):

# create string for valid time

   valid_date = (datetime.datetime(int(init_dt[:4]), int(init_dt[4:6]), int(init_dt[6:8]), int(init_dt[8:10])) + datetime.timedelta(hours=int(fore[i]))).strftime("%Y%m%d%H")


# read in mslp, checking whether box crosses Greenwich Meridian.

   if (np.sign(lonbl) + np.sign(lontr)) >= -1 and (np.sign(lonbl) + np.sign(lontr)) <= 1:

      mslp1 = forecast.variables["PRMSL_P0_L101_GLL0"][i,:,:]/100.0
      mslp_temp1 = mslp1[lat_box1:lat_box2,0:lon_box1]
      mslp_temp2 = mslp1[lat_box1:lat_box2,lon_box2:lon_box3]
      mslp = np.concatenate((mslp_temp2,mslp_temp1),axis=1)
      del mslp1
      del mslp_temp1
      del mslp_temp2
      mslp = smth9(mslp, 0.5, 0.25)

   else:

      mslp1 = forecast.variables["PRMSL_P0_L101_GLL0"][i,:,:]/100.0
      mslp = mslp1[lat_box1:lat_box2,lon_box1:lon_box2]
      del mslp1
      mslp = smth9(mslp, 0.5, 0.25)

# open workspace for forecast plots

   wks_type = "png"
   wks_res = ngl.Resources()
   wks_res.wkBackgroundOpacityF = 0.0
   wks = ngl.open_wks(wks_type, "GFSforecast_%s_%s_mslp_SNGL_%s_%03d" % (region, valid_date, init_dt[0:10], fore[i]), wks_res)

# define resources for forecast plots

   res = ngl.Resources()
   res.nglDraw  = False
   res.nglFrame = False

   res.mpGridAndLimbOn        = False
   res.pmTickMarkDisplayMode = "Never"

   res.cnInfoLabelOn              = False
   res.cnLineLabelsOn             = True
   res.cnFillOn                   = False
   res.cnHighLabelBackgroundColor = -1
   res.cnHighLabelFontColor       = "Black"
   res.cnHighLabelFontHeightF     = 0.015
   res.cnHighLabelPerimOn         = False
   res.cnHighLabelPerimThicknessF = 2.5
   res.cnHighLabelsOn             = True
   res.cnHighLowLabelOverlapMode  = "AdjustVPOmitOverHL"
   res.cnInfoLabelOn              = False
   res.cnLineLabelBackgroundColor = -1
   res.cnLineLabelDensityF        = 0.8
   res.cnLineLabelFontColor       = "Black"
   res.cnLineLabelFontHeightF     = 0.015
   res.cnLineLabelPerimOn         = False
   res.cnLineLabelsOn             = True
   res.cnLinesOn                  = True
   res.cnLowLabelBackgroundColor  = -1
   res.cnLowLabelFontColor        = "Black"
   res.cnLowLabelFontHeightF      = 0.015
   res.cnLowLabelPerimOn          = False
   res.cnLowLabelsOn              = True
   res.cnMonoLineLabelFontColor   = True

   res.sfXArray = lon2d
   res.sfYArray = lat2d

   res.mpProjection              = "CylindricalEquidistant"
   res.mpLimitMode = "LatLon"    # Limit the map view.
   res.mpMinLonF   = lontr
   res.mpMaxLonF   = lonbl
   res.mpMinLatF   = lattr
   res.mpMaxLatF   = latbl
   res.mpPerimOn   = True
   res.mpOutlineBoundarySets     = "AllBoundaries"
   res.mpNationalLineColor       = "gray40"
   res.mpNationalLineThicknessF  = 1.5
   res.mpGeophysicalLineColor    = "gray40"
   res.mpGeophysicalLineThicknessF = 1.5
   res.cnMonoLineColor           = True

   max_cont = (2.0*round(np.max(mslp/2.0),0))+10.0
   min_cont = (2.0*round(np.min(mslp/2.0),0))-10.0

   res.cnLevelSelectionMode = "ManualLevels"
   res.cnMinLevelValF       = min_cont
   res.cnMaxLevelValF       = max_cont
   res.cnLevelSpacingF      = 2.
   res.cnLineThicknessF     = 2.5

# create geopotential plots for forecast times

   mslp_plot = ngl.contour_map(wks,mslp,res)

   ngl.maximize_plot(wks, mslp_plot)
   ngl.draw(mslp_plot)
   ngl.frame(wks)

   ngl.destroy(wks)
   del res

os.system('mogrify -trim *_'+region+'_'+init_dt[0:10]+'_mslp_SNGL.png')
#if region == "WA" or region == "unknownWA":
#   os.system('mogrify -resize 886x600 *_'+region+'_'+init_dt[0:10]+'_mslp_SNGL.png')
#elif region == "EA" or region == "unknownEA":
#   os.system('mogrify -resize 600x733 *_'+region+'_'+init_dt[0:10]+'_mslp_SNGL.png')

os.system('mv *_'+region+'_'+init_dt[0:10]+'_mslp_SNGL.png %s/MARTIN/GFS/'%(GFS_dir)+region+'/'+init_dt[0:10]+'/mslp')

os.system('mogrify -trim *'+region+'_*mslp_SNGL_'+init_dt[0:10]+'*.png')
#if region == "WA" or region == "unknownWA":
#   os.system('mogrify -resize 886x600 *'+region+'_*mslp_SNGL_'+init_dt[0:10]+'*.png')
#elif region == "EA" or region == "unknownEA":
#   os.system('mogrify -resize 600x733 *'+region+'_*mslp_SNGL_'+init_dt[0:10]+'*.png')

os.system('mv *'+region+'_*mslp_SNGL_'+init_dt[0:10]+'*.png %s/MARTIN/GFS/'%(GFS_dir)+region+'/'+init_dt[0:10]+'/mslp')
