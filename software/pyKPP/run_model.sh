#!/bin/bash
cd $2
source setcase
cd $2/CO_iso/$1
echo $PWD
kpp strato_CO.kpp

make -f Makefile_strato_CO

rm *.mod
rm *.o
rm *.f90

./strato_CO.exe
rm *.exe
rm Makefile_strato_CO
rm atoms_iso
rm jval.nc
