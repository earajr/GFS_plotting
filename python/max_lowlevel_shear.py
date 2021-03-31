###################################################################################################
# Project           : Global Challenges Research Fund (GCRF) African SWIFT (Science for Weather
#                     Information and Forecasting Techniques.
#
# Program name      : winds.py 
#
# Author            : Alexander J. Roberts, University of Leeds, NCAS
# 
# Date created      : Jan 2019
#
# Purpose           : Plot winds images as part of SWIFT_GFSplotting.
#
# Revision History  :
#
# Usage             : Can be used as part of wider plotting repository or independently e.g.
#                     "python3 winds.py time lev lat lon lat lon"
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

###################################################################################################

# Main script to plot winds

# define directory

diri = (os.getcwd())+"/"

# forecast times (currently set to plot 0 to 48 hours)

fore = np.arange(3,73,3)

# accept initialisation time and level as arguments

init_dt = (sys.argv[1])
lev1 = ["925", "900", "850", "800"]
lev2 = ["700", "650", "600", "550", "500"]

# read in domains and accept lat and lon limits as arguments

b = open(diri+"/domains")
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
analysis = nio.open_file(diri+a_fili)

# read pressure levels from analysis file

levs_p1 = analysis.variables["lv_ISBL0"]
levs_p = ['{:.0f}'.format(x) for x in levs_p1[:]/100.0]
del levs_p1

# identify level index

lev_index1 = []
lev_index2 = []

for i in np.arange(0,len(lev1), 1):
   lev_index1.append(levs_p.index(lev1[i]))
for i in np.arange(0,len(lev2), 1):
   lev_index2.append(levs_p.index(lev2[i]))

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

# read in winds, checking whether box crosses Greenwich Meridian.

u1 = np.zeros((len(lev1),len(lat), len(lon)), float)
v1 = np.zeros((len(lev1),len(lat), len(lon)), float)

u2 = np.zeros((len(lev2),len(lat), len(lon)), float)
v2 = np.zeros((len(lev2),len(lat), len(lon)), float)

if (np.sign(lonbl) + np.sign(lontr)) >= -1 and (np.sign(lonbl) + np.sign(lontr)) <= 1:

   for i in np.arange(0,len(lev1),1):
      u_temp = analysis.variables["UGRD_P0_L100_GLL0"][lev_index1[i],:,:]
      u_tempA = u_temp[lat_box1:lat_box2,0:lon_box1]
      u_tempB = u_temp[lat_box1:lat_box2,lon_box2:lon_box3]
      u1[i,:,:] = np.concatenate((u_tempB,u_tempA),axis=1)
      del(u_temp)
      del(u_tempA)
      del(u_tempB)

      v_temp = analysis.variables["VGRD_P0_L100_GLL0"][lev_index1[i],:,:]
      v_tempA = v_temp[lat_box1:lat_box2,0:lon_box1]
      v_tempB = v_temp[lat_box1:lat_box2,lon_box2:lon_box3]
      v1[i,:,:] = np.concatenate((v_tempB,v_tempA),axis=1)
      del(v_temp)
      del(v_tempA)
      del(v_tempB)

   for i in np.arange(0,len(lev2),1):

      u_temp = analysis.variables["UGRD_P0_L100_GLL0"][lev_index2[i],:,:]
      u_tempA = u_temp[lat_box1:lat_box2,0:lon_box1]
      u_tempB = u_temp[lat_box1:lat_box2,lon_box2:lon_box3]
      u2[i,:,:] = np.concatenate((u_tempB,u_tempA),axis=1)
      del(u_temp)
      del(u_tempA)
      del(u_tempB)

      v_temp = analysis.variables["VGRD_P0_L100_GLL0"][lev_index2[i],:,:]
      v_tempA = v_temp[lat_box1:lat_box2,0:lon_box1]
      v_tempB = v_temp[lat_box1:lat_box2,lon_box2:lon_box3]
      v2[i,:,:] = np.concatenate((v_tempB,v_tempA),axis=1)
      del(v_temp)
      del(v_tempA)
      del(v_tempB)

else:

   for i in np.arange(0,len(lev1),1):
      u_temp = analysis.variables["UGRD_P0_L100_GLL0"][lev_index1[i],:,:]
      u1[i,:,:] = u_temp[lat_box1:lat_box2,lon_box1:lon_box2]
      del u_temp

      v_temp = analysis.variables["VGRD_P0_L100_GLL0"][lev_index1[i],:,:]
      v1[i,:,:] = v_temp[lat_box1:lat_box2,lon_box1:lon_box2]
      del v_temp

   for i in np.arange(0,len(lev2),1):
      u_temp = analysis.variables["UGRD_P0_L100_GLL0"][lev_index2[i],:,:]
      u2[i,:,:] = u_temp[lat_box1:lat_box2,lon_box1:lon_box2]
      del u_temp

      v_temp = analysis.variables["VGRD_P0_L100_GLL0"][lev_index2[i],:,:]
      v2[i,:,:] = v_temp[lat_box1:lat_box2,lon_box1:lon_box2]
      del v_temp

# calculate max shear

shear = np.zeros((len(lev1),len(lev2),len(lat), len(lon)), float)
max_shear = np.zeros((len(lat), len(lon)), float)
max_shear_u2_u1 = np.zeros((len(lat), len(lon)), float)
max_shear_v2_v1 = np.zeros((len(lat), len(lon)), float)

for i in np.arange(0,len(lev1),1):
   for j in np.arange(0,len(lev2),1):
      shear[i,j,:,:] = np.sqrt((u2[j]-u1[i])**2.0 + (v2[j]-v1[i])**2.0)

      max_shear_u2_u1 = np.where(shear[i,j,:,:] > max_shear, u2[j]-u1[i], max_shear_u2_u1)
      max_shear_v2_v1 = np.where(shear[i,j,:,:] > max_shear, v2[j]-v1[i], max_shear_v2_v1)
      max_shear = np.where(shear[i,j,:,:] > max_shear, shear[i,j,:,:], max_shear)

# create 2d lat and lon

lat2d = np.zeros((len(lat),len(lon)))
lon2d = np.zeros((len(lat),len(lon)))

for i in range(0, len(lon)):
   lat2d[:,i] = lat

for i in range(0, len(lat)):
   lon2d[i,:] = lon
   
# open workspace for analysis plot

wks_type = "png"
wks = ngl.open_wks(wks_type, "GFSanalysis_%s_%s_max_lowlevel_shear_SNGL" % (region, init_dt[0:10]))

# define resources for analysis plot

res = ngl.Resources()
res.nglDraw                     = False
res.nglFrame                    = False

cmap = ngl.read_colormap_file("WhiteBlueGreenYellowRed")

res.cnLinesOn                   = False
res.cnLineLabelsOn              = False
res.cnFillOn                    = True
res.cnFillPalette               = cmap[15:,:]

res.lbAutoManage          = False
res.lbLabelFontHeightF         = 0.005
res.lbOrientation              = "horizontal"
res.lbLabelAngleF              = 45
res.pmLabelBarOrthogonalPosF = -1.
res.pmLabelBarParallelPosF = 0.25
res.pmLabelBarWidthF      = 0.3
res.pmLabelBarHeightF     = 0.1
res.lbTitleString         = "max shear (m/s)"
res.lbTitleFontHeightF   = 0.0125

res.mpFillOn                    = False
res.mpGeophysicalLineColor      = "Grey18"
res.mpGeophysicalLineThicknessF = 1.5

res.sfXArray                    = lon2d
res.sfYArray                    = lat2d

res.mpGridAndLimbOn        = False
res.pmTickMarkDisplayMode = "Never"

res.cnInfoLabelOn              = False

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

#max_cont = 50.0
#min_cont = 0.0

res.cnLevelSelectionMode = "ExplicitLevels"
res.cnLevels = [10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 22.0, 24.0, 26.0, 28.0, 30.0, 32.0, 34.0, 36.0, 38.0, 40.0]
res.cnFillColors = [-1, 15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165, 180, 195, 210, 225,237 ]

# create shear plot for analysis data

shear_plot = ngl.contour_map(wks,max_shear,res)

# define resources for vectors

vcres                         = ngl.Resources()
vcres.nglDraw                 = False
vcres.nglFrame                = False

vcres.vfXArray                = lon2d
vcres.vfYArray                = lat2d

vcres.vcRefMagnitudeF         = 30.0             # define vector ref mag
vcres.vcRefLengthF            = 0.03             # define length of vec ref
vcres.vcMinFracLengthF        = 0.3
vcres.vcMinDistanceF          = 0.02
vcres.vcRefAnnoOrthogonalPosF = -0.20
vcres.vcRefAnnoFontHeightF    = 0.005
vcres.vcLineArrowThicknessF     = 2.0

# create vector plot for analysis data and overlay on colour contours level 1

uv_plot1  = ngl.vector(wks,max_shear_u2_u1,max_shear_v2_v1,vcres)

# create vector plot for analysis data and overlay on colour contours level2

#vcres.vcLineArrowColor = "Red"
#
#uv_plot2 = ngl.vector(wks,u_2,v_2,vcres)

ngl.overlay(shear_plot,uv_plot1)
#ngl.overlay(shear_plot,uv_plot2)
ngl.maximize_plot(wks, shear_plot)
ngl.draw(shear_plot)
ngl.frame(wks)

ngl.destroy(wks)
del res
del vcres
del u1
del v1
del u2
del v2
del shear
del max_shear
del max_shear_u2_u1
del max_shear_v2_v1

###################################################################################################

# open forecast file

f_fili = "GFS_48h_forecast_%s_%s.nc" % (init_dt[:8], init_dt[8:10])
forecast = nio.open_file(diri+f_fili)

# loop through forecast times

for i in range(0, len(fore)):

# create string for valid time

   valid_date = (datetime.datetime(int(init_dt[:4]), int(init_dt[4:6]), int(init_dt[6:8]), int(init_dt[8:10])) + datetime.timedelta(hours=int(fore[i]))).strftime("%Y%m%d%H")

# read in winds, checking whether box crosses Greenwich Meridian.

   u1 = np.zeros((len(lev1),len(lat), len(lon)), float)
   v1 = np.zeros((len(lev1),len(lat), len(lon)), float)

   u2 = np.zeros((len(lev2),len(lat), len(lon)), float)
   v2 = np.zeros((len(lev2),len(lat), len(lon)), float)

   if (np.sign(lonbl) + np.sign(lontr)) >= -1 and (np.sign(lonbl) + np.sign(lontr)) <= 1:

      for j in np.arange(0,len(lev1),1):
         u_temp = forecast.variables["UGRD_P0_L100_GLL0"][i,lev_index1[j],:,:]
         u_tempA = u_temp[lat_box1:lat_box2,0:lon_box1]
         u_tempB = u_temp[lat_box1:lat_box2,lon_box2:lon_box3]
         u1[j,:,:] = np.concatenate((u_tempB,u_tempA),axis=1)
         del(u_temp)
         del(u_tempA)
         del(u_tempB)
   
         v_temp = forecast.variables["VGRD_P0_L100_GLL0"][i,lev_index1[j],:,:]
         v_tempA = v_temp[lat_box1:lat_box2,0:lon_box1]
         v_tempB = v_temp[lat_box1:lat_box2,lon_box2:lon_box3]
         v1[j,:,:] = np.concatenate((v_tempB,v_tempA),axis=1)
         del(v_temp)
         del(v_tempA)
         del(v_tempB)

      u2 = np.zeros((len(lev2),len(lat), len(lon)), float)
      v2 = np.zeros((len(lev2),len(lat), len(lon)), float)

      for j in np.arange(0,len(lev2),1):

         u_temp = forecast.variables["UGRD_P0_L100_GLL0"][i,lev_index2[j],:,:]
         u_tempA = u_temp[lat_box1:lat_box2,0:lon_box1]
         u_tempB = u_temp[lat_box1:lat_box2,lon_box2:lon_box3]
         u2[j,:,:] = np.concatenate((u_tempB,u_tempA),axis=1)
         del(u_temp)
         del(u_tempA)
         del(u_tempB)

         v_temp = forecast.variables["VGRD_P0_L100_GLL0"][i,lev_index2[j],:,:]
         v_tempA = v_temp[lat_box1:lat_box2,0:lon_box1]
         v_tempB = v_temp[lat_box1:lat_box2,lon_box2:lon_box3]
         v2[j,:,:] = np.concatenate((v_tempB,v_tempA),axis=1)
         del(v_temp)
         del(v_tempA)
         del(v_tempB)

   else:

      for j in np.arange(0,len(lev1),1):
         u_temp = forecast.variables["UGRD_P0_L100_GLL0"][i,lev_index1[j],:,:]
         u1[j,:,:] = u_temp[lat_box1:lat_box2,lon_box1:lon_box2]
         del u_temp

         v_temp = forecast.variables["VGRD_P0_L100_GLL0"][i,lev_index1[j],:,:]
         v1[j,:,:] = v_temp[lat_box1:lat_box2,lon_box1:lon_box2]
         del v_temp

      for j in np.arange(0,len(lev2),1):
         u_temp = forecast.variables["UGRD_P0_L100_GLL0"][i,lev_index2[j],:,:]
         u2[j,:,:] = u_temp[lat_box1:lat_box2,lon_box1:lon_box2]
         del u_temp

         v_temp = forecast.variables["VGRD_P0_L100_GLL0"][i,lev_index2[j],:,:]
         v2[j,:,:] = v_temp[lat_box1:lat_box2,lon_box1:lon_box2]
         del v_temp

   # calculate windspeed

   shear = np.zeros((len(lev1),len(lev2),len(lat), len(lon)), float)
   max_shear = np.zeros((len(lat), len(lon)), float)
   max_shear_u2_u1 = np.zeros((len(lat), len(lon)), float)
   max_shear_v2_v1 = np.zeros((len(lat), len(lon)), float)

   for j in np.arange(0,len(lev1),1):
      for k in np.arange(0,len(lev2),1):
         shear[j,k,:,:] = np.sqrt((u2[k]-u1[j])**2.0 + (v2[k]-v1[j])**2.0)

         max_shear_u2_u1 = np.where(shear[j,k,:,:] > max_shear, u2[k]-u1[j], max_shear_u2_u1)
         max_shear_v2_v1 = np.where(shear[j,k,:,:] > max_shear, v2[k]-v1[j], max_shear_v2_v1)
         max_shear = np.where(shear[j,k,:,:] > max_shear, shear[j,k,:,:], max_shear)

# open workspace for forecast plots

   wks_type = "png"
   wks = ngl.open_wks(wks_type, "GFSforecast_%s_%s_max_lowlevel_shear_SNGL_%s_%03d" % (region, init_dt[0:10], init_dt[0:10], fore[i]))
#   wks = ngl.open_wks(wks_type, "GFSforecast_%s_%s_wind_%shPa_%s_%03d" % (region, valid_date, lev_hPa, init_dt[0:10], fore[i]))

# define resources for forecast plots

   res = ngl.Resources()
   res.nglDraw                     = False
   res.nglFrame                    = False

   cmap = ngl.read_colormap_file("WhiteBlueGreenYellowRed")

   res.cnLinesOn                   = False
   res.cnLineLabelsOn              = False
   res.cnFillOn                    = True
   res.cnFillPalette               = cmap[15:,:]

   res.lbAutoManage          = False
   res.lbLabelFontHeightF         = 0.005
   res.lbOrientation              = "horizontal"
   res.lbLabelAngleF              = 45
   res.pmLabelBarOrthogonalPosF = -1.
   res.pmLabelBarParallelPosF = 0.25
   res.pmLabelBarWidthF      = 0.3
   res.pmLabelBarHeightF     = 0.1
   res.lbTitleString         = "max shear (m/s)"
   res.lbTitleFontHeightF   = 0.0125   

   res.mpFillOn                    = False
   res.mpGeophysicalLineColor      = "Grey18"
   res.mpGeophysicalLineThicknessF = 1.5

   res.sfXArray                    = lon2d
   res.sfYArray                    = lat2d

   res.mpGridAndLimbOn        = False
   res.pmTickMarkDisplayMode = "Never"

   res.cnInfoLabelOn              = False

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

#   max_cont = 50.0
#   min_cont = 0.0

#   res.cnLevelSelectionMode = "ManualLevels"
#   res.cnMinLevelValF       = min_cont
#   res.cnMaxLevelValF       = max_cont
#   res.cnLevelSpacingF      = 2.
#   res.cnLineThicknessF     = 2.5

   res.cnLevelSelectionMode = "ExplicitLevels"
   res.cnLevels = [10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 22.0, 24.0, 26.0, 28.0, 30.0, 32.0, 34.0, 36.0, 38.0, 40.0]
   res.cnFillColors = [-1, 15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165, 180, 195, 210, 225,237 ]

# create ws plot for analysis data

   shear_plot = ngl.contour_map(wks,max_shear,res)


# define resources for vectors

   vcres                         = ngl.Resources()
   vcres.nglDraw                 = False
   vcres.nglFrame                = False

   vcres.vfXArray                = lon2d
   vcres.vfYArray                = lat2d

   #vcres.vcFillArrowsOn          = True
   res.vcLineArrowColor          = "Black"
   vcres.vcRefMagnitudeF         = 30.0             # define vector ref mag
   vcres.vcRefLengthF            = 0.03             # define length of vec ref
   vcres.vcMinFracLengthF        = 0.3
   vcres.vcMinDistanceF          = 0.02
   vcres.vcRefAnnoOrthogonalPosF = -0.20
   vcres.vcRefAnnoFontHeightF    = 0.005
   vcres.vcLineArrowThicknessF     = 2.0

# create vector plot for analysis data and overlay on colour contours

   uv_plot1  = ngl.vector(wks,max_shear_u2_u1,max_shear_v2_v1,vcres)

# create vector plot for analysis data and overlay on colour contours level2

   ngl.overlay(shear_plot,uv_plot1)
   ngl.maximize_plot(wks, shear_plot)
   ngl.draw(shear_plot)
   ngl.frame(wks)

   ngl.destroy(wks)
   del res
   del vcres
   del u1
   del v1
   del u2 
   del v2
   del shear
   del max_shear
   del max_shear_u2_u1
   del max_shear_v2_v1

os.system('mogrify -trim *_'+region+'_'+init_dt[0:10]+'_max_lowlevel_shear_SNGL.png')
if region == "WA" or region == "unknownWA":
   os.system('mogrify -resize 886x600 *_'+region+'_'+init_dt[0:10]+'_max_lowlevel_shear_SNGL.png')
elif region == "EA" or region == "unknownEA":
   os.system('mogrify -resize 600x733 *_'+region+'_'+init_dt[0:10]+'_max_lowlevel_shear_SNGL.png')

os.system('mv *_'+region+'_'+init_dt[0:10]+'_max_lowlevel_shear_SNGL.png MARTIN/GFS/'+region+'/'+init_dt[0:10]+'/max_lowlevel_shear')

os.system('mogrify -trim *'+region+'_*_max_lowlevel_shear_SNGL_'+init_dt[0:10]+'*.png')
if region == "WA" or region == "unknownWA":
   os.system('mogrify -resize 886x600 *'+region+'_*_max_lowlevel_shear_SNGL_'+init_dt[0:10]+'*.png')
elif region == "EA" or region == "unknownEA":
   os.system('mogrify -resize 600x733 *'+region+'_*_max_lowlevel_shear_SNGL_'+init_dt[0:10]+'*.png')

os.system('mv *'+region+'_*_max_lowlevel_shear_SNGL_'+init_dt[0:10]+'*.png MARTIN/GFS/'+region+'/'+init_dt[0:10]+'/max_lowlevel_shear')
