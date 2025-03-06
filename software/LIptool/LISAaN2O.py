#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  2 14:03:44 2018

@author: joram
"""
import os
import pandas as pd
import numpy as np
from  calendar import timegm
import time
from scipy.interpolate import interp1d
from scipy.optimize import curve_fit
from glob import glob
import sys
from shutil import copy2
import matplotlib
matplotlib.use('Qt5Agg')
matplotlib.rc('text', usetex=False)
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
# LISA folder to process
import json
#LISA_folder=sys.argv[1]
LISA_folder=os.getcwd()
print()
print(LISA_folder)
print()
LISA_config=LISA_folder+'/LISA_config.py'
if os.path.exists('Figures')==False:
    os.mkdir('Figures')
# Constants
srcdir='/home/joram/.local/src/python/LIptool'
#os.chdir(LISA_folder)
## Create a symlink before importing Libraries that share global variables
srcdir='/home/joram/.local/src/python/LIptool'
copy2(LISA_config,srcdir)
#
from LIptool import *

clear_pyc()

# Define directories
picarro_dir='JKADS/'


co_stable_isotope_unit='''
N2O        N2O mole fraction    ppb 
N2O un     N2O mole fraction uncertainty   ppb 
CO JKADS    CO mole fraction from the JKADS ppb
CO JKADS    CO mole fraction uncertainty from the JKADS ppb
'''
co_stable_isotopes_fields=['N2O','N2O un','CO JKADS','CO un JKADS']

co_stable_isotopes_header='''
Info N2O analysis. N2O analysis performed on JKADS from lsce
End info N2O analysis 
'''

master_file=glob('Processed/*LISA_flight.csv')[0]
unit_str,header,data_original=LoadLisa(master_file)

unit_str=append_unit(unit_str,co_stable_isotope_unit)
header=append_header(header,co_stable_isotopes_header)

picarro_files=glob(picarro_dir+'*.dat')
print()
print('Found picarro files: ',picarro_files)
print()
#radiosonde_file=glob(radiosonde_dir+'*.tsv')

data=JKADS(picarro_files)
# Calibration time stamps 
print()
print('First check if  file is present')
print()
print(data)
f=glob('Processed/*.json')
if 'Processed/recal_fileN2O.json' not in f: 
    cal_list=[]
    more_calibration='y'
    while more_calibration=='y':
        cal_list.extend(select_data(data['index'], data['N2O_cor'],'for calibration'))
        more_calibration=str(input('Do you want to select another calibration interval, I will interpolate based on time if more intervals are selected [y/n]?'))
        print(more_calibration)
    pic_samples=select_samples(data_original,data,key='N2O_cor')
    pic_samples['Cal']=cal_list
    with open('Processed/recal_fileN2O.json','w') as inter:
        json.dump(pic_samples, inter)
else:
    with open('Processed/recal_fileN2O.json','r') as inter:
        pic_samples=json.load(inter)
fcal=JKADS_calibration(data,pic_samples['Cal'])
os.chdir('Figures')

fcal.savefig('CalibrationN2O.pdf',format='pdf')

plt.close()
os.chdir('..')
#
data_save=calc_n2o_samples(data_original,data,pic_samples,samplenames)
print('N2O data')
print(data_save[['N2O','N2O un']])
print('CO data')
print(data_save[[ 'CO','CO un']])
print('CO data JKADS')
print(data_save[[ 'CO JKADS','CO un JKADS']])

date=data_original['Date'][0]
with open('Processed/{}_LISA_flight.csv'.format(date).replace('-',''),'w') as result:
    result.write(unit_str)
    result.write(header)
    data_save.to_csv(result,index=False)
    result.close()                                                       
#
#print(
#
#more_calc=str(raw_input('Do you want to recalculate a specific species [y/n]?')) 
#print()
#if more_calc=='y':
#    print(data.columns.values
#    key=str(raw_input('Provide me with key from list:\n CO2, CH4, or CO\n')) 
#    
#    if 'Processed/recal_file_{}.json'.format(key) not in f: 
#        pic_samples2=select_samples(LISAdata,data,key+'_cal') 
#    else:
#        with open('Processed/recal_file_{}.json'.format(key),'r') as inter:
#            pic_samples2=json.load(inter)
#    data_spec=calc_samples(LISAdata,data,pic_samples2)
#    print('CO2 data'
#    print(data_spec[['CO2','CO2 un']]
#    print('CH4 data'
#    print(data_spec [[ 'CH4' ,'CH4 un']]
#    print('CO data'
#    print(data_spec[[ 'CO','CO un']]
##    key=str(raw_input('which species to overwrite?\n')) 
#    data_save[key].iloc[:]=data_spec[key]
#    
#    data_save[key+' un'].iloc[:]=data_spec[key+' un']
#    with open('Processed/recal_file_{}.json'.format(key),'w') as inter:
#        json.dump(pic_samples2, inter)
#    add_info='For '+key+'a different selection was made. Because '
#    reason=str(raw_input('Why is the selection different? Because ... \n'))
#    add_info+=reason+'\n'
#
#    samplel_intervals=[]
#    for key1 in pic_samples2:
#        if key1 !='Cal':
#            samplel_intervals.extend(pic_samples2[key1])
#    add_info+='Additional sample index {0} {1}\n'.format(key,samplel_intervals)
#else:
#    add_info=''
#    pass
##Create figures:
#os.chdir('Figures')
#plot_picarro_species(data)
#plot_picarro_data(data,pic_samples)
#for key in Datalogger.keys():
#    if key!='Date':
#        plt.close()
#        plt.plot(Datalogger[key])
#        plt.xlabel('Time')
#        plt.ylabel(key)
#        plt.savefig('Datalogger_'+key+'.pdf',format='pdf',bbox_inches='tight')
#        plt.close()
#
#for key in Radiosonde.keys():
#    plt.close()
#    plt.plot(Radiosonde[key])
#    plt.xlabel('Time')
#    plt.ylabel(key)
#    plt.savefig('Radiosonde_'+key+'.pdf',format='pdf',bbox_inches='tight')
#    plt.close()
#os.chdir('..')
##print(data.columns.values()
#date=data_save['Date'][0]
#
#cal=cal_string(data,pic_samples,add_info)
#with open('Processed/{}_LISA_flight.csv'.format(date.replace('-','')),'w') as result:
#    result.write(sample_info+'\n'+unit_str)
#    result.write(cal)
#    result.write('End of header information\n')
#    data_save.to_csv(result,index=False)
#    result.close()
#     
#
#
#quit()
