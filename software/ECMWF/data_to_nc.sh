#!/bin/sh
date=$1
gribf="$1_cams_eac4.grb"
gribsurf=$1_cams_eac4_surface.grb
gribhyb=$1_cams_eac4_hybrid.grb
ncsurff="$1_cams_eac4_surf.nc"
ncsurfdmf="$1_cams_eac4_surf-dm.nc"
nchybf="$1_cams_eac4_hyb.nc"
nchybdmf="$1_cams_eac4_hyb-dm.nc"
gribtarget=$1_cams_eac4_[typeOfLevel].grb

# split model levles
grib_copy $gribf $gribtarget
grib_to_netcdf $gribsurf -o $ncsurff
grib_to_netcdf $gribhyb -o $nchybf 
rm $gribhyb $gribsurf
# sleep 1
cdo -daymean $ncsurff $ncsurfdmf 
cdo -daymean $nchybf $nchybdmf 

