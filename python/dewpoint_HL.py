###################################################################################################
# Project           : Global Challenges Research Fund (GCRF) African SWIFT (Science for Weather
#                     Information and Forecasting Techniques.
#
# Program name      : dewpoint_HL.py
# 
# Author            : Alexander J. Roberts, University of Leeds, NCAS
# 
# Date created      : Jan 2019
#
# Purpose           : Plot the 2m dewpoint and the position of the heatlow defined as the 90th centile
#                     in difference between the 700 and 925 hPa geopotential.
#
# Revision History  :
#
# Usage             : Can be used as part of wider plotting repository or independently e.g.
#                     "python3 dewpoint_HL.py time lat lon lat lon"
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

# Main script to plot 2m dewpoint and heatlow

# define directory

diri = (os.getcwd())+"/"

# define pressure levels for heat low identification

lev1 = "700"
lev2 = "925"

# accept initialisation time and dates as argument and identify forecast time index for heat low calculation

init_dt = (sys.argv[1])
fili = "GFS_forecast_%s_%s.nc" % (init_dt[:8], init_dt[8:10])
if init_dt[8:10] == "00":
   t_index = [1, 9]
   f_time = [6, 30]
elif init_dt[8:10] == "06":
   t_index = [7, 15]
   f_time = [24, 48]
elif init_dt[8:10] == "12":
   t_index = [5, 13]
   f_time = [18, 42]
elif init_dt[8:10] == "18":
   t_index = [3, 11]
   f_time = [12, 36]

# read in data
 
data = nio.open_file(diri+fili)

# read in pressure levels

levs_p1 = data.variables["lv_ISBL0"]
levs_p = ['{:.0f}'.format(x) for x in levs_p1[:]/100.0]
del levs_p1

# identify level index

lev1_index = levs_p.index(lev1)
lev2_index = levs_p.index(lev2)

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

# read in lat

lat1 = data.variables["lat_0"]
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

lon1 = data.variables["lon_0"]

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

#del lat1
#del lon1

# read in dewpoint and geopotential

for j in range(0, len(t_index)):

   valid_date = (datetime.datetime(int(init_dt[:4]), int(init_dt[4:6]), int(init_dt[6:8]), int(init_dt[8:10])) + datetime.timedelta(hours=int(f_time[j]))).strftime("%Y%m%d%H")

   if (np.sign(lonbl) + np.sign(lontr)) >= -1 and (np.sign(lonbl) + np.sign(lontr)) <= 1:

      dp1 = data.variables["DPT_P0_L103_GLL0"][t_index[j],:,:]-273.15
      dp_temp1 = dp1[lat_box1:lat_box2,0:lon_box1]
      dp_temp2 = dp1[lat_box1:lat_box2,lon_box2:lon_box3]
      dp = np.concatenate((dp_temp2,dp_temp1),axis=1)
      del dp1
      del dp_temp1
      del dp_temp2

      geo11 = data.variables["HGT_P0_L100_GLL0"][t_index[j],lev1_index,:,:]/10.0
      geo1_temp1 = geo11[lat_box1:lat_box2,0:lon_box1]
      geo1_temp2 = geo11[lat_box1:lat_box2,lon_box2:lon_box3]
      geo1 = np.concatenate((geo1_temp2,geo1_temp1),axis=1)
      del geo11
      del geo1_temp1
      del geo1_temp2

      geo21 = data.variables["HGT_P0_L100_GLL0"][t_index[j],lev2_index,:,:]/10.0
      geo2_temp1 = geo21[lat_box1:lat_box2,0:lon_box1]
      geo2_temp2 = geo21[lat_box1:lat_box2,lon_box2:lon_box3]
      geo2 = np.concatenate((geo2_temp2,geo2_temp1),axis=1)
      del geo21
      del geo2_temp1
      del geo2_temp2

   else:

      dp1 = data.variables["DPT_P0_L103_GLL0"][t_index[j],:,:]-273.15
      dp = dp1[lat_box1:lat_box2,lon_box1:lon_box2]
      del dp1

      geo11 = data.variables["HGT_P0_L100_GLL0"][t_index[j],lev1_index,:,:]/10.0
      geo1 = geo11[lat_box1:lat_box2,lon_box1:lon_box2]
      del geo11

      geo21 = data.variables["HGT_P0_L100_GLL0"][t_index[j],lev2_index,:,:]/10.0
      geo2 = geo21[lat_box1:lat_box2,lon_box1:lon_box2]
      del geo21

   geo_diff = geo1 - geo2
   
   geo_thresh = np.percentile(geo_diff,90)

# open workspace for plot

   wks_type = "png"
   wks = ngl.open_wks(wks_type, "GFSforecast_%s_%s_DPandHL_2M_SNGL_%s_%03d" % (region, valid_date, init_dt[0:10], f_time[j]))

# define resources for forecast plots

   res = ngl.Resources()
   res.nglDraw  = False
   res.nglFrame = False

   res.vpWidthF  = 0.9
   res.vpHeightF = 0.6

   cmap = ngl.read_colormap_file("WhiteBlueGreenYellowRed")

#   res.tiXAxisString = "longitude"
#   res.tiXAxisFontHeightF = 0.015
#   res.tiYAxisString = "latitude"
#   res.tiYAxisFontHeightF = 0.015

   res.mpGridAndLimbOn        = False

#   res.tiMainString               = "Dewpoint temperature forecast %s +%03d" % (init_dt[0:10], f_time)
#   res.tiMainFontHeightF          = 0.015
   res.cnFillPalette              = cmap[:30:-1]
   res.cnInfoLabelOn              = False
   res.cnFillOn                   = True
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
   res.lbTitleString         = "2 m dewpoint"
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
   res.mpPerimOn   = True
   res.mpOutlineBoundarySets     = "AllBoundaries"
   res.mpNationalLineColor       = "gray40"
   res.mpNationalLineThicknessF  = 1.5
   res.mpGeophysicalLineColor    = "gray40"
   res.mpGeophysicalLineThicknessF = 1.5
   res.cnMonoLineColor           = True

   res.cnLevelSelectionMode = "ManualLevels"
   res.cnMinLevelValF       = -38.5
   res.cnMaxLevelValF       = 21.0
   res.cnLevelSpacingF      = 2.5
   res.cnLineThicknessF     = 2.5

# create dp plot for analysis data

   dp_plot = ngl.contour_map(wks,dp,res)

   del res.mpProjection
   del res.mpLimitMode
   del res.mpMinLonF
   del res.mpMaxLonF
   del res.mpMinLatF
   del res.mpMaxLatF
   del res.mpPerimOn
   del res.mpOutlineBoundarySets
   del res.mpNationalLineColor
   del res.mpNationalLineThicknessF
   del res.mpGeophysicalLineColor
   del res.mpGeophysicalLineThicknessF
   del res.mpGridAndLimbOn

# if pressure levels are 1000 or 925 hPa mark on 14 degree C contour in black (ITD)

   res.cnFillOn                   = False
   res.cnLineLabelBackgroundColor = -1
   res.cnLineLabelDensityF        = 0.8
   res.cnLineLabelFontColor       = "Black"
   res.cnLineLabelFontHeightF     = 0.015
   res.cnLineLabelPerimOn         = False
   res.cnLineLabelsOn             = True
   res.cnLinesOn                  = True
   res.cnMonoLineLabelFontColor   = True
   res.lbLabelFontHeightF         = 0.01

   res.cnLevelSelectionMode = "ManualLevels"
   res.cnMinLevelValF       = geo_thresh-200.0
   res.cnMaxLevelValF       = geo_thresh+200.0
   res.cnLevelSpacingF      = 200.0
   res.cnLineThicknessF     = 2.5

# plot ITD and overlay on colour contours

   HL_plot = ngl.contour(wks,geo_diff,res)
 
   ngl.overlay(dp_plot,HL_plot)

   ngl.maximize_plot(wks, dp_plot)
   ngl.draw(dp_plot)
   ngl.frame(wks)

   ngl.destroy(wks)
   del res
   del dp
   del geo1
   del geo2
   del geo_diff

###################################################################################################

os.system('mogrify -trim *'+region+'_*DPandHL_2M_SNGL_'+init_dt[0:10]+'*.png')
if region == "WA" or region == "unknownWA":
   os.system('mogrify -resize 886x600 *'+region+'_*DPandHL_2M_SNGL_'+init_dt[0:10]+'*.png')
elif region == "EA" or region == "unknownEA":
   os.system('mogrify -resize 600x733 *'+region+'_*DPandHL_2M_SNGL_'+init_dt[0:10]+'*.png')

os.system('mv *'+region+'_*DPandHL_2M_SNGL_'+init_dt[0:10]+'*.png %s/MARTIN/GFS/'%(GFS_dir)+region+'/'+init_dt[0:10]+'/dewpoint_HL')
