#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 22 16:49:10 2019
@author: joram
"""
import click 
import sys 
from netCDF4 import Dataset
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
from atmos.composition import o3_2_col
from JVALPP import *
from lodautil import get_CAMS_profile
from lodautil import date_to_hours
@click.command()
#Default values for optional parameters
#Deal with options
@click.option('--slf','-f','slf',default=0,type=int,help="Sea land fraction, 0 = sea")
@click.option('--nsza','-s','nsza',default=19,type=int,help="number of solar zenith angles")
@click.option('--albedo','-a','albedo',default=0.07,type=float,help="surface albedo")
@click.option('--date','-d','date',default="20170426",type=str,help="Date in yyyymmdd")
@click.option('--time','-t','time',default="1200",type=str,help="Time in HHMM")
@click.option('--lon','-l','longitude',default=1,type=float,help="longitude in degrees 0--360")
@click.option('--lat','-p','latitude',default=1,type=float,help="latitude in degrees -90--90 ")
@click.argument('cams_data',default='/home/joram/research/data/ECMWF_CAMS/Ozone_CAMS_annual.nc', type=click.Path(exists=True))
#program 
def main(nsza,albedo,slf,date,time,latitude,longitude,cams_data):
    '''This utility loads ozone and prepares a jval.f90 file to calculate photolysis rates'''
#Load data
    #convert pressure from mbar to Pa:
# calculate relative ozone and ozone column
    
    year=date[0:4]
    month=date[4:6]
    day=date[6:8]
    hours=time[0:2]
    minutes=time[2:4]

    filename="cams2jval"+date+'T'+time
    sza=np.linspace(0,90,nsza)
    nlev=25
    nc_fid=Dataset(cams_data)
    
    #from p= 100 Pa to 0 we linearly interpolate. jval requires relo3 and v3 to be of dim nlev+1
    
    hours=date_to_hours(int(year),int(month),int(day),int(hours),int(minutes))
    press=np.concatenate(([0.5],np.array(nc_fid['level'][:])))*100
    relo3=get_CAMS_profile('go3',hours,latitude,longitude,nc_fid)*28.970/47.997
    relo3=np.concatenate(([0.5*relo3[0]],relo3))
    v3=o3_2_col(press,relo3)
    
    press=press[1:]  
    temp=get_CAMS_profile('t',hours,latitude,longitude,nc_fid)
    rhum=get_CAMS_profile('r',hours,latitude,longitude,nc_fid)
    
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
