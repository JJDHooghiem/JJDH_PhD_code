#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  2 14:03:44 2018

@author: joram
"""
import json
import os
import sys
import time
from calendar import timegm
from glob import glob
from shutil import copy2

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas.plotting import register_matplotlib_converters
from scipy.interpolate import interp1d
from scipy.optimize import curve_fit

from LIptool import *

matplotlib.use('Qt5Agg')
matplotlib.rc('text', usetex=False)
register_matplotlib_converters()
# LISA folder to process
# LISA_folder=sys.argv[1]
LISA_folder = os.getcwd()
print()
print(LISA_folder)
print()
LISA_config = LISA_folder+'/LISA_config.py'
if os.path.exists('Processed') == False:
    os.mkdir('Processed')
if os.path.exists('Figures') == False:
    os.mkdir('Figures')
# Constants
# os.chdir(LISA_folder)
# Create a symlink before importing Libraries that share global variables
# Configparser should be used here
srcdir = '/home/joram/.local/src/python/LIptool'
copy2(LISA_config, srcdir)
#
# os.chdir(srcdir)
clear_pyc()

# os.chdir(LISA_folder)
# Define directories
picarro_dir = 'Picarro/'
radiosonde_dir = 'Radiosonde/'
datalogger_dir = 'Datalogger/'


#
picarro_files = glob(picarro_dir+'*.dat')
print()
print('Found picarro files: ', picarro_files)
print()
datalogger_file = glob(datalogger_dir+'*.csv')
if len(datalogger_file) == 1:
    datalogger_file = datalogger_file[0]
    print()
    print('Found datalogger file: ', datalogger_file)
    print()
else:
    print()
    print('Im just guessing')
    print()
radiosonde_file = glob(radiosonde_dir+'*.tsv')
if len(radiosonde_file) == 1:
    radiosonde_file = radiosonde_file[0]
    print()
    print('Found radiosonde file: ', radiosonde_file)
    print()
else:
    print()
    print('Im just guessing')
    print()
print()
print("Processing met data")
print()

Radiosonde, Datalogger, sample_info, LISAdata, figw, ofsets = process_met_data(
    datalogger_file, radiosonde_file)

os.chdir('Processed')
with open('pressure_ofset.json', 'w+') as inter:
    json.dump(ofsets, inter)
    inter.close()

os.chdir('..')

os.chdir('Figures')
figw.savefig('pmodel.pdf', format='pdf')
plt.close()
os.chdir('..')
print()
print("Processing picarro data")
print()
data = get_Picarro(picarro_files)
print()
print()
# Calibration time stamps
print()
print('First check if  file is present')
print()

# samplenames=[Datalogger["P1"][0],Datalogger["P2"][0],Datalogger["P3"][0],Datalogger["P4"][0]]
#samplenames=[str(i) for i in samplenames]
print(samplenames)

f = glob('Processed/*.json')
if 'Processed/recal_file.json' not in f:

    cal_list = []
    more_calibration = 'y'
    while more_calibration == 'y':
        cal_list.extend(select_data(
            data['index'], data['CO2_cor'], 'for calibration'))
        more_calibration = str(input(
            'Do you want to select another calibration interval, I will interpolate based on time if more intervals are selected [y/n]?'))
        print(more_calibration)

    pic_samples = select_samples(LISAdata, data, samplenames)
    pic_samples['Cal'] = cal_list
    with open('Processed/recal_file.json', 'w+') as inter:
        json.dump(pic_samples, inter)
        inter.close()
else:
    with open('Processed/recal_file.json', 'r') as inter:
        pic_samples = json.load(inter)

fcal = calibration(data, pic_samples['Cal'])
os.chdir('Figures')

fcal.savefig('Calibration.pdf', format='pdf')

plt.close()
os.chdir('..')
ALL_data = calc_samples(LISAdata, data, pic_samples, samplenames)

data_save = ALL_data
print('CO2 data')
print(data_save[['CO2', 'CO2 un']])
print('CH4 data')
print(data_save[['CH4', 'CH4 un']])
print('CO data')
print(data_save[['CO', 'CO un']])

print()

more_calc = str(input('Do you want to recalculate a specific species [y/n]?'))
print()
if more_calc == 'y':
    print(data.columns.values)
    key = str(input('Provide me with key from list:\n CO2, CH4, or CO\n'))

    if 'Processed/recal_file_{}.json'.format(key) not in f:
        pic_samples2 = select_samples(LISAdata, data, key+'_cal')
    else:
        with open('Processed/recal_file_{}.json'.format(key), 'r') as inter:
            pic_samples2 = json.load(inter)
    data_spec = calc_samples(LISAdata, data, pic_samples2, samplenames)
    print('CO2 data')
    print(data_spec[['CO2', 'CO2 un']])
    print('CH4 data')
    print(data_spec[['CH4', 'CH4 un']])
    print('CO data')
    print(data_spec[['CO', 'CO un']])
#    key=str(input('which species to overwrite?\n'))
    data_save[key].iloc[:] = data_spec[key]

    data_save[key+' un'].iloc[:] = data_spec[key+' un']
    with open('Processed/recal_file_{}.json'.format(key), 'w') as inter:
        json.dump(pic_samples2, inter)
    add_info = 'For '+key+'a different selection was made. Because '
    reason = str(input('Why is the selection different? Because ... \n'))
    add_info += reason+'\n'

    samplel_intervals = []
    for key1 in pic_samples2:
        if key1 != 'Cal':
            samplel_intervals.extend(pic_samples2[key1])
    add_info += 'Additional sample index {0} {1}\n'.format(
        key, samplel_intervals)

    os.chdir('Figures')
    plot_picarro_data(data, pic_samples2, fname='Recalc_' +
                      key, title='Recalculation for '+key)
    os.chdir('..')
else:
    add_info = ''
    pass
# Create figures:
os.chdir('Figures')
plot_picarro_species(data)
plot_picarro_data(data, pic_samples)
for iterkey in Datalogger.keys():
    if iterkey != 'Date':
        plt.close()
        plt.plot(Datalogger[iterkey])
        plt.xlabel('Time')
        plt.ylabel(iterkey)
        plt.savefig('Datalogger_'+iterkey+'.pdf',
                    format='pdf', bbox_inches='tight')
        plt.close()

for key in Radiosonde.keys():
    if Radiosonde[key].isnull().all() != True:
        plt.close()
        plt.plot(Radiosonde[key])
        plt.xlabel('Time')
        plt.ylabel(key)
        plt.savefig('Radiosonde_'+key+'.pdf',
                    format='pdf', bbox_inches='tight')
        plt.close()
os.chdir('..')
# print(data.columns.values()
date = data_save['Date'][0]

cal = cal_string(data, pic_samples, add_info)
with open('Processed/{}_LISA_flight.csv'.format(date.replace('-', '')), 'w') as result:
    result.write(sample_info+'\n'+unit_str)
    result.write(cal)
    result.write('End of header information\n')
    data_save.to_csv(result, index=False)
    result.close()
Datalogger.to_csv(
    'Processed/{}_LISA_metdata.csv'.format(date.replace('-', '')))

quit()
