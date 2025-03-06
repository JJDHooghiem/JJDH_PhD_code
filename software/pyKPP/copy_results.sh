#!/bin/bash
mv $2/models/$1/* $2/CO_iso/$1/
rmdir $2/models/$1
cp -r $2/CO_iso/$1 $3/$1
rm -r $2/CO_iso/$1
