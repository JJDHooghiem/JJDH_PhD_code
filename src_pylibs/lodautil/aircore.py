"""
Author: Joram Jan Dirk Hooghiem

This code was written for the analysis presented in the disseration of Joram Jan Dirk Hooghiem
Functions that do the core analysis are presented in here.  

This program is free software: you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software Foundation, 
version 3. This program is distributed in the hope that it will be useful, but 
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS 
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. 

You should have received a copy of the GNU General Public License along with this 
program. If not, see <http://www.gnu.org/licenses/>.
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd 
from glob import glob
import numpy as np
import time
import config

def AirCore_load():
    """
    Loads the aircore september data RUG001 sep 4-7 2017
    Puts the aircore data in a dictionary and returns that dictionary. 
    keys will be formatted RUG001 GMD002 based on filename or intermediat hardcoded definition for preliminary data.
    """ 
    AirCore={} 
    for f in glob(config.DataDir+'/AirCore_Measurements/Final_profiles/RUG_Sodankyla_AirCore_1/*.naf'):
       date=f.split('/')[-1].split('_')[2] 
       AC='RUG002'
       AirCore[AC+'_'+date]=import_AirCore(f)

    for f in glob(config.DataDir+'/AirCore_Measurements/PrelimTrain/*'):
        if f.endswith('ict'):
            date=f.split('/')[-1].split('_')[2][:8] 
            AC=f.split('/')[-1].split('_')[1]
            AirCore[AC+'_'+date]=import_AirCore(f)

        if f.endswith('csv'):
            date=f.split('/')[-1].split('_')[1] 
            AC='RUG00X'            
            AirCore[AC+'_'+date]=import_AirCore(f)
        if f.endswith('txt'):
            date=f.split('/')[-1].split('_')[2] 
            AC='TRN00X'
            AirCore[AC+'_'+date]=import_AirCore(f)
    return AirCore

#['Mid_UTC','Start_UTC','Stop_UTC','LAT','LON','P','GPS_ALT','T','RH','CO2','CO2_unc','CH4','CH4_unc','CO','CO_unc','THETA','upper_alt_unc_lim_co2','lower_alt_unc_lim_co2','upper_alt_unc_lim_ch4','lower_alt_unc_lim_ch4','upper_alt_unc_lim_co','lower_alt_unc_lim_co']
remapkeys={'Time'      : 'Mid_UTC',
        'Lat.'         : 'LAT',
        'Long.'        : 'LON',
        'Alt'          : 'GPS_ALT',
        'sdCO2'        : 'CO2_unc',
        'sdCH4'        : 'CH4_unc',
        'sdCO'         : 'CO_unc',
        'sdH2O'        : 'H2O_unc',
        'sdN2O'        : 'N2O_unc',
        'p.mbar.'      : 'P',
        'cos.ppt.'     : 'COS',
        'n2o.ppb.'     : 'N2O',
        'co2.ppm.'     : 'CO2',
        'ch4.ppb.'     : 'CH4',
        'co.ppb.'      : 'CO',
        'time.qcls'    : 'TIME',
        'yr.qcls'      : 'yr',
        'mon.qcls'     : 'mon',
        'day.qcls'     : 'day',
        'hr.qcls'      : 'HH',
        'min.qcls'     : 'MM',
        'sec.qcls'     : 'SS',
        'height.m.'    : 'GPS_ALT',
        'T.amb.'       : 'T',
        'rh.amb.'      : 'RH',
        'u.amb.'       : 'U',
        'v.amb.'       : 'V',
        'lat.amb.'     : 'LAT',
        'lon.amb.'     : 'LON',
        'time.flight.' : 'MISC1',
        'sample.no.'   : 'MISC2',
        'time.pic'     : 'TIME',
        'yr.pic'       : 'yr',
        'mon.pic'      : 'mon',
        'day.pic'      : 'day',
        'hr.pic'       : 'HH',
        'min.pic'      : 'MM',
        'sec.pic'      : 'SS',
        'co2.un.ppm.'  : 'CO2_unc',
        'ch4.un.ppb.'  : 'CH4_unc',
        'co.un.ppb.'   : 'CO_unc',
        'time':'Mid_UTC',
        'T.k.':'T',
        'rh.pct':'RH', 
        'height.m.':'GPS_ALT',
        'u.mps':'U',
        'v.mps':'V',
        'lat.deg.':'LAT',
        'lon.deg.':'LON',
        'theta.k.':'THETA',
        }
def ac2pd(filename,sp,sk):
    if filename.endswith('.txt'):
        dat=pd.read_csv(config.DataDir+'/AirCore_Measurements/PrelimTrain/AC_TRN_20190611_001_CO2_CH4_CO_H2O_v10.txt',skiprows=[*list(range(59)),60,61],sep='\s+')
        data=pd.read_csv(filename,skiprows=[*list(range(sk)),sk+1,sk+2],sep=sp)
        # data=data.drop([0]).reset_index()
    else: 
        data=pd.read_csv(filename,sep=sp,skiprows=sk)
    data=data.replace(99999.00,np.nan)
    data=data.replace(-7777.00,np.nan)
    data=data.replace(-8888.00,np.nan)
    data=data.replace(-9999.00,np.nan)
    #data.index=pd.to_datetime([time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(i)) for i in data['time']])
    data.rename(columns=remapkeys,inplace=True)
    return data
def import_AirCore(filename):
    """
    Assumes .naf file to import aircoredata. Adds datetime index,
    Returns a pandas DataFrame Also takes care of all the different headers  
    """
    if filename.endswith('ict'):
        sk=60
        sp=','
    elif filename.endswith('txt'):
        sp='\s+'
        if filename.endswith('AC_TRN_20190611_001_CO2_CH4_CO_H2O_v10.txt'):
            sk=59
        elif filename.endswith('AC_TRN_20190618_019_CO2_CH4_CO_N2O_H2O_v10.txt'):
            sk=69
        elif filename.endswith('AC_TRN_20190620_021_CO2_CH4_CO_N2O_H2O_v10.txt'):
            sk=67
        elif filename.endswith('AC_TRN_20190621_026_CO2_CH4_CO_H2O_v10.txt'):
            sk=64
    elif filename.endswith('csv'):
        sk=0
        sp=','
    elif filename.endswith('naf'):
        sk=31
        sp=' '
    data=ac2pd(filename,sp,sk)
    return data
