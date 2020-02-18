###################################################################################################
# Project           : Global Challenges Research Fund (GCRF) African SWIFT (Science for Weather
#                     Information and Forecasting Techniques.
#
# Program name      : pv.py 
#
# Author            : Alexander J. Roberts, University of Leeds, NCAS
# 
# Date created      : Jan 2019
#
# Purpose           : Plot PV images as part of SWIFT_GFSplotting.
#
# Revision History  :
#
# Usage             : Can be used as part of wider plotting repository or independently e.g.
#                     "python3 pv.py time lev lat lon lat lon"
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
from windspharm.standard import VectorWind

GFS_dir = os.environ['SWIFT_GFS']

###################################################################################################
def pv_calc(u, v, t, p, avort, lat, lon):

   ranku = np.ndim(u)

   if ranku != 3:
      print("StaticStabilityP: only 3D arrays allowed: rank="+ranku)
      exit
  
   rankv  = np.ndim(v)
   rankt  = np.ndim(t)
  
   if ranku != rankv or ranku != rankt:
      print("PotVortIsobaric: u, v, t must be the same rank: ranku=" +ranku+"  rankv="+rankv+"  rankt="+rankt)
      exit

   theta = t*(100000.0/p)**0.286

   dthdp = (np.gradient(theta))[0]/(np.gradient(p))[0]

   G = 9.80665
   pv = -G*(avort)*dthdp*10**5

   return( pv[1,:,:] )

###################################################################################################

# Main script to plot PV

# define directory

diri = (os.getcwd())+"/"

# forecast times (currently set to plot 0 to 48 hours)

fore = (os.popen("cat %s/controls/namelist | grep 'fore:' | awk -F: '{print $2}' | tr ',' ' '"%(GFS_dir))).read().split()
fore = [np.int(f) for f in fore]

# accept initialisation time and level as arguments

init_dt = (sys.argv[1])
lev_hPa = (sys.argv[2])

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

lev_index = levs_p.index(lev_hPa)

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

lev_index_low = lev_index-1
lev_index_hi = lev_index+1

if (np.sign(lonbl) + np.sign(lontr)) >= -1 and (np.sign(lonbl) + np.sign(lontr)) <= 1:

   u1 = analysis.variables["UGRD_P0_L100_GLL0"][lev_index_low:lev_index_hi+1,:,:]
   u_temp1 = u1[:,lat_box1:lat_box2,0:lon_box1]
   u_temp2 = u1[:,lat_box1:lat_box2,lon_box2:lon_box3]
   u = np.concatenate((u_temp2,u_temp1),axis=2)
   del u1
   del u_temp1
   del u_temp2

   v1 = analysis.variables["VGRD_P0_L100_GLL0"][lev_index_low:lev_index_hi+1,:,:]
   v_temp1 = v1[:,lat_box1:lat_box2,0:lon_box1]
   v_temp2 = v1[:,lat_box1:lat_box2,lon_box2:lon_box3]
   v = np.concatenate((v_temp2,v_temp1),axis=2)
   del v1
   del v_temp1
   del v_temp2

   t1 = analysis.variables["TMP_P0_L100_GLL0"][lev_index_low:lev_index_hi+1,:,:]
   t_temp1 = t1[:,lat_box1:lat_box2,0:lon_box1]
   t_temp2 = t1[:,lat_box1:lat_box2,lon_box2:lon_box3]
   t = np.concatenate((t_temp2,t_temp1),axis=2)
   del t1
   del t_temp1
   del t_temp2

   avort1 = analysis.variables["ABSV_P0_L100_GLL0"][lev_index_low:lev_index_hi+1,:,:]
   avort_temp1 = avort1[:,lat_box1:lat_box2,0:lon_box1]
   avort_temp2 = avort1[:,lat_box1:lat_box2,lon_box2:lon_box3]
   avort = np.concatenate((avort_temp2,avort_temp1),axis=2)
   del avort1
   del avort_temp1
   del avort_temp2

else:

   u1 = analysis.variables["UGRD_P0_L100_GLL0"][lev_index_low:lev_index_hi+1,:,:]
   u = u1[:,lat_box1:lat_box2,lon_box1:lon_box2]
   del u1

   v1 = analysis.variables["VGRD_P0_L100_GLL0"][lev_index_low:lev_index_hi+1,:,:]
   v = v1[:,lat_box1:lat_box2,lon_box1:lon_box2]
   del v1

   t1 = analysis.variables["TMP_P0_L100_GLL0"][lev_index_low:lev_index_hi+1,:,:]
   t = t1[:,lat_box1:lat_box2,lon_box1:lon_box2]
   del t1

   avort1 = analysis.variables["ABSV_P0_L100_GLL0"][lev_index_low:lev_index_hi+1,:,:]
   avort = avort1[:,lat_box1:lat_box2,lon_box1:lon_box2]
   del avort1


p = np.full_like(u, float(lev_hPa)*100.0)
p[0,:,:] = float(levs_p[lev_index_low])*100.0
p[2,:,:] = float(levs_p[lev_index_hi])*100.0

pv = pv_calc(u,v,t,p,avort,lat,lon)

# create 2d lat and lon

lat2d = np.zeros((len(lat),len(lon)))
lon2d = np.zeros((len(lat),len(lon)))

for i in range(0, len(lon)):
   lat2d[:,i] = lat

for i in range(0, len(lat)):
   lon2d[i,:] = lon
   
# open workspace for analysis plot

wks_type = "png"
wks = ngl.open_wks(wks_type, "GFSanalysis_%s_%s_PV_%shPa" % (region, init_dt[0:10], lev_hPa))

# define resources for analysis plot

res = ngl.Resources()
res.nglDraw                     = False
res.nglFrame                    = False

cmap = ngl.read_colormap_file("MPL_RdBu")

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
res.lbTitleString         = "%shPa potential vorticity (PVU)" % (lev_hPa)
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

if float(lev_hPa) < 300.0:
   max_cont = 1.0
   min_cont = -1.0
if float(lev_hPa) >= 300.0 and float(lev_hPa) <700:
   max_cont = 0.25
   min_cont = -0.25
if float(lev_hPa) >=700:
   max_cont = 0.1
   min_cont = -0.1

res.cnLevelSelectionMode = "ManualLevels"
res.cnMinLevelValF       = min_cont
res.cnMaxLevelValF       = max_cont
res.cnLevelSpacingF      = (max_cont-min_cont)/20.0
res.cnLineThicknessF     = 2.5 

# create pv plot for analysis data

pv_plot = ngl.contour_map(wks,pv,res)

ngl.maximize_plot(wks, pv_plot)
ngl.draw(pv_plot)
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

# read in fields for pv calculation, checking whether box crosses Greenwich Meridian.

   if (np.sign(lonbl) + np.sign(lontr)) >= -1 and (np.sign(lonbl) + np.sign(lontr)) <= 1:

      lev_index_low = lev_index-1
      lev_index_hi = lev_index+1

      u1 = forecast.variables["UGRD_P0_L100_GLL0"][i,lev_index_low:lev_index_hi+1,:,:]
      u_temp1 = u1[:,lat_box1:lat_box2,0:lon_box1]
      u_temp2 = u1[:,lat_box1:lat_box2,lon_box2:lon_box3]
      u = np.concatenate((u_temp2,u_temp1),axis=2)
      del u1
      del u_temp1
      del u_temp2

      v1 = forecast.variables["VGRD_P0_L100_GLL0"][i,lev_index_low:lev_index_hi+1,:,:]
      v_temp1 = v1[:,lat_box1:lat_box2,0:lon_box1]
      v_temp2 = v1[:,lat_box1:lat_box2,lon_box2:lon_box3]
      v = np.concatenate((v_temp2,v_temp1),axis=2)
      del v1
      del v_temp1
      del v_temp2

      t1 = forecast.variables["TMP_P0_L100_GLL0"][i,lev_index_low:lev_index_hi+1,:,:]
      t_temp1 = t1[:,lat_box1:lat_box2,0:lon_box1]
      t_temp2 = t1[:,lat_box1:lat_box2,lon_box2:lon_box3]
      t = np.concatenate((t_temp2,t_temp1),axis=2)
      del t1
      del t_temp1
      del t_temp2

      avort1 = forecast.variables["ABSV_P0_L100_GLL0"][i,lev_index_low:lev_index_hi+1,:,:]
      avort_temp1 = avort1[:,lat_box1:lat_box2,0:lon_box1]
      avort_temp2 = avort1[:,lat_box1:lat_box2,lon_box2:lon_box3]
      avort = np.concatenate((avort_temp2,avort_temp1),axis=2)
      del avort1
      del avort_temp1
      del avort_temp2

   else:

      u1 = forecast.variables["UGRD_P0_L100_GLL0"][i,lev_index_low:lev_index_hi+1,:,:]
      u = u1[:,lat_box1:lat_box2,lon_box1:lon_box2]
      del u1

      v1 = forecast.variables["VGRD_P0_L100_GLL0"][i,lev_index_low:lev_index_hi+1,:,:]
      v = v1[:,lat_box1:lat_box2,lon_box1:lon_box2]
      del v1

      t1 = forecast.variables["TMP_P0_L100_GLL0"][i,lev_index_low:lev_index_hi+1,:,:]
      t = t1[:,lat_box1:lat_box2,lon_box1:lon_box2]
      del t1

      avort1 = forecast.variables["ABSV_P0_L100_GLL0"][i,lev_index_low:lev_index_hi+1,:,:]
      avort = avort1[:,lat_box1:lat_box2,lon_box1:lon_box2]
      del avort1


   p = np.full_like(u, float(lev_hPa)*100.0)
   p[0,:,:] = float(levs_p[lev_index_low])*100.0
   p[2,:,:] = float(levs_p[lev_index_hi])*100.0

   pv = pv_calc(u,v,t,p,avort,lat,lon)

# open workspace for forecast plots

   wks_type = "png"
   wks = ngl.open_wks(wks_type, "GFSforecast_%s_%s_PV_%shPa_%s_%03d" % (region, valid_date, lev_hPa, init_dt[0:10], fore[i]))

# define resources for forecast plots

   res = ngl.Resources()
   res.nglDraw                     = False
   res.nglFrame                    = False

   cmap = ngl.read_colormap_file("MPL_RdBu")

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
   res.lbTitleString         = "%shPa potential vorticity (PVU)" % (lev_hPa)
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

   if float(lev_hPa) < 300.0:
      max_cont = 1.0
      min_cont = -1.0
   if float(lev_hPa) >= 300.0 and float(lev_hPa) >700:
      max_cont = 0.25
      min_cont = -0.25
   if float(lev_hPa) >=700:
      max_cont = 0.1
      min_cont = -0.1

   res.cnLevelSelectionMode = "ManualLevels"
   res.cnMinLevelValF       = min_cont
   res.cnMaxLevelValF       = max_cont
   res.cnLevelSpacingF      = (max_cont-min_cont)/20.0
   res.cnLineThicknessF     = 2.5

# create ws plot for analysis data

   pv_plot = ngl.contour_map(wks,pv,res)

   ngl.maximize_plot(wks, pv_plot)
   ngl.draw(pv_plot)
   ngl.frame(wks)

   ngl.destroy(wks)
   del res

os.system('mogrify -trim *_'+region+'_'+init_dt[0:10]+'_PV_'+lev_hPa+'hPa.png')
#if region == "WA" or region == "unknownWA":
#   os.system('mogrify -resize 886x600 *_'+region+'_'+init_dt[0:10]+'_PV_'+lev_hPa+'hPa.png')
#elif region == "EA" or region == "unknownEA":
#   os.system('mogrify -resize 600x733 *_'+region+'_'+init_dt[0:10]+'_PV_'+lev_hPa+'hPa.png')

os.system('mv *_'+region+'_'+init_dt[0:10]+'_PV_'+lev_hPa+'hPa.png %s/MARTIN/GFS/'%(GFS_dir)+region+'/'+init_dt[0:10]+'/pv_'+lev_hPa)

os.system('mogrify -trim *'+region+'_*_PV_'+lev_hPa+'hPa_'+init_dt[0:10]+'*.png')
#if region == "WA" or region == "unknownWA":
#   os.system('mogrify -resize 886x600 *'+region+'_*_PV_'+lev_hPa+'hPa_'+init_dt[0:10]+'*.png')
#elif region == "EA" or region == "unknownEA":
#   os.system('mogrify -resize 600x733 *'+region+'_*_PV_'+lev_hPa+'hPa_'+init_dt[0:10]+'*.png')

os.system('mv *'+region+'_*_PV_'+lev_hPa+'hPa_'+init_dt[0:10]+'*.png %s/MARTIN/GFS/'%(GFS_dir)+region+'/'+init_dt[0:10]+'/pv_'+lev_hPa)

