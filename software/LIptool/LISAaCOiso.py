#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 16:35:59 2019

@author: joram
"""

from io import StringIO
import os
import pandas as pd
from glob import glob
from LIptool import *
import numpy as np
co_stable_isotope_unit = '''
IRMS date       ,Analysis date of the stable isotope measurements (CO IRMS d13C(CO) d18O(CO)), UTC+2
CO IRMS         ,CO mole fraction from the IRMS  ,nano mol per mol
d13C(CO)        ,13C content expressed vs vpdb    ,per mil
d13C(CO) un     ,uncertainty in 13C content epressed vs vpdb, per mil
d18O(CO)        ,18O content expressed vs vsmow    ,per mil
d18O(CO) un     ,uncertainty 18O content expressed vs vsmow,per mil
'''
co_stable_isotopes_fields = ['IRMS date', 'CO IRMS',
                             'd13C(CO)', 'd13C(CO) un', 'd18O(CO)', 'd18O(CO) un']

co_stable_isotopes_header = '''
Info stable isotope analysis. Stable isotope ratio's obtained using cf-irms measurements 
End info stable isotope analysis
'''
master_file = glob('Processed/*LISA_flight.csv')[0]
source_file = os.getcwd()
while os.path.isdir(source_file) == True:

    source_file += select_file(source_file).replace(source_file, '')

data_append = pd.read_csv(source_file)

# assign uncertainies as determined by Elena Popa
data_append.loc[np.isfinite(data_append['13C']),'13C std']=0.5
data_append.loc[np.isfinite(data_append['18O']),'18O std']=0.5

unit_str, header, data_original = LoadLisa(master_file)

print()
print('Loaded the master file')
print()

unit_str = append_unit(unit_str, co_stable_isotope_unit)
header = append_header(header, co_stable_isotopes_header)
print(data_append)
print()
print(data_original['p'])
print()

# fix rows
correct_order = input('is the order in the appended data correct [y/n]?\n')
emptyframe = pd.DataFrame(index=range(
    len(data_original)), columns=data_append.keys())
if correct_order != 'y':
    for i in range(len(data_append)):
        print(data_append.iloc[i])
        print()
        print("to which sample does the data above belong?")
        for p, ii in zip(data_original['p'], range(0, len(data_original['p']))):
            print()
            print(ii, p)
        row = int(input('number '))
        emptyframe.iloc[row] = data_append.iloc[i]
else:
    print("this is not implemented yet. Pleas return to select samples. Wil now exit")
    exit()
    pass
data_append = emptyframe
for orkey in co_stable_isotopes_fields:
    print('Give the field code for '+orkey)
    print()
    for key, ii in zip(data_append.keys(), range(0, len(data_append.keys()))):
        print(ii, key)
    print()
    ii = int(input('number'))
    data_original[orkey] = data_append[data_append.keys()[ii]]

date = data_original['Date'][0]
with open('Processed/{}_LISA_flight.csv'.format(date).replace('-', ''), 'w') as result:
    result.write(unit_str)
    result.write(header)
    data_original.to_csv(result, index=False)
    result.close()
