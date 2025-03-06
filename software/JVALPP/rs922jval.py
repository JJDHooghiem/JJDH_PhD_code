#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 22 16:49:10 2019

@author: joram
"""

#%%
import click
import sys
#import os
#from glob import glob
#import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
from atmos.composition import o3_2_col
from JVALPP import *
@click.command()
#Default values for optional parameters
#Deal with options
@click.option('--slf','-f','slf',default=0,type=int,help="Sea land fraction, 0 = sea")
@click.option('--nlev','-l','nlev',default=19,type=int,help="number of levels")
@click.option('--nsza','-s','nsza',default=10,type=int,help="number of solar zenith angles")
@click.option('--albedo','-a','albedo',default=0.07,type=float,help="surface albedo")
@click.argument('sonde_data',type=click.Path(exists=True))
#program 
def main(sonde_data,nlev,nsza,albedo,slf):
    '''This utility loads ozone and prepares a jval.f90 file to calculate photolysis rates'''
#Load data
    filename=sonde_data.split(',')[0]
    sonde_data=pd.read_csv(sonde_data, sep='\s+',header=None,names=['P','Time','Alt','T','RH','Tin','PO3','Windir','Windspeed'],skiprows=144)
    #convert pressure from mbar to Pa:
    if np.min(sonde_data['P'])>10:
        print("minimum pressure did not exceed 10 mbar, exit without file production")
        exit() 
    sonde_data.loc[:,'P']=100*sonde_data['P']
    sonde_data=sonde_data.iloc[::-1].reset_index()
# calculate relative ozone and ozone column
    sonde_data['relO3']=(sonde_data['PO3']/1000.)/(sonde_data['P'])
    sonde_data['colO3']=o3_2_col(sonde_data['P'],sonde_data['relO3'])
    sza=np.linspace(0,90,nsza)
    if nlev==19:
        press = np.array([np.min(sonde_data['P']),#Pa, original jval with the topmost pressure level added. since in jval dim(v3) is nlev+1 
        1000., 3000., 5040., 7339., 10248., 14053., 18935., 24966., 32107., 
        40212., 49027., 58204., 67317., 75897., 83472., 89631., 94099.,     
        96838., 98169. ])
    else:
        press=np.linspace(np.min(sonde_data['P']),np.max(sonde_data['P']),nlev+1)
    v3=interp1d(sonde_data['P'],sonde_data['colO3'],fill_value="extrapolate")(press)
    relo3=interp1d(sonde_data['P'],sonde_data['relO3'],fill_value="extrapolate")(press)
# Generate the (nlev) arras     
    press=press[1:]  
    temp=interp1d(sonde_data['P'],sonde_data['T'],fill_value="extrapolate")(press)+273.15
    rhum=interp1d(sonde_data['P'],sonde_data['RH'],fill_value="extrapolate")(press)
    print("creating file "+filename+'_jval.f90')
    with open(filename+'_jval.f90','w') as f:
        f.write(jval_code.format(
filename=filename,
v3=np2f90_array(v3),
relo3=np2f90_array(relo3),
press=np2f90_array(press),
temp=np2f90_array(temp),
rhum=np2f90_array(rhum),
albedo=albedo,
slf=slf,
nsza=nsza,
nlev=nlev,
sza=np2f90_array(sza)
            ))
        f.close()
if __name__=="__main__":
    main()
     
