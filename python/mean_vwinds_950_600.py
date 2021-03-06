###################################################################################################
# Project           : Global Challenges Research Fund (GCRF) African SWIFT (Science for Weather
#                     Information and Forecasting Techniques.
#
# Program name      : mean_vwinds_950_600.py 
#
# Author            : Alexander J. Roberts, University of Leeds, NCAS
# 
# Date created      : April 2019
#
# Purpose           : Mean meridional windspeed for pressure levels between 925 hPa and 650 hPa. This
#                     measure is particularly useful for the identification of African Easterly Waves
#                     over West Africa.
#
# Revision History  :
#
# Usage             : Can be used as part of wider plotting repository or independently e.g.
#                     "python3 mean_vwinds_950_600.py time lat lon lat lon"
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

# Main script to plot mean meridional winds between 925 and 650 hPa

# define directory

diri = (os.getcwd())+"/"

# define pressure levels

lev1 = "950"
lev2 = "600"

# forecast times (currently set to 0 to 48 hours)

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

# read in analysis files

a_fili = "analysis_gfs_4_%s_%s00_000.nc" % (init_dt[:8], init_dt[8:10])

# read pressure levels from analysis file

analysis = nio.open_file(diri+a_fili)

level_dim = analysis.variables["UGRD_P0_L100_GLL0"].dimensions[0]

levs_p1 = analysis.variables[level_dim]
levs_p = ['{:.0f}'.format(x) for x in levs_p1[:]/100.0]
del levs_p1

# identify level index

lev1_index = levs_p.index(lev1)
lev2_index = levs_p.index(lev2)

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

   u1 = analysis.variables["UGRD_P0_L100_GLL0"][lev2_index:lev1_index,:,:]
   u_temp1 = np.mean(u1[:,lat_box1:lat_box2,0:lon_box1], axis = 0)
   u_temp2 = np.mean(u1[:,lat_box1:lat_box2,lon_box2:lon_box3], axis = 0)
   u = np.concatenate((u_temp2,u_temp1),axis=1)
   del u1
   del u_temp1
   del u_temp2

   v1 = analysis.variables["VGRD_P0_L100_GLL0"][lev2_index:lev1_index,:,:]
   v_temp1 = np.mean(v1[:,lat_box1:lat_box2,0:lon_box1], axis=0)
   v_temp2 = np.mean(v1[:,lat_box1:lat_box2,lon_box2:lon_box3], axis = 0)
   v = np.concatenate((v_temp2,v_temp1),axis=1)
   del v1
   del v_temp1
   del v_temp2

else:
   
   u1 = analysis.variables["UGRD_P0_L100_GLL0"][lev2_index:lev1_index,:,:]
   u = np.mean(u1[:,lat_box1:lat_box2,lon_box1:lon_box2], axis = 0)
   del u1

   v1 = analysis.variables["VGRD_P0_L100_GLL0"][lev2_index:lev1_index,:,:]
   v = np.mean(v1[:,lat_box1:lat_box2,lon_box1:lon_box2], axis = 0)
   del v1

# create 2d lat and lon

lat2d = np.zeros((len(lat),len(lon)))
lon2d = np.zeros((len(lat),len(lon)))

for i in range(0, len(lon)):
   lat2d[:,i] = lat

for i in range(0, len(lat)):
   lon2d[i,:] = lon
   
# open workspace for analysis plot

wks_type = "png"
wks = ngl.open_wks(wks_type, "GFSanalysis_%s_%s_meanVwinds_%shPa_%shPa_SNGL" % (region, init_dt[0:10], lev1, lev2))

# define resources for analysis plot

res = ngl.Resources()
res.nglDraw                     = False
res.nglFrame                    = False

res.vpWidthF  = 0.9
res.vpHeightF = 0.6

cmap = ngl.read_colormap_file("BlueRed")

res.pmTickMarkDisplayMode = "Never"

res.cnLinesOn                   = False
res.cnLineLabelsOn              = False
res.cnFillOn                    = True
res.cnFillPalette               = cmap

res.lbAutoManage          = False
res.lbLabelFontHeightF         = 0.005
res.lbOrientation              = "horizontal"
res.lbLabelAngleF              = 45
res.pmLabelBarOrthogonalPosF = -1.
res.pmLabelBarParallelPosF = 0.25
res.pmLabelBarWidthF      = 0.3
res.pmLabelBarHeightF     = 0.1
res.lbTitleString         = "%shPa to %shPa mean v winds " % (lev1, lev2)
res.lbTitleFontHeightF   = 0.0125

res.mpFillOn                    = False
res.mpGeophysicalLineColor      = "Grey18"
res.mpGeophysicalLineThicknessF = 1.5

res.sfXArray                    = lon2d
res.sfYArray                    = lat2d

res.mpGridAndLimbOn        = False

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

max_cont = 10.0
min_cont = -10.0

res.cnLevelSelectionMode = "ManualLevels"
res.cnMinLevelValF       = min_cont
res.cnMaxLevelValF       = max_cont
res.cnLevelSpacingF      = 1.
res.cnLineThicknessF     = 2.5 

# create ws plot for analysis data

ws_plot = ngl.contour_map(wks,v,res)

# define resources for vectors

vcres                         = ngl.Resources()
vcres.nglDraw                 = False
vcres.nglFrame                = False

vcres.vfXArray                = lon2d
vcres.vfYArray                = lat2d

#vcres.vcFillArrowsOn          = True
vcres.vcRefMagnitudeF         = 30.0             # define vector ref mag
vcres.vcRefLengthF            = 0.03             # define length of vec ref
vcres.vcMinFracLengthF        = 0.3
vcres.vcMinDistanceF          = 0.02
vcres.vcRefAnnoOrthogonalPosF = -0.20
vcres.vcRefAnnoFontHeightF    = 0.005
vcres.vcLineArrowThicknessF     = 2.0
vcres.vcRefAnnoOrthogonalPosF   = -0.06
vcres.vcRefAnnoParallelPosF     = 0.094

# create vector plot for analysis data and overlay on colour contours

uv_plot  = ngl.vector(wks,u,v,vcres)

ngl.overlay(ws_plot,uv_plot)
ngl.maximize_plot(wks, ws_plot)
ngl.draw(ws_plot)
ngl.frame(wks)

ngl.destroy(wks)
del res
del vcres

###################################################################################################

# open forecast file

f_fili = "GFS_forecast_%s_%s.nc" % (init_dt[:8], init_dt[8:10])
forecast = nio.open_file(diri+f_fili)

# loop through forecast times

for i in range(0, len(fore)):

# create string for valid time

   valid_date = (datetime.datetime(int(init_dt[:4]), int(init_dt[4:6]), int(init_dt[6:8]), int(init_dt[8:10])) + datetime.timedelta(hours=int(fore[i]))).strftime("%Y%m%d%H")

# read in winds, checking whether box crosses Greenwich Meridian.

   if (np.sign(lonbl) + np.sign(lontr)) >= -1 and (np.sign(lonbl) + np.sign(lontr)) <= 1:

      u1 = forecast.variables["UGRD_P0_L100_GLL0"][i,lev2_index:lev1_index,:,:]
      u_temp1 = np.mean(u1[:,lat_box1:lat_box2,0:lon_box1], axis = 0)
      u_temp2 = np.mean(u1[:,lat_box1:lat_box2,lon_box2:lon_box3], axis = 0)
      u = np.concatenate((u_temp2,u_temp1),axis=1)
      del u1 
      del u_temp1
      del u_temp2

      v1 = forecast.variables["VGRD_P0_L100_GLL0"][i,lev2_index:lev1_index,:,:]
      v_temp1 = np.mean(v1[:,lat_box1:lat_box2,0:lon_box1], axis = 0)
      v_temp2 = np.mean(v1[:,lat_box1:lat_box2,lon_box2:lon_box3], axis = 0)
      v = np.concatenate((v_temp2,v_temp1),axis=1)
      del v1
      del v_temp1
      del v_temp2

   else:
 
      u1 = forecast.variables["UGRD_P0_L100_GLL0"][i,lev2_index:lev1_index,:,:]
      u = np.mean(u1[:,lat_box1:lat_box2,lon_box1:lon_box2], axis = 0)
      del u1

      v1 = forecast.variables["VGRD_P0_L100_GLL0"][i,lev2_index:lev1_index,:,:]
      v = np.mean(v1[:,lat_box1:lat_box2,lon_box1:lon_box2], axis = 0)
      del v1

# open workspace for forecast plots

   wks_type = "png"
   wks = ngl.open_wks(wks_type, "GFSforecast_%s_%s_meanVwinds_%shPa_%shPa_SNGL_%s_%03d" % (region, valid_date, lev1, lev2, init_dt[0:10], fore[i]))

# define resources for forecast plots

   res = ngl.Resources()
   res.nglDraw                     = False
   res.nglFrame                    = False

   res.vpWidthF  = 0.9
   res.vpHeightF = 0.6

   cmap = ngl.read_colormap_file("BlueRed")

   res.pmTickMarkDisplayMode = "Never"

   res.cnLinesOn                   = False
   res.cnLineLabelsOn              = False
   res.cnFillOn                    = True
   res.cnFillPalette               = cmap

   res.lbAutoManage          = False
   res.lbLabelFontHeightF         = 0.005
   res.lbOrientation              = "horizontal"
   res.lbLabelAngleF              = 45
   res.pmLabelBarOrthogonalPosF = -1.
   res.pmLabelBarParallelPosF = 0.25
   res.pmLabelBarWidthF      = 0.3
   res.pmLabelBarHeightF     = 0.1
   res.lbTitleString         = "%shPa to %shPa mean v winds " % (lev1, lev2)
   res.lbTitleFontHeightF   = 0.0125

   res.mpFillOn                    = False
   res.mpGeophysicalLineColor      = "Grey18"
   res.mpGeophysicalLineThicknessF = 1.5

   res.sfXArray                    = lon2d
   res.sfYArray                    = lat2d

   res.mpGridAndLimbOn        = False

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

   max_cont = 10.0
   min_cont = -10.0

   res.cnLevelSelectionMode = "ManualLevels"
   res.cnMinLevelValF       = min_cont
   res.cnMaxLevelValF       = max_cont
   res.cnLevelSpacingF      = 1.
   res.cnLineThicknessF     = 2.5

# create ws plot for analysis data

   ws_plot = ngl.contour_map(wks,v,res)

# define resources for vectors

   vcres                         = ngl.Resources()
   vcres.nglDraw                 = False
   vcres.nglFrame                = False

   vcres.vfXArray                = lon2d
   vcres.vfYArray                = lat2d

   #vcres.vcFillArrowsOn          = True
   vcres.vcRefMagnitudeF         = 30.0             # define vector ref mag
   vcres.vcRefLengthF            = 0.03             # define length of vec ref
   vcres.vcMinFracLengthF        = 0.3
   vcres.vcMinDistanceF          = 0.02
   vcres.vcRefAnnoOrthogonalPosF = -0.20
   vcres.vcRefAnnoFontHeightF    = 0.005
   vcres.vcLineArrowThicknessF     = 2.0
   vcres.vcRefAnnoOrthogonalPosF   = -0.06
   vcres.vcRefAnnoParallelPosF     = 0.094

# create vector plot for analysis data and overlay on colour contours

   uv_plot  = ngl.vector(wks,u,v,vcres)

   ngl.overlay(ws_plot,uv_plot)
   ngl.maximize_plot(wks, ws_plot)
   ngl.draw(ws_plot)
   ngl.frame(wks)

   ngl.destroy(wks)
   del res
   del vcres

os.system('mogrify -trim *_'+region+'_'+init_dt[0:10]+'_meanVwinds_'+lev1+'hPa_'+lev2+'hPa_SNGL.png')
#if region == "WA" or region == "unknownWA":
#   os.system('mogrify -resize 886x600 *_'+region+'_'+init_dt[0:10]+'_meanVwinds_'+lev1+'hPa_'+lev2+'hPa_SNGL.png')
#elif region == "EA" or region == "unknownEA":
#   os.system('mogrify -resize 600x733 *_'+region+'_'+init_dt[0:10]+'_meanVwinds_'+lev1+'hPa_'+lev2+'hPa_SNGL.png')

os.system('mv *_'+region+'_'+init_dt[0:10]+'_meanVwinds_'+lev1+'hPa_'+lev2+'hPa_SNGL.png %s/MARTIN/GFS/'%(GFS_dir)+region+'/'+init_dt[0:10]+'/mean_vwinds_950_600')

os.system('mogrify -trim *'+region+'_*meanVwinds_'+lev1+'hPa_'+lev2+'hPa_SNGL_'+init_dt[0:10]+'*.png')
#if region == "WA" or region == "unknownWA":
#   os.system('mogrify -resize 886x600 *'+region+'_*meanVwinds_'+lev1+'hPa_'+lev2+'hPa_SNGL_'+init_dt[0:10]+'*.png')
#elif region == "EA" or region == "unknownEA":
#   os.system('mogrify -resize 600x733 *'+region+'_*meanVwinds_'+lev1+'hPa_'+lev2+'hPa_SNGL_'+init_dt[0:10]+'*.png')

os.system('mv *'+region+'_*meanVwinds_'+lev1+'hPa_'+lev2+'hPa_SNGL_'+init_dt[0:10]+'*.png %s/MARTIN/GFS/'%(GFS_dir)+region+'/'+init_dt[0:10]+'/mean_vwinds_950_600')




