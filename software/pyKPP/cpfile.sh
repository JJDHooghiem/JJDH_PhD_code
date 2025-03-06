#!/bin/bash
cd /Users/joram/scripts/Modelling/kpp/CO_iso

mkdir $1
mkdir ../models/$1
cp ../models/$2.def ../models/$1/strato_CO_base.def
cp ../models/$2.eqn ../models/$1/strato_CO_base.eqn
cp ../models/$2.spc ../models/$1/strato_CO_base.spc
cp $3.kpp $1/strato_CO.kpp
cp ../models/atoms_iso $1/atoms_iso
cp jval.nc $1/jval.nc
