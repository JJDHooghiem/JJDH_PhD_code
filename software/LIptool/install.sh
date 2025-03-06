#!/bin/sh
bin="$HOME/.local/bin"
rm $bin/lisaproc
ln LISAproc.py $bin/lisaproc 
rm $bin/lisaco
ln LISAaCOiso.py $bin/lisaco 
rm $bin/lisan2o
ln LISAaN2O.py $bin/lisan2o
rm $bin/lisarep
ln LISAreport.py $bin/lisarep
