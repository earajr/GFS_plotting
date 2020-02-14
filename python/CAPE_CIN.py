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

# Main script to plot CAPE and CIN

# define directory

diri = (os.getcwd())+"/"

# forecast times (set in namelist file)

fore = (os.popen("cat %s/controls/namelist | grep 'fore:' | awk -F: '{print $2}' | tr ',' ' '"%(GFS_dir))).read().split()
fore = [np.int(f) for f in fore]

#fore = np.arange(3,73,3)

# accept initialisation time and dates as an argument

init_dt = (sys.argv[1])

# read in domains and accept lat and lon limits as arguments

b = open(GFS_dir+"/controls/domains")
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
      
# read in CAPE and CIN, checking whether box crosses Greenwich Meridian.

if (np.sign(lonbl) + np.sign(lontr)) >= -1 and (np.sign(lonbl) + np.sign(lontr)) <= 1:

   CAPE1 = analysis.variables["CAPE_P0_L1_GLL0"][:,:]
   CAPE_temp1 = CAPE1[lat_box1:lat_box2,0:lon_box1]
   CAPE_temp2 = CAPE1[lat_box1:lat_box2,lon_box2:lon_box3]
   CAPE = np.concatenate((CAPE_temp2,CAPE_temp1),axis=1)
   del CAPE1
   del CAPE_temp1
   del CAPE_temp2

   CIN1 = analysis.variables["CIN_P0_L1_GLL0"][:,:]
   CIN_temp1 = CIN1[lat_box1:lat_box2,0:lon_box1]
   CIN_temp2 = CIN1[lat_box1:lat_box2,lon_box2:lon_box3]
   CIN = np.concatenate((CIN_temp2,CIN_temp1),axis=1)
   CIN = smth9(CIN, 0.5, 0.25)
   del CIN1
   del CIN_temp1
   del CIN_temp2

else:
   CAPE1 = analysis.variables["CAPE_P0_L1_GLL0"][:,:]
   CAPE = CAPE1[lat_box1:lat_box2,lon_box1:lon_box2]
   del(CAPE1)

   CIN1 = analysis.variables["CIN_P0_L1_GLL0"][:,:]
   CIN = CIN1[lat_box1:lat_box2,lon_box1:lon_box2]
   CIN = smth9(CIN, 0.5, 0.25)
   del(CIN1)

# create 2d lat and lon

lat2d = np.zeros((len(lat),len(lon)))
lon2d = np.zeros((len(lat),len(lon)))

for i in range(0, len(lon)):
   lat2d[:,i] = lat

for i in range(0, len(lat)):
   lon2d[i,:] = lon
   
# open workspace for analysis plot

imagename = "GFSanalysis_%s_%s_CAPECIN_SNGL" % (region, init_dt[0:10])

wks_type = "png"
wks_res = ngl.Resources()
wks_res.wkBackgroundOpacityF = 0.0
wks = ngl.open_wks(wks_type, imagename, wks_res)

# define resources for analysis plot

res = ngl.Resources()
res.nglDraw  = False
res.nglFrame = False

#res.tmXBOn             = False
#res.tmXTOn             = False
#res.tmYLOn             = False
#res.tmYROn             = False

res.vpWidthF  = 0.9
res.vpHeightF = 0.6

cmap = ngl.read_colormap_file("WhiteBlueGreenYellowRed")
#res.tiXAxisString = "longitude"
#res.tiXAxisFontHeightF = 0.015
#res.tiYAxisString = "latitude"
#res.tiYAxisFontHeightF = 0.015

res.mpGridAndLimbOn        = False

#res.tiMainString               = "CAPE and CIN analysis %s" % (init_dt[0:10])
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
res.lbTitleString         = "CAPE"
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

res.cnLevelSelectionMode = "ExplicitLevels"
res.cnLevels = [25.0, 75.0, 125.0, 250.0, 500.0, 750.0, 1000.0, 1250.0, 1500.0, 1750.0, 2000.0, 2250.0, 2500.0, 2750.0, 3000.0, 3250.0, 3500.0, 3750.0, 4000.0, 4500.0, 5000.0, 5500.0]
res.cnFillColors = [-1, 6, 17, 28, 39, 50, 61, 72, 83, 94, 105, 116, 127, 138, 149, 160, 171, 182, 193, 204, 215, 226, 237]

# create CAPE and CIN plot for analysis data

CAPE_plot = ngl.contour_map(wks,CAPE,res)

del res.mpProjection
del res.mpLimitMode
del res.mpMinLonF
del res.mpMaxLonF
del res.mpMinLatF
del res.mpMaxLatF
#del res.mpPerimOn
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
res.cnLinesOn                  = True
res.cnMonoLineLabelFontColor   = True
res.lbLabelFontHeightF         = 0.0075
res.cnLineThicknessF           = 2.5
res.cnInfoLabelOn              = True
res.cnInfoLabelString          = "CIN Contours at -50, -100 and -250 J/Kg"
res.cnInfoLabelOrthogonalPosF  = -0.06
res.cnInfoLabelParallelPosF    = 0.505
 
res.cnLevelSelectionMode = "ExplicitLevels"
res.cnLevels = [-250.0, -100.0, -50.0]

# plot CIN and overlay on colour contours

CIN_plot = ngl.contour(wks,CIN,res)

ngl.overlay(CAPE_plot,CIN_plot)

ngl.maximize_plot(wks, CAPE_plot)
ngl.draw(CAPE_plot)
ngl.frame(wks)

ngl.destroy(wks)
del res
del CAPE
del CIN

###################################################################################################

# open forecast file

f_fili = "GFS_forecast_%s_%s.nc" % (init_dt[:8], init_dt[8:10])
forecast = nio.open_file(diri+f_fili)

# loop through forecast times

for i in range(0, len(fore)):

# create valid date and time string

   valid_date = (datetime.datetime(int(init_dt[:4]), int(init_dt[4:6]), int(init_dt[6:8]), int(init_dt[8:10])) + datetime.timedelta(hours=int(fore[i]))).strftime("%Y%m%d%H")

# read in CAPE and CIN, checking whether box crosses Greenwich Meridian.

   if (np.sign(lonbl) + np.sign(lontr)) >= -1 and (np.sign(lonbl) + np.sign(lontr)) <= 1:

      CAPE1 = forecast.variables["CAPE_P0_L1_GLL0"][i,:,:]
      CAPE_temp1 = CAPE1[lat_box1:lat_box2,0:lon_box1]
      CAPE_temp2 = CAPE1[lat_box1:lat_box2,lon_box2:lon_box3]
      CAPE = np.concatenate((CAPE_temp2,CAPE_temp1),axis=1)
      del CAPE1
      del CAPE_temp1
      del CAPE_temp2

      CIN1 = forecast.variables["CIN_P0_L1_GLL0"][i,:,:]
      CIN_temp1 = CIN1[lat_box1:lat_box2,0:lon_box1]
      CIN_temp2 = CIN1[lat_box1:lat_box2,lon_box2:lon_box3]
      CIN = np.concatenate((CIN_temp2,CIN_temp1),axis=1)
      CIN = smth9(CIN, 0.5, 0.25)
      del CIN1
      del CIN_temp1
      del CIN_temp2

   else:

      CAPE1 = forecast.variables["CAPE_P0_L1_GLL0"][i,:,:]
      CAPE = CAPE1[lat_box1:lat_box2,lon_box1:lon_box2]
      del(CAPE1)

      CIN1 = forecast.variables["CIN_P0_L1_GLL0"][i,:,:]
      CIN = CIN1[lat_box1:lat_box2,lon_box1:lon_box2]
      CIN = smth9(CIN, 0.5, 0.25)
      del(CIN1)

# open workspace for forecast plots

   imagename = "GFSforecast_%s_%s_CAPECIN_SNGL_%s_%03d" % (region, valid_date, init_dt[0:10], fore[i])

   wks_type = "png"
   wks_res = ngl.Resources()
   wks_res.wkBackgroundOpacityF = 0.0
   wks = ngl.open_wks(wks_type, imagename, wks_res)

# define resources for forecast plots

   res = ngl.Resources()
   res.nglDraw  = False
   res.nglFrame = False

#   res.tmXBOn             = False
#   res.tmXTOn             = False
#   res.tmYLOn             = False
#   res.tmYROn             = False
  
   res.vpWidthF  = 0.9
   res.vpHeightF = 0.6

   cmap = ngl.read_colormap_file("WhiteBlueGreenYellowRed")
#   res.tiXAxisString = "longitude"
#   res.tiXAxisFontHeightF = 0.015
#   res.tiYAxisString = "latitude"
#   res.tiYAxisFontHeightF = 0.015

   res.mpGridAndLimbOn        = False

#   res.tiMainString               = "CAPE and CIN forecast %s +%03d" % (init_dt[0:10], fore[i])
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
   res.lbTitleString         = "CAPE"
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

   res.cnLevelSelectionMode = "ExplicitLevels"
   res.cnLevels = [25.0, 75.0, 125.0, 250.0, 500.0, 750.0, 1000.0, 1250.0, 1500.0, 1750.0, 2000.0, 2250.0, 2500.0, 2750.0, 3000.0, 3250.0, 3500.0, 3750.0, 4000.0, 4500.0, 5000.0, 5500.0]
   res.cnFillColors = [-1, 6, 17, 28, 39, 50, 61, 72, 83, 94, 105, 116, 127, 138, 149, 160, 171, 182, 193, 204, 215, 226, 237]


# create CAPE plots for forecast times

   CAPE_plot = ngl.contour_map(wks,CAPE,res)

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
   
   res.cnFillOn                   = False
   res.cnLineLabelBackgroundColor = -1
   res.cnLineLabelDensityF        = 0.8
   res.cnLineLabelFontColor       = "Red"
   res.cnLineColor                = "Red"
   res.cnLineLabelFontHeightF     = 0.01
   res.cnLineLabelPerimOn         = False
   res.cnLineLabelsOn             = True
   res.cnLinesOn                  = True
   res.cnMonoLineLabelFontColor   = True
   res.lbLabelFontHeightF         = 0.0075
   res.cnLineThicknessF           = 2.5
   res.cnInfoLabelOn              = True
   res.cnInfoLabelString          = "CIN Contours at -50, -100 and -250 J/Kg"
   res.cnInfoLabelOrthogonalPosF  = -0.06
   res.cnInfoLabelParallelPosF    = 0.505


   res.cnLevelSelectionMode = "ExplicitLevels"
   res.cnLevels = [-250.0, -100.0, -50.0]

# plot ITD and overlay on colour contours

   CIN_plot = ngl.contour(wks,CIN,res)

   ngl.overlay(CAPE_plot,CIN_plot)

   ngl.maximize_plot(wks, CAPE_plot)
   ngl.draw(CAPE_plot)
   ngl.frame(wks)
    
   ngl.destroy(wks)
   del res
   del CAPE
   del CIN

os.system('mogrify -trim *_'+region+'_'+init_dt[0:10]+'_CAPECIN_SNGL.png')
if region == "WA" or region == "unknownWA":
   os.system('mogrify -resize 886x600 *_'+region+'_'+init_dt[0:10]+'_CAPECIN_SNGL.png')
elif region == "EA" or region == "unknownEA":
   os.system('mogrify -resize 600x733 *_'+region+'_'+init_dt[0:10]+'_CAPECIN_SNGL.png')

os.system('mv *_'+region+'_'+init_dt[0:10]+'_CAPECIN_SNGL.png %s/MARTIN/GFS/'%(GFS_dir)+region+'/'+init_dt[0:10]+'/CAPE_CIN')

os.system('mogrify -trim *'+region+'_*CAPECIN_SNGL_'+init_dt[0:10]+'*.png')
if region == "WA" or region == "unknownWA":
   os.system('mogrify -resize 886x600 *'+region+'_*CAPECIN_SNGL_'+init_dt[0:10]+'*.png')
elif region == "EA" or region == "unknownEA":
   os.system('mogrify -resize 600x733 *'+region+'_*CAPECIN_SNGL_'+init_dt[0:10]+'*.png')

os.system('mv *'+region+'_*CAPECIN_SNGL_'+init_dt[0:10]+'*.png %s/MARTIN/GFS/'%(GFS_dir)+region+'/'+init_dt[0:10]+'/CAPE_CIN')


