###################################################################################################
# Project           : Global Challenges Research Fund (GCRF) African SWIFT (Science for Weather
#                     Information and Forecasting Techniques.
#
# Program name      : CAPE_CIN.py 
#
# Author            : Alexander J. Roberts, University of Leeds, NCAS
# 
# Date created      : Jan 2019
#
# Purpose           : Plot CAPE and CIN images as part of SWIFT_GFSplotting.
#
# Revision History  :
#
# Usage             : Can be used as part of wider plotting repository or independently e.g.
#                     "python3 CAPE_CIN.py time lat lon lat lon"
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

# Main script to plot KI TCWV and max shear

# define directory

diri = (os.getcwd())+"/"

# forecast times (currently set to plot 0 to 48 hours)

fore = np.arange(3,73,3)

# accept initialisation time and dates as an argument

init_dt = (sys.argv[1])
lev1 = ["925", "900", "850", "800"]
lev2 = ["700", "650", "600", "550", "500"]

# read in domains and accept lat and lon limits as arguments

b = open(diri+"/domains")
domains_content = b.readlines()

key_list = []
latlon_list = []

for domain in domains_content:
   key_list.append(domain.split(":")[0].strip())
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
      
# read in KI, PWAT and winds, checking whether box crosses Greenwich Meridian.

u1 = np.zeros((len(lev1),len(lat), len(lon)), float)
v1 = np.zeros((len(lev1),len(lat), len(lon)), float)

u2 = np.zeros((len(lev2),len(lat), len(lon)), float)
v2 = np.zeros((len(lev2),len(lat), len(lon)), float)

if (np.sign(lonbl) + np.sign(lontr)) >= -1 and (np.sign(lonbl) + np.sign(lontr)) <= 1:

   T8501 = analysis.variables["TMP_P0_L100_GLL0"][lev_index1[2],:,:]-273.15
   T850_temp1 = T8501[lat_box1:lat_box2,0:lon_box1]
   T850_temp2 = T8501[lat_box1:lat_box2,lon_box2:lon_box3]
   T850 = np.concatenate((T850_temp2,T850_temp1),axis=1)
   del T8501
   del T850_temp1
   del T850_temp2

   RH8501 = analysis.variables["RH_P0_L100_GLL0"][lev_index1[2],:,:]
   RH850_temp1 = RH8501[lat_box1:lat_box2,0:lon_box1]
   RH850_temp2 = RH8501[lat_box1:lat_box2,lon_box2:lon_box3]
   RH850 = np.concatenate((RH850_temp2,RH850_temp1),axis=1)
   del RH8501
   del RH850_temp1
   del RH850_temp2

   T7001 = analysis.variables["TMP_P0_L100_GLL0"][lev_index2[0],:,:]-273.15
   T700_temp1 = T7001[lat_box1:lat_box2,0:lon_box1]
   T700_temp2 = T7001[lat_box1:lat_box2,lon_box2:lon_box3]
   T700 = np.concatenate((T700_temp2,T700_temp1),axis=1)
   del T7001
   del T700_temp1
   del T700_temp2

   RH7001 = analysis.variables["RH_P0_L100_GLL0"][lev_index2[0],:,:]
   RH700_temp1 = RH7001[lat_box1:lat_box2,0:lon_box1]
   RH700_temp2 = RH7001[lat_box1:lat_box2,lon_box2:lon_box3]
   RH700 = np.concatenate((RH700_temp2,RH700_temp1),axis=1)
   del RH7001
   del RH700_temp1
   del RH700_temp2

   T5001 = analysis.variables["TMP_P0_L100_GLL0"][lev_index2[4],:,:]-273.15
   T500_temp1 = T5001[lat_box1:lat_box2,0:lon_box1]
   T500_temp2 = T5001[lat_box1:lat_box2,lon_box2:lon_box3]
   T500 = np.concatenate((T500_temp2,T500_temp1),axis=1)
   del T5001
   del T500_temp1
   del T500_temp2

   PWAT1 = analysis.variables["PWAT_P0_L200_GLL0"][:,:]
   PWAT_temp1 = PWAT1[lat_box1:lat_box2,0:lon_box1]
   PWAT_temp2 = PWAT1[lat_box1:lat_box2,lon_box2:lon_box3]
   PWAT = np.concatenate((PWAT_temp2,PWAT_temp1),axis=1)
   del PWAT1
   del PWAT_temp1
   del PWAT_temp2

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

   T8501 = analysis.variables["TMP_P0_L100_GLL0"][lev_index1[2],:,:]-273.15
   T850 = T8501[lat_box1:lat_box2,lon_box1:lon_box2]
   del(T8501)

   RH8501 = analysis.variables["RH_P0_L100_GLL0"][lev_index1[2],:,:]
   RH850 = RH8501[lat_box1:lat_box2,lon_box1:lon_box2]
   del(RH8501)

   T7001 = analysis.variables["TMP_P0_L100_GLL0"][lev_index2[0],:,:]-273.15
   T700 = T7001[lat_box1:lat_box2,lon_box1:lon_box2]
   del(T7001)

   RH7001 = analysis.variables["RH_P0_L100_GLL0"][lev_index2[0],:,:]
   RH700 = RH7001[lat_box1:lat_box2,lon_box1:lon_box2]
   del(RH7001)

   T5001 = analysis.variables["TMP_P0_L100_GLL0"][lev_index2[4],:,:]-273.15
   T500 = T5001[lat_box1:lat_box2,lon_box1:lon_box2]
   del(T5001)

   PWAT1 = analysis.variables["PWAT_P0_L200_GLL0"][:,:]
   PWAT = PWAT1[lat_box1:lat_box2,lon_box1:lon_box2]
   del PWAT1

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

#calculate max shear and KI

Td850 = T850 - ((100.0-RH850)/5.0)
Td700 = T700 - ((100.0-RH700)/5.0)
KI = (T850-T500)+Td850-(T700-Td700)

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

imagename = "GFSanalysis_%s_%s_KI_PWAT_maxshear_SNGL" % (region, init_dt[0:10])

wks_type = "png"
wks_res = ngl.Resources()
wks_res.wkBackgroundOpacityF = 0.0
wks = ngl.open_wks(wks_type, imagename, wks_res)

# define resources for analysis plot

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
res.lbTitleString         = "K Index"
res.lbTitleFontHeightF   = 0.0125

res.sfXArray = lon2d
res.sfYArray = lat2d

res.pmTickMarkDisplayMode = "Never"
#res.mpPerimOn   =  False
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

res.cnLevelSelectionMode = "ManualLevels"
res.cnMinLevelValF       = 15.0
res.cnMaxLevelValF       = 45.0
res.cnLevelSpacingF      = 1.5

res.cnFillColors = [-1, 6, 17, 28, 39, 50, 61, 72, 83, 94, 105, 116, 127, 138, 149, 160, 171, 182, 193, 204, 215, 226]

# create KI plot for analysis data

KI_plot = ngl.contour_map(wks,KI,res)

del res.mpProjection
del res.mpLimitMode
del res.mpMinLonF
del res.mpMaxLonF
del res.mpMinLatF
del res.mpMaxLatF
del res.mpOutlineBoundarySets
del res.mpNationalLineColor
del res.mpNationalLineThicknessF
del res.mpGeophysicalLineColor
del res.mpGeophysicalLineThicknessF
del res.mpGridAndLimbOn

res.cnMonoLineColor           = True
res.cnFillOn                   = False
res.cnLineLabelBackgroundColor = -1
res.cnLineLabelDensityF        = 0.8
res.cnLineLabelFontColor       = "Red"
res.cnLineColor                = "Red"
res.cnLineLabelFontHeightF     = 0.01
res.cnLineLabelPerimOn         = False
res.cnLineLabelsOn             = True
res.cnLineLabelInterval        = 1
res.cnLinesOn                  = True
res.cnMonoLineLabelFontColor   = True
res.lbLabelFontHeightF         = 0.0075
res.cnLineThicknessF           = 2.5
res.cnInfoLabelOn              = True
res.cnInfoLabelString          = "PWAT Contours at 15, 30, 45 and 60 mm"
res.cnInfoLabelOrthogonalPosF  = -0.06
res.cnInfoLabelParallelPosF    = 0.505
res.cnLineLabelPlacementMode = "constant"
 
res.cnLevelSelectionMode = "ManualLevels"
res.cnMinLevelValF       = 15.0
res.cnMaxLevelValF       = 60.0
res.cnLevelSpacingF      = 15.0
res.cnLineThicknessF     = 2.5

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

PWAT_plot = ngl.contour(wks,PWAT,res)

ngl.overlay(KI_plot,uv_plot1)
ngl.overlay(KI_plot,PWAT_plot)

ngl.maximize_plot(wks, KI_plot)
ngl.draw(KI_plot)
ngl.frame(wks)

ngl.destroy(wks)
del res
del T850
del Td850
del RH850
del T700
del Td700
del RH700
del T500
del KI
del PWAT
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

# create valid date and time string

   valid_date = (datetime.datetime(int(init_dt[:4]), int(init_dt[4:6]), int(init_dt[6:8]), int(init_dt[8:10])) + datetime.timedelta(hours=int(fore[i]))).strftime("%Y%m%d%H")

# read in KI, PWAT and winds, checking whether box crosses Greenwich Meridian.

# read in KI, PWAT and winds, checking whether box crosses Greenwich Meridian.

   u1 = np.zeros((len(lev1),len(lat), len(lon)), float)
   v1 = np.zeros((len(lev1),len(lat), len(lon)), float)

   u2 = np.zeros((len(lev2),len(lat), len(lon)), float)
   v2 = np.zeros((len(lev2),len(lat), len(lon)), float)

   if (np.sign(lonbl) + np.sign(lontr)) >= -1 and (np.sign(lonbl) + np.sign(lontr)) <= 1:

      T8501 = forecast.variables["TMP_P0_L100_GLL0"][i,lev_index1[2],:,:]-273.15
      T850_temp1 = T8501[lat_box1:lat_box2,0:lon_box1]
      T850_temp2 = T8501[lat_box1:lat_box2,lon_box2:lon_box3]
      T850 = np.concatenate((T850_temp2,T850_temp1),axis=1)
      del T8501
      del T850_temp1
      del T850_temp2

      RH8501 = forecast.variables["RH_P0_L100_GLL0"][i,lev_index1[2],:,:]
      RH850_temp1 = RH8501[lat_box1:lat_box2,0:lon_box1]
      RH850_temp2 = RH8501[lat_box1:lat_box2,lon_box2:lon_box3]
      RH850 = np.concatenate((RH850_temp2,RH850_temp1),axis=1)
      del RH8501
      del RH850_temp1
      del RH850_temp2

      T7001 = forecast.variables["TMP_P0_L100_GLL0"][i,lev_index2[0],:,:]-273.15
      T700_temp1 = T7001[lat_box1:lat_box2,0:lon_box1]
      T700_temp2 = T7001[lat_box1:lat_box2,lon_box2:lon_box3]
      T700 = np.concatenate((T700_temp2,T700_temp1),axis=1)
      del T7001
      del T700_temp1
      del T700_temp2

      RH7001 = forecast.variables["RH_P0_L100_GLL0"][i,lev_index2[0],:,:]
      RH700_temp1 = RH7001[lat_box1:lat_box2,0:lon_box1]
      RH700_temp2 = RH7001[lat_box1:lat_box2,lon_box2:lon_box3]
      RH700 = np.concatenate((RH700_temp2,RH700_temp1),axis=1)
      del RH7001
      del RH700_temp1
      del RH700_temp2

      T5001 = forecast.variables["TMP_P0_L100_GLL0"][i,lev_index2[4],:,:]-273.15
      T500_temp1 = T5001[lat_box1:lat_box2,0:lon_box1]
      T500_temp2 = T5001[lat_box1:lat_box2,lon_box2:lon_box3]
      T500 = np.concatenate((T500_temp2,T500_temp1),axis=1)
      del T5001
      del T500_temp1
      del T500_temp2

      PWAT1 = forecast.variables["PWAT_P0_L200_GLL0"][i,:,:]
      PWAT_temp1 = PWAT1[lat_box1:lat_box2,0:lon_box1]
      PWAT_temp2 = PWAT1[lat_box1:lat_box2,lon_box2:lon_box3]
      PWAT = np.concatenate((PWAT_temp2,PWAT_temp1),axis=1)
      del PWAT1
      del PWAT_temp1
      del PWAT_temp2

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

      T8501 = forecast.variables["TMP_P0_L100_GLL0"][i,lev_index1[2],:,:]-273.15
      T850 = T8501[lat_box1:lat_box2,lon_box1:lon_box2]
      del(T8501)

      RH8501 =forecast.variables["RH_P0_L100_GLL0"][i,lev_index1[2],:,:]
      RH850 = RH8501[lat_box1:lat_box2,lon_box1:lon_box2]
      del(RH8501)

      T7001 = forecast.variables["TMP_P0_L100_GLL0"][i,lev_index2[0],:,:]-273.15
      T700 = T7001[lat_box1:lat_box2,lon_box1:lon_box2]
      del(T7001)

      RH7001 = forecast.variables["RH_P0_L100_GLL0"][i,lev_index2[0],:,:]
      RH700 = RH7001[lat_box1:lat_box2,lon_box1:lon_box2]
      del(RH7001)

      T5001 = forecast.variables["TMP_P0_L100_GLL0"][i,lev_index2[4],:,:]-273.15
      T500 = T5001[lat_box1:lat_box2,lon_box1:lon_box2]
      del(T5001)

      PWAT1 = forecast.variables["PWAT_P0_L200_GLL0"][i,:,:]
      PWAT = PWAT1[lat_box1:lat_box2,lon_box1:lon_box2]
      del PWAT1   

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

   # calculate shear and KI

   Td850 = T850 - ((100.0-RH850)/5.0)
   Td700 = T700 - ((100.0-RH700)/5.0)
   KI = (T850-T500)+Td850-(T700-Td700)

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

   imagename = "GFSforecast_%s_%s_KI_PWAT_maxshear_SNGL_%s_%03d" % (region, valid_date, init_dt[0:10], fore[i])

   wks_type = "png"
   wks_res = ngl.Resources()
   wks_res.wkBackgroundOpacityF = 0.0
   wks = ngl.open_wks(wks_type, imagename, wks_res)

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
   res.lbTitleString         = "K Index"
   res.lbTitleFontHeightF   = 0.0125

   res.sfXArray = lon2d
   res.sfYArray = lat2d

   res.pmTickMarkDisplayMode = "Never"
#   res.mpPerimOn   =  False
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

   res.cnLevelSelectionMode = "ManualLevels"
   res.cnMinLevelValF       = 15.0
   res.cnMaxLevelValF       = 45.0
   res.cnLevelSpacingF      = 1.5

   res.cnFillColors = [-1, 6, 17, 28, 39, 50, 61, 72, 83, 94, 105, 116, 127, 138, 149, 160, 171, 182, 193, 204, 215, 226]

# create KI plots for forecast times

   KI_plot = ngl.contour_map(wks,KI,res)

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
   
   res.cnMonoLineColor           = True
   res.cnFillOn                   = False
   res.cnLineLabelBackgroundColor = -1
   res.cnLineLabelDensityF        = 0.8
   res.cnLineLabelFontColor       = "Red"
   res.cnLineColor                = "Red"
   res.cnLineLabelFontHeightF     = 0.01
   res.cnLineLabelPerimOn         = False
   res.cnLineLabelsOn             = True
   res.cnLineLabelInterval        = 1
   res.cnLinesOn                  = True
   res.cnMonoLineLabelFontColor   = True
   res.lbLabelFontHeightF         = 0.0075
   res.cnLineThicknessF           = 2.5
   res.cnInfoLabelOn              = True
   res.cnInfoLabelString          = "PWAT Contours at 15, 30, 45 and 60 mm"
   res.cnInfoLabelOrthogonalPosF  = -0.06
   res.cnInfoLabelParallelPosF    = 0.505
   res.cnLineLabelPlacementMode = "constant"

   res.cnLevelSelectionMode = "ManualLevels"
   res.cnMinLevelValF       = 15.0
   res.cnMaxLevelValF       = 60.0
   res.cnLevelSpacingF      = 15.0
   res.cnLineThicknessF     = 2.5

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

# plot PWAT and overlay on colour contours

   PWAT_plot = ngl.contour(wks,PWAT,res)

   ngl.overlay(KI_plot,uv_plot1)
   ngl.overlay(KI_plot,PWAT_plot)

   ngl.maximize_plot(wks, KI_plot)
   ngl.draw(KI_plot)
   ngl.frame(wks)

   ngl.destroy(wks)
   del res
   del T850
   del Td850
   del RH850
   del T700
   del Td700
   del RH700
   del T500
   del KI
   del PWAT
   del vcres
   del u1
   del v1
   del u2
   del v2
   del shear
   del max_shear
   del max_shear_u2_u1
   del max_shear_v2_v1


os.system('mogrify -trim *_'+region+'_'+init_dt[0:10]+'_KI_PWAT_maxshear_SNGL.png')
if region == "WA" or region == "unknownWA":
   os.system('mogrify -resize 886x600 *_'+region+'_'+init_dt[0:10]+'_KI_PWAT_maxshear_SNGL.png')
elif region == "EA" or region == "unknownEA":
   os.system('mogrify -resize 600x733 *_'+region+'_'+init_dt[0:10]+'_KI_PWAT_maxshear_SNGL.png')

os.system('mv *_'+region+'_'+init_dt[0:10]+'_KI_PWAT_maxshear_SNGL.png MARTIN/GFS/'+region+'/'+init_dt[0:10]+'/KI_PWAT_maxshear')

os.system('mogrify -trim *'+region+'_*KI_PWAT_maxshear_SNGL_'+init_dt[0:10]+'*.png')
if region == "WA" or region == "unknownWA":
   os.system('mogrify -resize 886x600 *'+region+'_*KI_PWAT_maxshear_SNGL_'+init_dt[0:10]+'*.png')
elif region == "EA" or region == "unknownEA":
   os.system('mogrify -resize 600x733 *'+region+'_*KI_PWAT_maxshear_SNGL_'+init_dt[0:10]+'*.png')

os.system('mv *'+region+'_*KI_PWAT_maxshear_SNGL_'+init_dt[0:10]+'*.png MARTIN/GFS/'+region+'/'+init_dt[0:10]+'/KI_PWAT_maxshear')
