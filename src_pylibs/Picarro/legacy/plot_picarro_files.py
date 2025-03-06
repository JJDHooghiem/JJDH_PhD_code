#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 12 12:50:27 2018

@author: Joram
"""

#%%
import os
from glob import glob
import matplotlib.pyplot as plt
import pandas as pd
os.chdir('/Volumes/ExternalStorageJJDH/Work_Storage/2018_Ringo backup files/')

for a,b,c in os.walk(os.getcwd()):#'/Users/Joram/Documents/PhD_work_related/Data/Campaigns/2017_Sodankylä_Campaigns/2017_04_21_LightAirCore_01_Flight/py'):
    os.chdir(a)
    files=glob('*.dat')
    
    
    for f in files:
        fig,axes=plt.subplots(4,1,figsize=(6,10))
        
        df=pd.read_csv(f,sep='\s+',dtype=None)
        sel=df['H2O']<0.01
        
        axes[0].plot(df['JULIAN_DAYS'][sel],df['CO2'][sel],'o',label=f)
        axes[1].plot(df['JULIAN_DAYS'][sel],df['CH4'][sel],'o',label=f)
        axes[2].plot(df['JULIAN_DAYS'][sel],df['CO'][sel],'o',label=f)
        axes[3].plot(df['JULIAN_DAYS'][sel],df['H2O'][sel],'o',label=f)
        axes[0].set_ylabel('CO2')
        axes[1].set_ylabel('Ch4')
        axes[2].set_ylabel('CO')
        axes[3].set_ylabel('H2O')
        axes[0].legend()
        fig.tight_layout()

#        fig.savefig('/Users/Joram/Desktop/Figures/'+f.split('.')[0]+'_dry.pdf',format='pdf')
        #%%
        files=glob('*.dat')