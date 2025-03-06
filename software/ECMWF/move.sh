#!/bin/sh
date=$1
datadir="/home/joram/research/data/ECMWF_CAMS/"
nchybf="$1_cams_eac4_hyb.nc"
nchybdmf="$1_cams_eac4_hyb-dm.nc"
mv $nchybf $datadir$nchybf

mv $nchybdmf $datadir$nchybdmf
