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
lev1_hPa = "925"
lev2_hPa = "700"

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

# read pressure levels from analysis file

analysis = nio.open_file(diri+a_fili)

#####float UGRD_P0_L100_GLL0(lv_ISBL5, lat_0, lon_0) 

levs_p1 = analysis.variables["lv_ISBL5"]
levs_p = ['{:.0f}'.format(x) for x in levs_p1[:]/100.0]
del levs_p1

# identify level index

lev_index1 = levs_p.index(lev1_hPa)
lev_index2 = levs_p.index(lev2_hPa)

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

if (np.sign(lonbl) + np.sign(lontr)) >= -1 and (np.sign(lonbl) + np.sign(lontr)) <= 1:

   u1_1 = analysis.variables["UGRD_P0_L100_GLL0"][lev_index1,:,:]
   u_1_temp1 = u1_1[lat_box1:lat_box2,0:lon_box1]
   u_1_temp2 = u1_1[lat_box1:lat_box2,lon_box2:lon_box3]
   u_1 = np.concatenate((u_1_temp2,u_1_temp1),axis=1)
   del u1_1
   del u_1_temp1
   del u_1_temp2

   v1_1 = analysis.variables["VGRD_P0_L100_GLL0"][lev_index1,:,:]
   v_1_temp1 = v1_1[lat_box1:lat_box2,0:lon_box1]
   v_1_temp2 = v1_1[lat_box1:lat_box2,lon_box2:lon_box3]
   v_1 = np.concatenate((v_1_temp2,v_1_temp1),axis=1)
   del v1_1
   del v_1_temp1
   del v_1_temp2

   u1_2 = analysis.variables["UGRD_P0_L100_GLL0"][lev_index2,:,:]
   u_2_temp1 = u1_2[lat_box1:lat_box2,0:lon_box1]
   u_2_temp2 = u1_2[lat_box1:lat_box2,lon_box2:lon_box3]
   u_2 = np.concatenate((u_2_temp2,u_2_temp1),axis=1)
   del u1_2
   del u_2_temp1
   del u_2_temp2

   v1_2 = analysis.variables["VGRD_P0_L100_GLL0"][lev_index2,:,:]
   v_2_temp1 = v1_2[lat_box1:lat_box2,0:lon_box1]
   v_2_temp2 = v1_2[lat_box1:lat_box2,lon_box2:lon_box3]
   v_2 = np.concatenate((v_2_temp2,v_2_temp1),axis=1)
   del v1_2
   del v_2_temp1
   del v_2_temp2

else:

   u1_1 = analysis.variables["UGRD_P0_L100_GLL0"][lev_index1,:,:]
   u_1 = u1_1[lat_box1:lat_box2,lon_box1:lon_box2]
   del u1_1

   v1_1 = analysis.variables["VGRD_P0_L100_GLL0"][lev_index1,:,:]
   v_1 = v1_1[lat_box1:lat_box2,lon_box1:lon_box2]
   del v1_1

   u1_2 = analysis.variables["UGRD_P0_L100_GLL0"][lev_index2,:,:]
   u_2 = u1_2[lat_box1:lat_box2,lon_box1:lon_box2]
   del u1_2

   v1_2 = analysis.variables["VGRD_P0_L100_GLL0"][lev_index2,:,:]
   v_2 = v1_2[lat_box1:lat_box2,lon_box1:lon_box2]
   del v1_2

# calculate windspeed

#ws = np.sqrt(u**2.0 + v**2.0)

shear = np.sqrt((u_2-u_1)**2.0 + (v_2-v_1)**2.0)

# create 2d lat and lon

lat2d = np.zeros((len(lat),len(lon)))
lon2d = np.zeros((len(lat),len(lon)))

for i in range(0, len(lon)):
   lat2d[:,i] = lat

for i in range(0, len(lat)):
   lon2d[i,:] = lon
   
# open workspace for analysis plot

wks_type = "png"
wks = ngl.open_wks(wks_type, "GFSanalysis_%s_%s_shear_%shPa_%shPa" % (region, init_dt[0:10], lev1_hPa, lev2_hPa))

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
res.lbTitleString         = "%shPa to %shPa shear (m/s)" % (lev1_hPa, lev2_hPa)
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

shear_plot = ngl.contour_map(wks,shear,res)

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

uv_plot1  = ngl.vector(wks,u_1,v_1,vcres)

# create vector plot for analysis data and overlay on colour contours level2

vcres.vcLineArrowColor = "Red"

uv_plot2 = ngl.vector(wks,u_2,v_2,vcres)

ngl.overlay(shear_plot,uv_plot1)
ngl.overlay(shear_plot,uv_plot2)
ngl.maximize_plot(wks, shear_plot)
ngl.draw(shear_plot)
ngl.frame(wks)

ngl.destroy(wks)
del res
del vcres


###################################################################################################

# open forecast file

f_fili = "GFS_48h_forecast_%s_%s.nc" % (init_dt[:8], init_dt[8:10])
forecast = nio.open_file(diri+f_fili)

# loop through forecast times

for i in range(0, len(fore)):

# create string for valid time

   valid_date = (datetime.datetime(int(init_dt[:4]), int(init_dt[4:6]), int(init_dt[6:8]), int(init_dt[8:10])) + datetime.timedelta(hours=int(fore[i]))).strftime("%Y%m%d%H")

# read in winds, checking whether box crosses Greenwich Meridian.

   if (np.sign(lonbl) + np.sign(lontr)) >= -1 and (np.sign(lonbl) + np.sign(lontr)) <= 1:

      u1_1 = forecast.variables["UGRD_P0_L100_GLL0"][i,lev_index1,:,:]
      u_1_temp1 = u1_1[lat_box1:lat_box2,0:lon_box1]
      u_1_temp2 = u1_1[lat_box1:lat_box2,lon_box2:lon_box3]
      u_1 = np.concatenate((u_1_temp2,u_1_temp1),axis=1)
      del u1_1
      del u_1_temp1
      del u_1_temp2

      v1_1 = forecast.variables["VGRD_P0_L100_GLL0"][i,lev_index1,:,:]
      v_1_temp1 = v1_1[lat_box1:lat_box2,0:lon_box1]
      v_1_temp2 = v1_1[lat_box1:lat_box2,lon_box2:lon_box3]
      v_1 = np.concatenate((v_1_temp2,v_1_temp1),axis=1)
      del v1_1
      del v_1_temp1
      del v_1_temp2

      u1_2 = forecast.variables["UGRD_P0_L100_GLL0"][i,lev_index2,:,:]
      u_2_temp1 = u1_2[lat_box1:lat_box2,0:lon_box1]
      u_2_temp2 = u1_2[lat_box1:lat_box2,lon_box2:lon_box3]
      u_2 = np.concatenate((u_2_temp2,u_2_temp1),axis=1)
      del u1_2
      del u_2_temp1
      del u_2_temp2

      v1_2 = forecast.variables["VGRD_P0_L100_GLL0"][i,lev_index2,:,:]
      v_2_temp1 = v1_2[lat_box1:lat_box2,0:lon_box1]
      v_2_temp2 = v1_2[lat_box1:lat_box2,lon_box2:lon_box3]
      v_2 = np.concatenate((v_2_temp2,v_2_temp1),axis=1)
      del v1_2
      del v_2_temp1
      del v_2_temp2

   else:

      u1_1 = forecast.variables["UGRD_P0_L100_GLL0"][i, lev_index1,:,:]
      u_1 = u1_1[lat_box1:lat_box2,lon_box1:lon_box2]
      del u1_1

      v1_1 = forecast.variables["VGRD_P0_L100_GLL0"][i, lev_index1,:,:]
      v_1 = v1_1[lat_box1:lat_box2,lon_box1:lon_box2]
      del v1_1

      u1_2 = forecast.variables["UGRD_P0_L100_GLL0"][i, lev_index2,:,:]
      u_2 = u1_2[lat_box1:lat_box2,lon_box1:lon_box2]
      del u1_2

      v1_2 = forecast.variables["VGRD_P0_L100_GLL0"][i, lev_index2,:,:]
      v_2 = v1_2[lat_box1:lat_box2,lon_box1:lon_box2]
      del v1_2


#   if (np.sign(lonbl) + np.sign(lontr)) >= -1 and (np.sign(lonbl) + np.sign(lontr)) <= 1:
#
#      u1 = forecast.variables["UGRD_P0_L100_GLL0"][i,lev_index,:,:]
#      u_temp1 = u1[lat_box1:lat_box2,0:lon_box1]
#      u_temp2 = u1[lat_box1:lat_box2,lon_box2:lon_box3]
#      u = np.concatenate((u_temp2,u_temp1),axis=1)
#      del u1 
#      del u_temp1
#      del u_temp2
#
#      v1 = forecast.variables["VGRD_P0_L100_GLL0"][i,lev_index,:,:]
#      v_temp1 = v1[lat_box1:lat_box2,0:lon_box1]
#      v_temp2 = v1[lat_box1:lat_box2,lon_box2:lon_box3]
#      v = np.concatenate((v_temp2,v_temp1),axis=1)
#      del v1
#      del v_temp1
#      del v_temp2
#
#   else:
#
#      u1 = forecast.variables["UGRD_P0_L100_GLL0"][i,lev_index,:,:]
#      u = u1[lat_box1:lat_box2,lon_box1:lon_box2]
#      del u1
#
#      v1 = forecast.variables["VGRD_P0_L100_GLL0"][i,lev_index,:,:]
#      v = v1[lat_box1:lat_box2,lon_box1:lon_box2]
#      del v1
#
# calculate shear

#   ws = np.sqrt(u**2.0 + v**2.0)

   shear = np.sqrt((u_2-u_1)**2.0 + (v_2-v_1)**2.0)


# open workspace for forecast plots

   wks_type = "png"
   wks = ngl.open_wks(wks_type, "GFSforecast_%s_%s_shear_%shPa_%shPa_%s_%03d" % (region, init_dt[0:10], lev1_hPa, lev2_hPa, init_dt[0:10], fore[i]))
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
   res.lbTitleString         = "%shPa to %shPa shear (m/s)" % (lev1_hPa, lev2_hPa)
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

#   ws_plot = ngl.contour_map(wks,ws,res)
   shear_plot = ngl.contour_map(wks,shear,res)


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

   uv_plot1  = ngl.vector(wks,u_1,v_1,vcres)

# create vector plot for analysis data and overlay on colour contours level2

   vcres.vcLineArrowColor = "Red"

   uv_plot2 = ngl.vector(wks,u_2,v_2,vcres)

   ngl.overlay(shear_plot,uv_plot1)
   ngl.overlay(shear_plot,uv_plot2)
   ngl.maximize_plot(wks, shear_plot)
   ngl.draw(shear_plot)
   ngl.frame(wks)

   ngl.destroy(wks)
   del res
   del vcres

#GFSanalysis_WA_2021032206_shear_925hPa_700hPa.png
#GFSforecast_WA_2021032206_shear_925hPa_700hPa_2021032206_033.png

os.system('mogrify -trim *_'+region+'_'+init_dt[0:10]+'_shear_'+lev1_hPa+'hPa_'+lev2_hPa+'hPa.png')
if region == "WA" or region == "unknownWA":
   os.system('mogrify -resize 886x600 *_'+region+'_'+init_dt[0:10]+'_shear_'+lev1_hPa+'hPa_'+lev2_hPa+'hPa.png')
elif region == "EA" or region == "unknownEA":
   os.system('mogrify -resize 600x733 *_'+region+'_'+init_dt[0:10]+'_shear_'+lev1_hPa+'hPa_'+lev2_hPa+'hPa.png')

os.system('mv *_'+region+'_'+init_dt[0:10]+'_shear_'+lev1_hPa+'hPa_'+lev2_hPa+'hPa.png MARTIN/GFS/'+region+'/'+init_dt[0:10]+'/shear_'+lev1_hPa+'_'+lev2_hPa)

os.system('mogrify -trim *'+region+'_*_shear_'+lev1_hPa+'hPa_'+lev2_hPa+'hPa_'+init_dt[0:10]+'*.png')
if region == "WA" or region == "unknownWA":
   os.system('mogrify -resize 886x600 *'+region+'_*_shear_'+lev1_hPa+'hPa_'+lev2_hPa+'hPa_'+init_dt[0:10]+'*.png')
elif region == "EA" or region == "unknownEA":
   os.system('mogrify -resize 600x733 *'+region+'_*_shear_'+lev1_hPa+'hPa_'+lev2_hPa+'hPa_'+init_dt[0:10]+'*.png')

os.system('mv *'+region+'_*_shear_'+lev1_hPa+'hPa_'+lev2_hPa+'hPa_'+init_dt[0:10]+'*.png MARTIN/GFS/'+region+'/'+init_dt[0:10]+'/shear_'+lev1_hPa+'_'+lev2_hPa)

