#!/bin/sh
date=$1
datadir="/home/joram/research/data/ECMWF_CAMS/"
ncsurff="$1_cams_eac4_surf.nc"
ncsurfdmf="$1_cams_eac4_surf-dm.nc"
nchybf="$1_cams_eac4_hyb.nc"
nchybdmf="$1_cams_eac4_hyb-dm.nc"
# cdo merge $datadir$ncsurff $ncsurff $datadir$ncsurff
# cdo merge $datadir$ncsurfdmf $ncsurfdmf $datadir$ncsurfdmf 
mv $nchybf "$nchybf-back"
cdo merge $datadir$nchybf "$nchybf-back" $nchybf 
mv $nchybdmf "$nchybdmf-back"
cdo merge $datadir$nchybdmf  "$nchybdmf-back" $nchybdmf 
