###################################################################################################
# Project           : Global Challenges Research Fund (GCRF) African SWIFT (Science for Weather
#                     Information and Forecasting Techniques.
#
# Program name      : lat_lon.py 
#
# Author            : Alexander J. Roberts, University of Leeds, NCAS
# 
# Date created      : Jan 2019
#
# Purpose           : Plot lat lon grid lines for region as part of SWIFT_GFSplotting.
#
# Revision History  :
#
# Usage             : Can be used as part of wider plotting repository or independently e.g.
#                     "python3 lat_lon.py lat lon lat lon"
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
# Main script

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

colours = ["black", "white"]

for colour in colours:

   imagename = "grid_"+colour+'_'+region

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

   res.mpGridAndLimbOn        = True

   res.pmTickMarkDisplayMode = "Never"
   res.mpProjection              = "CylindricalEquidistant"
   res.mpLimitMode = "LatLon"    # Limit the map view.
   res.mpMinLonF   = lontr
   res.mpMaxLonF   = lonbl
   res.mpMinLatF   = lattr
   res.mpMaxLatF   = latbl
   res.mpOutlineBoundarySets     = "AllBoundaries"
   res.mpNationalLineColor       = -1
   res.mpNationalLineThicknessF  = 2.0
   res.mpGeophysicalLineColor    = -1
   res.mpGeophysicalLineThicknessF = 2.0
   res.mpGridLatSpacingF = 5.0
   res.mpGridLonSpacingF = 5.0
   res.mpGridLineThicknessF = 2.0
   res.mpGridLineColor             = colour
   res.cnMonoLineColor           = True

   grid_plot = ngl.map(wks,res)

   ngl.maximize_plot(wks, grid_plot)
   ngl.draw(grid_plot)
   ngl.frame(wks)

   ngl.destroy(wks)
   del res

   if region == "WA" or region == "unknownWA":
      os.system('mogrify -trim grid_'+colour+'_'+region+'.png')
      os.system('mogrify -resize 886x600 grid_'+colour+'_'+region+'.png')
   elif region == "EA" or region == "unknownEA":
      os.system('mogrify -trim grid_'+colour+'_'+region+'.png')
      os.system('mogrify -resize 600x733 grid_'+colour+'_'+region+'.png')


