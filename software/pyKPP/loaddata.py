#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 14:30:34 2019

@author: joram
"""

#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from glob import glob
#%%
files=glob('/Users/joram/scripts/Modelling/kpp_py_interface/Results_run/*/*.kppdat')
#%%

# =============================================================================
# load data
# =============================================================================
key=''
for f in files:
    data=pd.read_csv(f)
    #if key=='':
    #    print data.keys()
    #    key=input('give me a key to plot ')


    plt.plot(data['Time'][:],data['CO'][:],label=f.split('/')[-1])
#plt.legend()
plt.show()    
##%%
#data=pd.read_csv(f)  
#s=[0.000000000000000000]*len(data)
#for key in data.keys():
#    if 'Br' in key:
##        plt.plot(data[key],label=key)
#        s+=data[key]
#        
#        
#        plt.plot(s,label=key)
#plt.legend()
#
##%%
#def meta_to_dict(files):
#    f=open(files,'r')
#    lines=f.readlines()
#    f.close()
#    info={}
#    for line in lines:
#        for el in line.strip('{}').split(','):
#            key=el.split(':')[0]
#            val=el.split(':')[1]
#            try:
#                val=float(val)
#            except ValueError:
#                val=val.strip("'").strip(" '")
#            info[key.strip("'").strip(" '")]=val
#    return info
## =============================================================================
## 
## =============================================================================
##%%
#LISA_dir='/Users/joram/Documents/PhD_work_related/Data/LISAs_CO_Measurements/Processed/Profiles'
#def import_LISA(LISA_dir):
##    os.chdir(LISA_dir)
#    files=glob(LISA_dir+'/'+'*.csv')
#
#    data={}
#    for f in files:
#        date=f.split(' ')[1].replace('-','_')
#        df=pd.read_csv(f,sep=',',dtype=None)
#        data[date]=df
#    return data
#data = import_LISA(LISA_dir)
##%%
#keys1=[  u'Temperature', u'Theta (K)',
#       u'Relative Humidtiy', u'Lon', u'Lat', u'Weighted p(mbar)', u'Altitude',
#       u'Samplesize (L)', u'Vertical resolution', u'CO2(ppm)', 
#       u'CH4(ppb)', u'CO(ppb)',
#       u'CO_uu', u'Delta C13 (VPDB) no delta 17 corr',
#       u'Delta O18 (VSMOW)']
#
#keys2=[ u'Temperature', u'Theta (K)',
#       u'Relative Humidtiy', u'Lon', u'Lat', u'Weighted p(mbar)', u'Altitude',
#       u'Samplesize (L)', u'Vertical resolution', u'CO2(ppm)', 
#       u'CH4(ppb)', u'CO(ppb)',
#       u'CO_uu', u'Delta C13 (VPDB) no delta 17 corr',
#       u'Delta O18 (VSMOW)']
#
#for key1 in keys1:
#    for key2 in keys2:
#        if key1!=key2:
#            for dat in data:
#                plt.plot(data[dat][key1],data[dat][key2],label=dat)
#                plt.xlabel(key1)
#                plt.ylabel(key2)
#                plt.legend()
#            plt.savefig(key1+key2+'.pdf',format='pdf')
#            plt.show()
