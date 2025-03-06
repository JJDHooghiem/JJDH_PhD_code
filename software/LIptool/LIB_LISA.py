#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
import time
from calendar import timegm
from glob import glob

import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
from scipy.optimize import curve_fit
from scipy.stats import linregress

try:
    from .LISA_config import *
    print('found LISA_config')
except ImportError:
    from .LISA_default import *
    print('using default configuration')
from io import StringIO

import matplotlib.pyplot as plt

#==============================================================================
#
#Picarro Utilities 
#
# Future deprecation warning will be moved to its own repo
#
#==============================================================================
srcdir='/home/joram/.local/src/python/LIptool'
def clear_pyc():
    try:
        os.remove(srcdir+'/LISA_config.py')
    except FileNotFoundError:
        pass
    try:
        os.remove(srcdir+'/LISA_config.pyc')
    except FileNotFoundError:
        pass
    return
def time_stamp(data):
    data.index=pd.to_datetime(data['DATE']+' '+data['TIME'],format='%Y-%m-%d %H:%M:%S.%f')
    timetosec(data)
    return

def timetosec(data):
    m=len(data['TIME'])
    t=[]
    for j in range(0,m):
        s=data['TIME'][j].split(':')
        t.append(float(s[0])*3600+float(s[1])*60+float(s[2]))
    data['AbsTime']=t
    s=[]
    for j in range(0,len(t)):
        s.append(t[j]-t[0])
    data['RelTime']=s
    return
# =============================================================================
# Vapor corrections
# =============================================================================
def co2vcor(data):
    a=co2_water_a
    b=co2_water_b
    H2OREP=data['h2o_reported']
    CO2raw=data['CO2_raw']
    CO2dry=CO2raw/(1+a*H2OREP+b*H2OREP**2)
    return CO2dry

def ch4vcor(data):
    a=ch4_water_a
    b=ch4_water_b
    H2OREP=data['h2o_reported']
    CH4raw=data['CH4_raw']
    CH4dry=CH4raw/(1+a*H2OREP+b*H2OREP**2)
    return CH4dry


def covcor(data):
    a,b,c,d=Dco_water_a,Dco_water_b,Dco_water_c,Dco_water_d
    data["deltaCO"]= a*data["b_h2o_pct"] + b*data["b_h2o_pct"]**2 + c*data["b_h2o_pct"]**3 + d*data["b_h2o_pct"]**4
    a=co_water_a
    b=co_water_b
    COcor=(data["CO_raw"]-data["deltaCO"])/(1+a*data['h2o_reported']+b*data['h2o_reported']**2)
    return COcor


# =============================================================================
# Pressure corrections
# =============================================================================

def co2cavcor(data):
    '''
    applies temperature and pressure correction
    '''
    a,b=co2_temp_a,Cav_T_set
    CO2Tcor=data['CO2']+a*(data['CavityTemp']-b)
    
    c,d=co2_pres_a,Cav_P_set
    CO2raw=CO2Tcor+c*(data['CavityPressure']-d)
    return CO2raw

def ch4cavcor(data):
    '''
    applies temperature and pressure correction and converts to pbb
    '''
    a,b=ch4_temp_a,Cav_T_set
    CH4Tcor=1000.0*data['CH4']+a*(data['CavityTemp']-b)
    c,d=ch4_pres_a,Cav_P_set
    CH4raw=CH4Tcor+c*(data['CavityPressure']-d)
    return CH4raw


    
# =============================================================================
# Calibration
# =============================================================================

def co2cal(data,drift=0):
    data['CO2_uncal']=data['CO2_cor']
    CO2cor=((data['CO2_uncal']*co2_cal_a)+co2_cal_b)+drift
    return CO2cor

def ch4cal(data,drift=0):
    data['CH4_uncal']=data['CH4_cor']
    CH4cor=((data['CH4_uncal']*ch4_cal_a)+ch4_cal_b)+drift
    return CH4cor

def cocal(data,drift=0):
    data['CO_uncal']=data['CO_cor']
    COcor=((data['CO_uncal']*co_cal_a)+co_cal_b)+drift
    return COcor

def COcal(data):
    '''
all$COw <- (calib["co_conc_intercept",] + calib["co_conc_slope",]* (all$Peak84 + calib["co_offset",] + (calib["co_water_linear",] * all$H2O_co) + (calib["co_water_quadratic",]* all$H2O_co^2) + (calib["co_water_co2",] * all$H2O_co * ((calib["co2_conc_slope",]*all$Peak14)+calib["co2_conc_intercept",])) + (calib["co_co2_linear",] * ((calib["co2_conc_slope",]*all$Peak14)+calib["co2_conc_intercept",]))))*1000
all$COdryLSCE <- all$COw/(calib["co_wd_quadratic",]*(all$H2Or)^2 + calib["co_wd_linear",]*(all$H2Or) + 1)
    '''
    CO_wet=(co_conc_intercept+co_conc_slope*(data['peak84_raw']+co_offset+(co_water_linear*data['b_h2o_pct'])+(co_water_quadratic*data['b_h2o_pct']**2)+(co_water_co2*data['b_h2o_pct']*((co2_conc_slope*data['peak_14'])+co2_conc_intercept))+(co_co2_linear*((co2_conc_slope*data['peak_14'])+co2_conc_intercept))))*1000
    CO_dry=CO_wet/(co_wd_quadratic*data['h2o_reported']**2 + co_wd_linear*data['h2o_reported'] + 1)
    #print(CO_dry
    return CO_dry

def cavitycutoff(data):
   data['CO2']=[np.nan if abs(data['CavityPressure'][i]-Cav_P_set)>Cav_P_cutoff or abs(data['CavityTemp'][i]-Cav_T_set)>Cav_T_cutoff else data['CO2'][i] for i in range(0,len(data['CavityPressure']))]
   data['CH4']=[np.nan if abs(data['CavityPressure'][i]-Cav_P_set)>Cav_P_cutoff or abs(data['CavityTemp'][i]-Cav_T_set)>Cav_T_cutoff else data['CH4'][i] for i in range(0,len(data['CavityPressure']))]
   data['peak84_raw']=[np.nan if abs(data['CavityPressure'][i]-Cav_P_set)>Cav_P_cutoff or abs(data['CavityTemp'][i]-Cav_T_set)>Cav_T_cutoff else data['peak84_raw'][i] for i in range(0,len(data['CavityPressure']))]
   return

def removefill(data):
   data["CO2"]=[data["CO2"][i] if data["species"][i]==1 else np.nan for i in range(0,len(data["CO2"]))]
   data["peak84_raw"]=[data["peak84_raw"][i] if data["species"][i]==4 else np.nan for i in range(0,len(data["CO"]))]
   data["CO"]=[data["CO"][i] if data["species"][i]==4 else np.nan for i in range(0,len(data["CO"]))]
   data["CH4"]=[data["CH4"][i] if data["species"][i]==2 else np.nan for i in range(0,len(data["CH4"]))]
   data["H2O"]=[data["H2O"][i] if data["species"][i]==3 else np.nan for i in range(0,len(data["H2O"]))]
   data["h2o_reported"]=[data["h2o_reported"][i] if data["species"][i]==3 else np.nan for i in range(0,len(data["h2o_reported"]))]
   return

def JKADS(Data_Picarro):
    if len(Data_Picarro)!=1:
        data=[pd.read_csv(dat_file,sep='\s+',dtype=None) for dat_file in Data_Picarro]
#        for dat in data:
#            time_stamp(dat)
        data=pd.concat(data,axis=0)
        time_stamp(data)
        data=data.sort_index()
    

    else:
        data=pd.read_csv(Data_Picarro[0],sep='\s+',dtype=None)
        time_stamp(data)
    data['index']=np.array(range(0,len(data['N2O'])))
    H2Operc=data['H2O']/1E6
    data['N2O_d']=data['N2O']/(JKADS_N2O_water_a*H2Operc**3+JKADS_N2O_water_b*H2Operc**2+JKADS_N2O_water_c*H2Operc+1)
    data['N2O_cor']=JKADS_N2O_Cal_a * data['N2O_d'] + JKADS_N2O_Cal_b


    data['CO_d']=data['CO']/(JKADS_CO_water_a*H2Operc**2+JKADS_CO_water_b*H2Operc+JKADS_CO_water_c)
    data['CO_cor']=JKADS_CO_Cal_a * data['CO_d'] + JKADS_CO_Cal_b
    return data

def JKADS_calibration(data,time_stamps,resample=False):
    '''
    true=measured+ofset->ofset=true-measured
    '''
    cal_n2o=np.array([])
    cal_co=np.array([])

    Time_n2o=[]
    Time_co=[]
    if resample==False:
        for i in range(0,int( len(time_stamps)/2 )):
            a=time_stamps[i*2]
            b=time_stamps[i*2+1]
            cal_n2o=np.concatenate((cal_n2o,np.array(data['N2O_cor'][a:b][np.isfinite(data['N2O_cor'])])))
            cal_co=np.concatenate((cal_co,np.array(data['CO_cor'][a:b][np.isfinite(data['CO_cor'])])))
            Time_n2o=np.concatenate((Time_n2o,np.array(data['RelTime'][a:b][np.isfinite(data['N2O_cor'])])))
            Time_co=np.concatenate((Time_co,np.array(data['RelTime'][a:b][np.isfinite(data['CO_cor'])])))
    else:
        for i in range(0,int(len(time_stamps)/2)):
            a=time_stamps[i*2]
            b=time_stamps[i*2+1]
            interval='1T'
            cal_n2o=np.concatenate((cal_n2o,np.array(data['N2O_cor'][a:b][np.isfinite(data['N2O_cor'])].resample(interval).mean())))
            cal_co=np.concatenate((cal_co,np.array(data['CO_cor'][a:b][np.isfinite(data['CO_cor'])].resample(interval).mean())))
            Time_n2o=np.concatenate((Time_n2o,np.array(data['RelTime'][a:b][np.isfinite(data['N2O_cor'])].resample(interval).mean())))
            Time_co=np.concatenate((Time_co,np.array(data['RelTime'][a:b][np.isfinite(data['CO_cor'])].resample(interval).mean())))

    cal_n2o_ofset=n2o_cal_tar-cal_n2o
    cal_co_ofset=co_cal_tar-cal_co
    print(np.mean(cal_n2o_ofset),'\t',np.std(cal_n2o_ofset))
    print(np.mean(cal_co_ofset),'\t', np.std(cal_co_ofset))
    n2o_linregress_result=linregress(Time_n2o,cal_n2o_ofset)
    co_linregress_result=linregress(Time_co,cal_co_ofset)

    data['N2O_cor_lin']=n2o_linregress_result[0]*data["RelTime"]+n2o_linregress_result[1]
    data['CO_cor_lin']=co_linregress_result[0]*data["RelTime"]+co_linregress_result[1]

    n2o_res_lin=n2o_cal_tar-(cal_n2o+(n2o_linregress_result[0]*Time_n2o+n2o_linregress_result[1]))
    co_res_lin=co_cal_tar-(cal_co+(co_linregress_result[0]*Time_co+co_linregress_result[1]))

    n2o_res_1p=n2o_cal_tar-(cal_n2o+np.mean(cal_n2o_ofset))
    co_res_1p=co_cal_tar-(cal_co+np.mean(cal_co_ofset))

    data['N2O_cal']=data['N2O_cor']+data['N2O_cor_lin']
    data['CO_cal']=data['CO_cor']+data['CO_cor_lin']

    f, axes_array=plt.subplots(2,2,sharex=True,sharey=False, figsize=(20,20))

    axes_array[0,0].plot(Time_n2o,cal_n2o_ofset,marker='o',color='r',linestyle='')
    axes_array[1,0].plot(Time_co,cal_co_ofset,marker='o',color='r',linestyle='')

    axes_array[0,0].plot(data["RelTime"],data['N2O_cor_lin'],color='g',linewidth=2)
    axes_array[1,0].plot(data["RelTime"],data['CO_cor_lin'],color='g',linewidth=2)

    axes_array[0,0].set_title('Green fit: ${0:f}t+{1:f}$, R$^2=${2}'.format(n2o_linregress_result[0],n2o_linregress_result[1],np.round(n2o_linregress_result[2]**2,2)))
    axes_array[1,0].set_title('Green fit: ${0:f}t+{1:f}$, R$^2=${2}'.format(co_linregress_result[0],co_linregress_result[1],np.round(co_linregress_result[2]**2,2)))

    axes_array[0,0].set_ylabel('$\Delta$CO$_2$ (ppm) (True-Measured)')
    axes_array[1,0].set_ylabel('$\Delta$CO(ppb) (True-Measured)')
    axes_array[1,0].set_xlabel('time (min)')

    axes_array[0,1].plot(Time_n2o,n2o_res_lin,marker='o',color='r',linestyle='')
    axes_array[1,1].plot(Time_co,co_res_lin,marker='o',color='r',linestyle='')

    axes_array[0,1].plot(Time_n2o,n2o_res_1p,marker='o',color='g',linestyle='')
    axes_array[1,1].plot(Time_co,co_res_1p,marker='o',color='g',linestyle='')

    axes_array[0,1].set_ylim([-0.5,0.5])
    axes_array[1,1].set_ylim([-10,10])

    axes_array[0,1].set_title('Linear in red, mean: {0:f}$\pm${1:f}\n1 point in blue, mean: {2:f}$\pm${3:f}'.format(np.mean(n2o_res_lin),np.std(n2o_res_lin),np.mean(n2o_res_1p),np.std(n2o_res_1p)))
    axes_array[1,1].set_title('Linear in red, mean: {0:f}$\pm${1:f}\n1 point in blue, mean: {2:f}$\pm${3:f}'.format(np.mean(co_res_lin),np.std(co_res_lin),np.mean(co_res_1p),np.std(co_res_1p)))



    axes_array[0,1].set_ylabel('Residual \ce{N2O} (ppb) (True-Measured)')
    axes_array[1,1].set_ylabel('Residual \ce{CO} (ppb) (True-Measured)')
    axes_array[1,1].set_xlabel('time (min)')
    #plt.show()
    return f

def calibration(data,time_stamps,resample=False):
    '''
    true=measured+ofset->ofset=true-measured
    '''
    cal_co2=np.array([])
    cal_ch4=np.array([])
    cal_co=np.array([])

    Time_co2=[]
    Time_ch4=[]
    Time_co=[]
    if resample==False:
        for i in range(0,int(len(time_stamps)/2)):
            a=time_stamps[i*2]
            b=time_stamps[i*2+1]
            cal_co2=np.concatenate((cal_co2,np.array(data['CO2_cor'][a:b][np.isfinite(data['CO2_cor'])])))
            cal_ch4=np.concatenate((cal_ch4,np.array(data['CH4_cor'][a:b][np.isfinite(data['CH4_cor'])])))
            cal_co=np.concatenate((cal_co,np.array(data['CO_cor'][a:b][np.isfinite(data['CO_cor'])])))
            Time_co2=np.concatenate((Time_co2,np.array(data['RelTime'][a:b][np.isfinite(data['CO2_cor'])])))
            Time_ch4=np.concatenate((Time_ch4,np.array(data['RelTime'][a:b][np.isfinite(data['CH4_cor'])])))
            Time_co=np.concatenate((Time_co,np.array(data['RelTime'][a:b][np.isfinite(data['CO_cor'])])))
    else:
        for i in range(0,int(len(time_stamps)/2)):
            a=time_stamps[i*2]
            b=time_stamps[i*2+1]
            interval='1T'
            cal_co2=np.concatenate((cal_co2,np.array(data['CO2_cor'][a:b][np.isfinite(data['CO2_cor'])].resample(interval).mean())))
            cal_ch4=np.concatenate((cal_ch4,np.array(data['CH4_cor'][a:b][np.isfinite(data['CH4_cor'])].resample(interval).mean())))
            cal_co=np.concatenate((cal_co,np.array(data['CO_cor'][a:b][np.isfinite(data['CO_cor'])].resample(interval).mean())))
            Time_co2=np.concatenate((Time_co2,np.array(data['RelTime'][a:b][np.isfinite(data['CO2_cor'])].resample(interval).mean())))
            Time_ch4=np.concatenate((Time_ch4,np.array(data['RelTime'][a:b][np.isfinite(data['CH4_cor'])].resample(interval).mean())))
            Time_co=np.concatenate((Time_co,np.array(data['RelTime'][a:b][np.isfinite(data['CO_cor'])].resample(interval).mean())))

    cal_co2_ofset=co2_cal_tar-cal_co2
    cal_ch4_ofset=ch4_cal_tar-cal_ch4
    cal_co_ofset=co_cal_tar-cal_co
    print(np.mean(cal_co2_ofset),'\t',np.std(cal_co2_ofset))
    print(np.mean(cal_ch4_ofset),'\t',np.std(cal_ch4_ofset))
    print(np.mean(cal_co_ofset),'\t', np.std(cal_co_ofset))
    co2_linregress_result=linregress(Time_co2,cal_co2_ofset)
    ch4_linregress_result=linregress(Time_ch4,cal_ch4_ofset)
    co_linregress_result=linregress(Time_co,cal_co_ofset)

    data['CO2_cor_lin']=co2_linregress_result[0]*data["RelTime"]+co2_linregress_result[1]
    data['CH4_cor_lin']=ch4_linregress_result[0]*data["RelTime"]+ch4_linregress_result[1]
    data['CO_cor_lin']=co_linregress_result[0]*data["RelTime"]+co_linregress_result[1]

    co2_res_lin=co2_cal_tar-(cal_co2+(co2_linregress_result[0]*Time_co2+co2_linregress_result[1]))
    ch4_res_lin=ch4_cal_tar-(cal_ch4+(ch4_linregress_result[0]*Time_ch4+ch4_linregress_result[1]))
    co_res_lin=co_cal_tar-(cal_co+(co_linregress_result[0]*Time_co+co_linregress_result[1]))

    co2_res_1p=co2_cal_tar-(cal_co2+np.mean(cal_co2_ofset))
    ch4_res_1p=ch4_cal_tar-(cal_ch4+np.mean(cal_ch4_ofset))
    co_res_1p=co_cal_tar-(cal_co+np.mean(cal_co_ofset))

    data['CO2_cal']=data['CO2_cor']+data['CO2_cor_lin']
    data['CH4_cal']=data['CH4_cor']+data['CH4_cor_lin']
    data['CO_cal']=data['CO_cor']+data['CO_cor_lin']

    f, axes_array=plt.subplots(3,2,sharex=True,sharey=False, figsize=(20,20))

    axes_array[0,0].plot(Time_co2,cal_co2_ofset,marker='o',color='r',linestyle='')
    axes_array[1,0].plot(Time_ch4,cal_ch4_ofset,marker='o',color='r',linestyle='')
    axes_array[2,0].plot(Time_co,cal_co_ofset,marker='o',color='r',linestyle='')

    axes_array[0,0].plot(data["RelTime"],data['CO2_cor_lin'],color='g',linewidth=2)
    axes_array[1,0].plot(data["RelTime"],data['CH4_cor_lin'],color='g',linewidth=2)
    axes_array[2,0].plot(data["RelTime"],data['CO_cor_lin'],color='g',linewidth=2)

    axes_array[0,0].set_title('Green fit: ${0:f}t+{1:f}$, R$^2=${2}'.format(co2_linregress_result[0],co2_linregress_result[1],np.round(co2_linregress_result[2]**2,2)))
    axes_array[1,0].set_title('Green fit: ${0:f}t+{1:f}$, R$^2=${2}'.format(ch4_linregress_result[0],ch4_linregress_result[1],np.round(ch4_linregress_result[2]**2,2)))
    axes_array[2,0].set_title('Green fit: ${0:f}t+{1:f}$, R$^2=${2}'.format(co_linregress_result[0],co_linregress_result[1],np.round(co_linregress_result[2]**2,2)))

    axes_array[0,0].set_ylabel('$\Delta$CO$_2$ (ppm) (True-Measured)')
    axes_array[1,0].set_ylabel('$\Delta$CH$_4$(ppb) (True-Measured)')
    axes_array[2,0].set_ylabel('$\Delta$CO(ppb) (True-Measured)')
    axes_array[2,0].set_xlabel('time (min)')

    axes_array[0,1].plot(Time_co2,co2_res_lin,marker='o',color='r',linestyle='')
    axes_array[1,1].plot(Time_ch4,ch4_res_lin,marker='o',color='r',linestyle='')
    axes_array[2,1].plot(Time_co,co_res_lin,marker='o',color='r',linestyle='')

    axes_array[0,1].plot(Time_co2,co2_res_1p,marker='o',color='g',linestyle='')
    axes_array[1,1].plot(Time_ch4,ch4_res_1p,marker='o',color='g',linestyle='')
    axes_array[2,1].plot(Time_co,co_res_1p,marker='o',color='g',linestyle='')

    axes_array[0,1].set_ylim([-0.5,0.5])
    axes_array[1,1].set_ylim([-2,2])
    axes_array[2,1].set_ylim([-10,10])

    axes_array[0,1].set_title('Linear in red, mean: {0:f}$\pm${1:f}\n1 point in blue, mean: {2:f}$\pm${3:f}'.format(np.mean(co2_res_lin),np.std(co2_res_lin),np.mean(co2_res_1p),np.std(co2_res_1p)))
    axes_array[1,1].set_title('Linear in red, mean: {0:f}$\pm${1:f}\n1 point in blue, mean: {2:f}$\pm${3:f}'.format(np.mean(ch4_res_lin),np.std(ch4_res_lin),np.mean(ch4_res_1p),np.std(ch4_res_1p)))
    axes_array[2,1].set_title('Linear in red, mean: {0:f}$\pm${1:f}\n1 point in blue, mean: {2:f}$\pm${3:f}'.format(np.mean(co_res_lin),np.std(co_res_lin),np.mean(co_res_1p),np.std(co_res_1p)))


    axes_array[0,1].set_ylabel('Residual CO$_2$ (ppm) (True-Measured)')
    axes_array[1,1].set_ylabel('Residual CH$_4$(ppb) (True-Measured)')
    axes_array[2,1].set_ylabel('Residual CO(ppb) (True-Measured)')
    axes_array[2,1].set_xlabel('time (min)')
    #plt.show()
    return f

def get_Picarro(Data_Picarro,interpolate=False):

    if len(Data_Picarro)!=1:
        data=[pd.read_csv(dat_file,sep='\s+',dtype=None) for dat_file in Data_Picarro]
#        for dat in data:
#            time_stamp(dat)
        data=pd.concat(data,axis=0)
        time_stamp(data)
        data=data.sort_index()

    else:
        data=pd.read_csv(Data_Picarro[0],sep='\s+',dtype=None)
        time_stamp(data)
    removefill(data)


    cavitycutoff(data)
    index=np.array(range(0,len(data['CO2'])))
    data['index']=index
    #Apply cavity correction and change units from ppm to ppb for ch4 and co
    data['CO2_raw']=co2cavcor(data)
    data['CH4_raw']=ch4cavcor(data)
    data['CO_raw']=(co_peak84_a*data['peak84_raw']+co_peak84_b)*1000
    #Interpolate water
    interpolator=interp1d(data['RelTime'][np.isfinite(data['h2o_reported'])],data['h2o_reported'][np.isfinite(data['h2o_reported'])],fill_value='extrapolate')
    data['h2o_reported']=interpolator(data['RelTime'])

    interpolator=interp1d(data['RelTime'][np.isfinite(data['H2O'])],data['H2O'][np.isfinite(data['H2O'])],fill_value='extrapolate')
    data['H2O']=interpolator(data['RelTime'])

    #apply vapor corrections
    data['CO2_cor']=co2vcor(data)
    data['CH4_cor']=ch4vcor(data)
    if picarro=='RUG_mobile':
        data['CO_cor']=covcor(data)
    if picarro=='LSCE':
        data['CO_cor']=COcal(data)
#    #callibrate data
    data['CO2_cor']=co2cal(data)
    data['CH4_cor']=ch4cal(data)
    data['CO_cor']=cocal(data)
#    #fill CO2,CH4 and CO data
    if interpolate!=False:
        interpolator=interp1d(data['RelTime'][np.isfinite(data['CO2_cor'])],data['CO2_cor'][np.isfinite(data['CO2_cor'])],fill_value='extrapolate')
        data['CO2_cor']=interpolator(data['RelTime'])

        interpolator=interp1d(data['RelTime'][np.isfinite(data['CH4_cor'])],data['CH4_cor'][np.isfinite(data['CH4_cor'])],fill_value='extrapolate')
        data['CH4_cor']=interpolator(data['RelTime'])

        interpolator=interp1d(data['RelTime'][np.isfinite(data['CO_cor'])],data['CO_cor'][np.isfinite(data['CO_cor'])],fill_value='extrapolate')
        data['CO_cor']=interpolator(data['RelTime'])

    return data

def zoom(xdata,ydata,xlabel='x data',ylabel='y data',save_result=False):
    status='n'
    tl=len(ydata)
    print('total datapoints: '+str(len(ydata)))
    plt.clf()
#    f.show(block=False)
    plt.plot(xdata[np.isfinite(ydata)],ydata[np.isfinite(ydata)],'o')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.show(block=False)
    while status=='n':


        point,ran=input('Provide datapoint and range to zoom: ')
        if point>tl:
            point=tl-1
            print('Your index was out of bounds. I have chosen the last data point')

        if point+ran/2>tl:
            plt.plot(xdata[point-ran/2:][np.isfinite(ydata)],ydata[point-ran/2:][np.isfinite(ydata)],linestyle='-',color='darkgreen')
            plt.plot(xdata[point],ydata[point],'o',color='darkred')
        elif point-ran/2<0:
            plt.plot(xdata[0:point+ran/2][np.isfinite(ydata)],ydata[0:point+ran/2][np.isfinite(ydata)],linestyle='-',color='darkgreen')
            plt.plot(xdata[point],ydata[point],'o',color='darkred')
        else:
            plt.plot(xdata[point-ran/2:point+ran/2][np.isfinite(ydata)],ydata[point-ran/2:point+ran/2][np.isfinite(ydata)],linestyle='-',color='darkgreen')
            plt.plot(xdata[point],ydata[point],'o',color='darkred')
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.show(block=False)
        status=input('Are you happy with the current selection [y/n]: ')

    f,ax=plt.subplots(1,2,figsize=(10,10))
    ax[0].plot(xdata[np.isfinite(ydata)],ydata[np.isfinite(ydata)],linestyle='-',color='darkgreen')
    ax[0].set_xlabel(xlabel)
    ax[0].set_ylabel(ylabel)
    ax[0].plot(xdata[point],ydata[point],'o',color='darkred',label='Selected data point: ({0},{1}'.format(xdata[point],ydata[point]))


    ax[1].plot(xdata[point-ran/2:point+ran/2][np.isfinite(ydata)],ydata[point-ran/2:point+ran/2][np.isfinite(ydata)],linestyle='-',color='darkgreen')
    ax[1].plot(xdata[point],ydata[point],'o',color='darkred',label='Selected: ({0},{1})'.format(xdata[point],ydata[point]))
    ax[1].set_xlabel(xlabel)
    ax[1].set_ylabel(ylabel)
    ax[1].legend()
    ax[1].set_title('Zoom of left panel')
    if save_result==True:
        fn=input('Provide filename: ')
        f.savefig('Figures/'+fn+'.pdf',bbox_inches='tight',format='pdf')
    return f,point


def plot_picarro_species(data):
    species=['CO2','CH4','CO']
    for spec in species:
        plt.close()
        if spec=='CO':
            for key in data.keys():
                if spec in key:    
                    if not 'dry' in key:
                        if not 'lin' in key:
                            if key!='CO':
                                if not 'CO2' in key: 
                                    if not 'delta' in key: 
                                        plt.plot(data[key],'o',label=key)
        elif spec=='CO2':
            for key in data.keys():
                if spec in key:    
                    if not 'dry' in key:
                        if not 'lin' in key:
                            plt.plot(data[key],'o',label=key)
        elif spec=='CH4':
            for key in data.keys():
                if spec in key:    
                    if not 'dry' in key:
                        if not 'lin' in key:
                            if key!='CH4':
                                plt.plot(data[key],'o',label=key)

        plt.xlabel('Time')
        plt.ylabel(spec)
        plt.legend()
        plt.savefig('Picarro_'+spec+'.pdf',format='pdf',bbox_inches='tight')
    return "Made plots"
def plot_picarro_data(data,pic_samples,fname='',title='Normal calculation'):
    keylist=['CO2_cal','CO_cal','CH4_cal','H2O','CavityPressure','CavityTemp']
    for key in keylist:
        plt.close()
        plt.plot(data[key],'o')
        plt.xlabel('Time')
        plt.ylabel(key)
        for key2 in pic_samples:
            for i in range(0,int(len(pic_samples[key2])/2)):
                a=pic_samples[key2][i*2]
                b=pic_samples[key2][i*2+1]
                mean=np.round( np.nanmean( data[key][a:b] ),3 )
                std=np.round( np.nanstd( data[key][a:b] ),3 )
                plt.plot(data[key][a:b],'o',label='Sample '+key2+':\t${}\pm{}$'.format(mean,std))
        plt.legend()
        plt.suptitle(title)
        plt.savefig('Picarro_'+key+fname+'.pdf',format='pdf',bbox_inches='tight')
    return "Made plots"
# =============================================================================
# Plotting tools
# =============================================================================

def raw_plot(data, filename,use_index=True):

    f, axes_array=plt.subplots(6,sharex=False,sharey=False, figsize=(10,20))

    axes_array[0].plot(data["RelTime"][np.isfinite(data['CO2_cor'])]/60,data['CO2_cor'][np.isfinite(data['CO2_cor'])])
    axes_array[1].plot(data["RelTime"][np.isfinite(data['CH4_cor'])]/60,(data['CH4_cor'][np.isfinite(data['CH4_cor'])]))
    axes_array[2].plot(data["RelTime"][np.isfinite(data['CO_cor'])]/60,(data['CO_cor'][np.isfinite(data['CO_cor'])]))

    axes_array[3].plot(data["RelTime"]/60,data['H2O'])
    axes_array[4].plot(data["RelTime"]/60,data['CavityPressure'])
    axes_array[5].plot(data["RelTime"]/60,data['CavityTemp'])

    axes_array[0].set_ylabel('CO$_2$ (ppm)')
    axes_array[1].set_ylabel('CH$_4$(ppb)')
    axes_array[2].set_ylabel('CO(ppb)')
    axes_array[3].set_ylabel('H$_2$O(%)')
    axes_array[4].set_ylabel('Cavity Pressure (Torr)')
    axes_array[5].set_ylabel('Cavity Temperature (Celcius)')
    axes_array[4].set_ylim([Cav_P_set-2*Cav_P_cutoff,Cav_P_set+2*Cav_P_cutoff])
    axes_array[5].set_ylim([Cav_T_set-2*Cav_T_cutoff,Cav_T_set+2*Cav_T_cutoff])
    axes_array[5].set_xlabel('time (min)')

    d=filename

    axes_array[0].set_title('CO$_2$')
    axes_array[1].set_title('CH$_4$')
    axes_array[2].set_title('CO')
    axes_array[3].set_title('H$_2$O')
    axes_array[4].set_title('Cavity pressure')
    axes_array[5].set_title('Cavity temperature')

    return f


def meanplot(start, stop, data, filename, whole=False,use_index=True):
    f, axes_array=plt.subplots(6,sharex=False,sharey=False, figsize=(10,20))


    if whole==True:
        axes_array[0].plot(data["RelTime"][np.isfinite(data['CO2_cor'])]/60,data['CO2_cor'][np.isfinite(data['CO2_cor'])])
        axes_array[1].plot(data["RelTime"][np.isfinite(data['CH4_cor'])]/60,(data['CH4_cor'][np.isfinite(data['CH4_cor'])]))
        axes_array[2].plot(data["RelTime"][np.isfinite(data['CO_cor'])]/60,(data['CO_cor'][np.isfinite(data['CO_cor'])]))
        axes_array[3].plot(data["RelTime"]/60,data['H2O'])
        axes_array[4].plot(data["RelTime"]/60,data['CavityPressure'])
        axes_array[5].plot(data["RelTime"]/60,data['CavityTemp'])
    mean=[]
    time_stamps=[]
    for i in range(0,len(start)):
        if use_index==True:
            a,b=data.index[start[i]],data.index[stop[i]]
            time_stamps.append(a)
            time_stamps.append(b)
        else:
            a,b=intervalmatch(start[i],stop[i],data)
            time_stamps.append(a)
            time_stamps.append(b)

        mean.append(intervalmean(start[i],stop[i],data))
        axes_array[0].plot(data["RelTime"][a:b][np.isfinite(data['CO2_cor'])]/60,data['CO2_cor'][a:b][np.isfinite(data['CO2_cor'])],'r',linewidth=2)
        axes_array[1].plot(data["RelTime"][a:b][np.isfinite(data['CH4_cor'])]/60,(data['CH4_cor'][a:b][np.isfinite(data['CH4_cor'])]),'r',linewidth=2)
        axes_array[2].plot(data["RelTime"][a:b][np.isfinite(data['CO_cor'])]/60,(data['CO_cor'][a:b][np.isfinite(data['CO_cor'])]),'r',linewidth=2)
        axes_array[3].plot(data["RelTime"][a:b]/60,data['H2O'][a:b],'r',linewidth=2)
        axes_array[4].plot(data["RelTime"][a:b]/60,data['CavityPressure'][a:b],'r',linewidth=2)
        axes_array[5].plot(data["RelTime"][a:b]/60,data['CavityTemp'][a:b],'r',linewidth=2)

    axes_array[0].set_ylabel('CO$_2$ (ppm)')
    axes_array[1].set_ylabel('CH$_4$ (ppb)')
    axes_array[2].set_ylabel('CO (ppb)')
    axes_array[3].set_ylabel('H$_2$O(%)')
    axes_array[4].set_ylabel('Cavity Pressure (Torr)')
    axes_array[5].set_ylabel('Cavity Temperature (Celcius)')
    axes_array[4].set_ylim([Cav_P_set-2*Cav_P_cutoff,Cav_P_set+2*Cav_P_cutoff])
    axes_array[5].set_ylim([Cav_T_set-2*Cav_T_cutoff,Cav_T_set+2*Cav_T_cutoff])
    axes_array[5].set_xlabel('time (min)')

#
#    d=filename
#    if use_index==False:
#        t1=data.index[time_stamps[0]]
#        t2=data.index[time_stamps[1]]
#        t3=data.index[time_stamps[2]]
#        t4=data.index[time_stamps[3]]
#    else:
#        t1=time_stamps[0]
#        t2=time_stamps[1]
#        t3=time_stamps[2]
#        t4=time_stamps[3]
#
#    axes_array[0].set_title('Mean CO$_2$: {0}$\pm${1} and {2}$\pm${3}'.format(mean[0][0],mean[0][1],mean[1][0],mean[1][1]))
#    axes_array[1].set_title('Mean CH$_4$: {0}$\pm${1} and {2}$\pm${3}'.format(mean[0][2],mean[0][3],mean[1][2],mean[1][3]))
#    axes_array[2].set_title('Mean CO: {0}$\pm${1} and {2}$\pm${3}'.format(mean[0][4],mean[0][5],mean[1][4],mean[0][5]))
#    axes_array[3].set_title('Mean H$_2$O: {0}$\pm${1} and {2}$\pm${3}'.format(mean[0][6],mean[0][7],mean[1][6],mean[1][7]))
#    f.suptitle('Processed data {0}\nStart calibration before: {1}\ncalibration before analysis: {2}\n\nStart calibration after analysis: {3}\ncalibration after: {4}\nThe selected intervals are shown in red'.format(d,t1,t2,t3,t4),fontsize=14)

    return f,time_stamps,mean

def intervalmean(start,stop,data,Rounding=True,decimals=3,use_index=True):
    if use_index==False:
        a,b=intervalmatch(start,stop,data)
    else:
        a,b=start,stop
    if Rounding==True:
        co2=round(np.nanmean(data['CO2_cor'][a:b]),decimals)
        co2s=round(np.nanstd(data['CO2_cor'][a:b]),decimals)

        ch4=round(np.nanmean(data['CH4_cor'][a:b]),decimals)
        ch4s=round(np.nanstd(data['CH4_cor'][a:b]),decimals)

        co=round(np.nanmean(data['CO_cor'][a:b]),decimals)
        cos=round(np.nanstd(data['CO_cor'][a:b]),decimals)

        h2o=round(np.nanmean(data['H2O'][a:b]),decimals+2)
        h2os=round(np.nanstd(data['H2O'][a:b]),decimals+2)

    else:
        co2=np.nanmean(data['CO2_cor'][a:b])
        co2s=np.nanstd(data['CO2_cor'][a:b])

        ch4=np.nanmean(data['CH4_cor'][a:b])
        ch4s=np.nanstd(data['CH4_cor'][a:b])

        co=np.nanmean(data['CO_cor'][a:b])
        cos=np.nanstd(data['CO_cor'][a:b])

        h2o=np.nanmean(data['H2O'][a:b])
        h2os=np.nanstd(data['H2O'][a:b])
    return co2, co2s, ch4, ch4s,co,cos,h2o,h2os

def intervalcalmeann2o(start,stop,data,Rounding=True,decimals=3,use_index=True):
    if use_index==False:
        a,b=intervalmatch(start,stop,data)
    else:
        a,b=start,stop
    if Rounding==True:
        n2o=round(np.nanmean(data['N2O_cal'][a:b]),decimals)


        n2os=round(np.nanstd(data['N2O_cal'][a:b]),decimals)

        co=round(np.nanmean(data['CO_cal'][a:b]),decimals)
        cos=round(np.nanstd(data['CO_cal'][a:b]),decimals)


    else:
        n2o=np.nanmean(data['N2O_cal'][a:b])
        n2os=np.nanstd(data['N2O_cal'][a:b])

        co=np.nanmean(data['CO_cal'][a:b])
        cos=np.nanstd(data['CO_cal'][a:b])

    return n2o,n2os,co,cos
def intervalcalmean(start,stop,data,Rounding=True,decimals=3,use_index=True):
    if use_index==False:
        a,b=intervalmatch(start,stop,data)
    else:
        a,b=start,stop
    if Rounding==True:
        co2=round(np.nanmean(data['CO2_cal'][a:b]),decimals)
        co2s=round(np.nanstd(data['CO2_cal'][a:b]),decimals)

        ch4=round(np.nanmean(data['CH4_cal'][a:b]),decimals)
        ch4s=round(np.nanstd(data['CH4_cal'][a:b]),decimals)

        co=round(np.nanmean(data['CO_cal'][a:b]),decimals)
        cos=round(np.nanstd(data['CO_cal'][a:b]),decimals)

        h2o=round(np.nanmean(data['H2O'][a:b]),decimals+2)
        h2os=round(np.nanstd(data['H2O'][a:b]),decimals+2)

    else:
        co2=np.nanmean(data['CO2_cal'][a:b])
        co2s=np.nanstd(data['CO2_cal'][a:b])

        ch4=np.nanmean(data['CH4_cal'][a:b])
        ch4s=np.nanstd(data['CH4_cal'][a:b])

        co=np.nanmean(data['CO_cal'][a:b])
        cos=np.nanstd(data['CO_cal'][a:b])

        h2o=np.nanmean(data['H2O'][a:b])
        h2os=np.nanstd(data['H2O'][a:b])
    return co2, co2s, ch4, ch4s,co,cos,h2o,h2os
###
# End of picarro util
###


def LoadLisa(path):
  
    #path='2017-04-26_LISA_flight.csv'
    with open(path,'r') as result:
        headerstring=result.read()
        header,data=headerstring.split('End of header information\n')
        data = StringIO(data)
        data = pd.read_csv(data, sep=",")
        unit_str, header=header.split('End of unit declaration\n')
    return unit_str,header,data

def append_unit(unit_str,unit_app):
    unit_str+=unit_app
    unit_str+='End of unit declaration\n'
    return unit_str

def append_header(header_str,header_app):
    header_str+=header_app
    header_str+='End of header information\n'
    return header_str

def SaveLisa(path,header,data):
    with open(path,'w') as result:
        result.write(header)
        data.to_csv(result,index=False)
        result.close()
    return "Data succesfully appended"

def select_file(parent):
    files=glob(parent+'/*')
    print()
    print('Pick which file is the source file')
    print()
    
    for f,s in zip(files,range(0,len(files))):
        print(s,f.replace(parent+'/',''))
    file_dir=files[int(input('Give a number: '))]
    return file_dir


def sampler_data(samplel_intervals,labels):
    flag=np.repeat('non_sample',len(data))
    date=np.repeat(str(data.index[0].date()),len(labels))
    data_summary=[]
    for i in range(0,len(labels)):
        a=samplel_intervals[i*2]
        b=samplel_intervals[i*2+1]
        flag[a:b]=labels[i]
        data_summary.append(intervalcalmean(a,b,data,Rounding=True,decimals=3,use_index=True))


#   20 data_summary=np.array(data_summary).T

    data_summary=pd.DataFrame(data_summary,columns=['CO2', 'CO2 un','CH4','CH4 un','CO','CO un','H2O','H20 un'])
    data_summary['date']=date
    data_summary['P']=labels

    data['sample']=flag
    return data,data_summary,date


def selector_ofset(x,y,inputlabel):
    global points
    points=[]
    def onpick_start(event):
        thisline = event.artist
        start = thisline.get_xdata()
        ind = event.ind
        points.append(np.take(start, ind)[0])
        plt.legend()
        if len(points)==1:
            b=np.argmin(np.abs(x - points[0]))
            selxdata=x[b]
            selydata=y[b]
            ax1.plot(selxdata,selydata,'or',label='selected: {}'.format(selxdata))
            ax1.legend()
            ax1.set_title('Happy with your selection [y/n]')
            fig.canvas.draw()
        return 
    
    def on_key(event):
        global points 
        if 'y' == event.key:
            plt.close()
        elif 'n'== event.key:
            points=[]
            plt.close()
        return
    global ax1, fig
    fig, ax1 = plt.subplots(1, 1)
    line, = ax1.plot(x,y, 'o', picker=5)
    ax1.set_title(inputlabel)
    fig.canvas.mpl_connect('pick_event', onpick_start)
    fig.canvas.mpl_connect('key_press_event', on_key)
    plt.show() 
    return points
def selector(x,y,inputlabel):
    global points
    points=[]
    def onpick_start(event):
        thisline = event.artist
        start = thisline.get_xdata()
        ind = event.ind
        points.append(np.take(start, ind)[0])
        plt.legend()
        if len(points)==2:
            b=np.argmin(np.abs(x - points[0]))
            e=np.argmin(np.abs(x - points[1]))
            selxdata=x[b:e]
            selydata=y[b:e]
            mean=np.round(np.mean(selydata),3)
            std=np.round(np.std(selydata),3)
            ax1.plot(selxdata,selydata,'or',label='mean: {}$\pm${}'.format(mean,std))
            ax1.legend()
            ax1.set_title('Happy with your selection [y/n]')
            fig.canvas.draw()
        return 
    
    def on_key(event):
        global points 
        if 'y' == event.key:
            plt.close()
        elif 'n'== event.key:
            points=[]
            plt.close()
        return
    global ax1, fig
    fig, ax1 = plt.subplots(1, 1)
    line, = ax1.plot(x,y, 'o', picker=5)
    ax1.set_title(inputlabel)
    fig.canvas.mpl_connect('pick_event', onpick_start)
    fig.canvas.mpl_connect('key_press_event', on_key)
    plt.show() 
    return points

def select_data(x,y,inputlabel):
    points=[]
    while len(points)!=2:
        points=selector(x,y,inputlabel)
    return points 

def select_samples(met_data,picarro_data,samplenames,key='CO2_cor'):
    pic_samples={}
    for p in samplenames:
        print()
        print('Select data obtained from the ',p,' hPa sample')
        print()
        idx=select_data(picarro_data['index'],picarro_data[key],p)
        #s is  selected
        pic_samples[p]=idx
    return pic_samples 


def calc_n2o_samples(met_data,picarro_data,pic_samples,samplenames):
    samples=[]
    print(pic_samples.keys())
    for p,pw in zip(samplenames,met_data['p']):
        print(p,' ',pw)
        idx=pic_samples[p]#s is  selected
        s=intervalcalmeann2o(idx[0],idx[1],picarro_data)
        s=list(s)
        samples.append(np.array(s))
    samples=pd.DataFrame(samples,columns=['N2O','N2O un','CO JKADS','CO un JKADS'])
    samples = pd.concat([met_data,samples],axis=1)
    return samples   
def calc_samples(met_data,picarro_data,pic_samples,samplenames):
    samples=[]
    print(pic_samples.keys())
    for p,pw in zip(samplenames,met_data['p']):
        print(p,' ',pw)
        idx=pic_samples[p]#s is  selected
        s=intervalcalmean(idx[0],idx[1],picarro_data)
        s=list(s)
        samples.append(np.array(s))
    samples=pd.DataFrame(samples,columns=['CO2', 'CO2 un','CH4','CH4 un','CO','CO un','H2O','H20 un'])
    # assign uncertainty as determined from picarro 
    samples.loc[:,'CO2 un']=0.12
    samples.loc[:,'CH4 un']=3
    samples.loc[:,'CO un']=1.4
    samples = pd.concat([met_data,samples],axis=1)
    return samples   

unit_str='''
Units are defined here\n
Header name:        , Description:                                                                    , unit:\n
Date                , Flight date                                                                     , dd/mm/yyyy\n
Time of sampling    , Average time at which sample was taken                                          , UTC\n
T                   , Temperature                                                                     , K\n
PT                  , Potential Temperature at 1000hPa equivalent                                     , K\n
RH                  , Relative humidity                                                               , %\n
Lon                 , Longitude                                                                       , degrees\n
Lat                 , Latitude                                                                        , degrees\n
p                   , Pressure (weighted)                                                             , hPa\n
p start             , Pressure at which sampling starts                                               , hPa\n
p stop              , Pressure at which sampling stops                                                , hPa\n
Altitude            , Altitude at Pressure (weighted)                                                 , m\n
Altitude start      , Altitude at which sampling starts                                               , m\n
Altitude stop       , Altitude at which sampling stops                                                , m\n
Vertical resolution , Vertical coverage of sample                                                     , m\n
Samplesize          , Sample-size at STP                                                              , L\n
Sampling time       , Total time of sampling                                                          , s\n
u                   , eastward wind component                                                         , m/s\n
v                   , northward wind component                                                        , m/s\n
mean speed          , mean speed during sampling                                                      , m/s\n
CO2                 , CO2 mole fraction                                                               , micro mol per mol\n
CO2 un              , 1-sigma uncertainty in CO2                                                      , micro mol per mol\n
CH4                 , CH4 mole fraction                                                               , nano mol per mol\n
CH4 un              , 1-sigma uncertainty in CH4                                                      , nano mol per mol\n
CO                  , CO mole fraction                                                                , nano mol per mol\n
CO un               , CO mole fraction                                                                , nano mol per mol\n
H2O                 , H2O in percent mole fraction NOT REPRESENTATIVE FOR THE STRATOSPHERE            , centi mol per mol\n
H2O un              , H2O uncertainy in percent mole fraction NOT REPRESENTATIVE FOR THE STRATOSPHERE , centi mol per mol\n
End of unit declaration
'''
def cal_string(picarro_data,pic_samples,add_info): 
    cal_index=pic_samples['Cal']
    samplel_intervals=[]
    for key in pic_samples:
        if key !='Cal':
            samplel_intervals.extend(pic_samples[key])
    cal1=intervalcalmean(cal_index[0],cal_index[1],picarro_data)
    cal2=intervalcalmean(cal_index[2],cal_index[3],picarro_data)
    info_str='''
Info on the crds data analysis of the LISA samples.\n
A linear calibration was perforemd, which accounted for both a small cavity temperature dependence and linear drift of the sample.\n
cal target values.\nCO2:{0}\nCH4:{1}\nCO:{2}\n
calgasmeasurements were:\n
CO2(ppm) CO2 std(ppm) CH4(ppb) CH4 std(ppb) CO(ppb) CO std(ppb)\n
{3}\n
{4}\n
calibration between index {5}
sample index {6}
both arrays containts indices as such that [start, stop, start, stop etc], so that the start means the starting index and stop means the stop index.
Python index starts with 0.\n
For the picarro settings/calibration/vapour corrections we refer to "LISA_config"-file\n
'''.format(co2_cal_tar,ch4_cal_tar,co_cal_tar,cal1,cal2,cal_index,samplel_intervals)
    info_str+=add_info
    info_str+='End of CRDS info\n'
    return info_str

def sample_info(Datalogger,key,pr):
    val=interp1d(Datalogger['PR'],Datalogger[key])(pr)
    return val

def make_data(start,stop,Datalogger,avep,ofsets):
    headerlist=['Date','Time of sampling','T','PT','RH','Lon','Lat','p','p start','p stop','Altitude','Altitude start','Altitude stop','Samplesize','Vertical resolution','Sampling time','mean speed']
    infos=[]
    for pr,s,p,ofset in zip(avep,start,stop,ofsets):
        p_bag=Datalogger[s+ofset:p]['PressureIn']
        T_air=np.nanmean(np.array(Datalogger['TemperatureIn'][s+ofset:p]))+Tstp

        info=[]
        info.append(str(Datalogger.index[s]).split(' ')[0])
        info.append(str(Datalogger.index[s]).split(' ')[1])
        info.append(np.round(sample_info(Datalogger,'TR',pr),2))
        info.append(np.round(sample_info(Datalogger,'Theta',pr),2))
        info.append(np.round(sample_info(Datalogger,'RH',pr),2))
        info.append(np.round(sample_info(Datalogger,'Lon',pr),4))
        info.append(np.round(sample_info(Datalogger,'Lat',pr),4))
        info.append(np.round(pr,2))
        info.append(np.round(Datalogger['PR'][s],2))
        info.append(np.round(Datalogger['PR'][p],2))
        info.append(np.round(sample_info(Datalogger,'Alt',pr),2))
        info.append(np.round(Datalogger['Alt'][s],2))
        info.append(np.round(Datalogger['Alt'][p],2))
        info.append(np.round(((np.max(p_bag/1000.)*V_b*Tstp*1000.)/((T_air)*Pstp))*1000,2))
        info.append(np.round(Datalogger['Alt'][p]-Datalogger['Alt'][s],2))
        info.append(np.round(Datalogger['AbsTime'][p]-Datalogger['AbsTime'][s],2))
        info.append(np.round(np.mean(Datalogger['Speed'].iloc[s:p]),2))
        infos.append(info)

    df=pd.DataFrame.from_records(data=infos,columns=headerlist)
    return df

def expsumfit(time,X,a,Tau,b):
    return X-a*np.exp(-(time-b)/Tau)

def import_logger(filename):
    '''
    imports a csv. Gives the maximum pressure allowed in the manifold.
    and the set pump time (in loop units)
    '''
    Datalogger=pd.read_csv(filename,delimiter=' *, *', engine='python')
    Datalogger.index=pd.to_datetime(Datalogger['Date'],format='%y/%m/%d %H:%M:%S')
    Datalogger['Time']=(Datalogger.index.astype(np.int64)-Datalogger.index.astype(np.int64)[0])/10**9
    Datalogger['Times']=[timegm(pd.to_datetime(Datalogger['Date'][i],format='%y/%m/%d %H:%M:%S').timetuple()) for i in range(0,len(Datalogger['Time']))]

    Pmax_set=Datalogger['Pmax'][0]                 #maximum allowed pressure
    Pump_time_set=Datalogger['Pump_delay'][0]      #Set Sampling time in steps. one step==1.2 seconds

    dt=float(Datalogger['Time'][-1]-Datalogger['Time'][0])/len(Datalogger['Time'])
    Timetrue=[]
    for i in range(0,len(Datalogger['Time'])):
        Timetrue.append(i*dt)
    Datalogger['AbsTime']=Timetrue
    return Pmax_set,Pump_time_set,Datalogger

#
# Theta should be moved to atmos take care of units
#
def theta(T,p):
    '''
    Calculates potentail temperature with 1000. mbar or hpa as the reference pressure.
    This was implemented as of 2018.
    '''
    return T*(1000./p)**(2./7)

def import_sonde(filename):
    '''
    import radiosonde data from the given tsv of csv
    '''
    # Get the utc start timestamp from the tsv file
    for line in open(filename, "r"):
        if "Launch time:" in line: timestamp=line.split(' ')[-3]+' '+line.split(' ')[-2]
        if "RS type:" in line: rs=line.split(' ')[-1].replace('\r\n','')
    Radiosonde=pd.read_csv(filename,skiprows=46,delimiter=' *\t *', engine='python')

    launch_lat=Radiosonde['Lat'][0]
    launch_lon=Radiosonde['Lon'][0]
    launch_alt=Radiosonde['Height'][0]

    Radiosonde['Times']=np.array(Radiosonde['time'])+timegm(pd.to_datetime(timestamp,format='%Y-%m-%d %H:%M:%S').timetuple())
    Radiosonde.index=pd.to_datetime([time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(t)) for t in Radiosonde['Times']])
    Radiosonde=Radiosonde.replace(-32768.0,np.nan)    #Replace the emptyfields with np.nan

    speed=np.diff(Radiosonde['Height'])/np.diff(Radiosonde['time'])
    speed=np.append(speed[0],speed)
    Radiosonde['Speed']=speed

    return Radiosonde, timestamp, rs, launch_lat,launch_lon,launch_alt

def sampling_interval(Datalogger,Pump_time_set,Sampling_start,Sampling_stop):
    '''
    Get the indeces of sampling intervals.
    '''
    start=[i for i in range(0,len(Datalogger['Pump_time'])) if Datalogger['Pump_time'][i]==Pump_time_set+Sampling_start]
    stop=[i for i in range(start[0],len(Datalogger['Pump_time'])) if Datalogger['Pump_time'][i]==Sampling_stop]
    return start,stop

def clip_datalogger(Datalogger,Radiosonde):
    interval=[]
    for m in range(0,len(Datalogger['Times'])):
        if Datalogger['Times'][m]>=Radiosonde['Times'][0] and Datalogger['Times'][m]<=Radiosonde['Times'][-1]:
            interval.append(m)
    return interval

def get_rs_data(Radiosonde,Datalogger,radiosonde_key):
    interpolator=interp1d(Radiosonde['Times'][np.isfinite(Radiosonde[radiosonde_key])],Radiosonde[radiosonde_key][np.isfinite(Radiosonde[radiosonde_key])],fill_value='extrapolate')
    Datalogger_Values=interpolator(Datalogger['Times'])
    return Datalogger_Values

def get_weights(Datalogger,start,stop):
    Weights=np.repeat(0.0,len(Datalogger))
    counter=1
    sample_interval=np.repeat(0.0,len(Datalogger))
    avep=[]
#    sampling_time=[]
    #plt.close()
    f=glob('Processed/*.json')
    if 'Processed/pressure_ofset.json' not in f: 
        ofsets=[] 
        for s,p in zip(start,stop):
        #    plt.plot(Datalogger['PressureIn'][s:p])
            x=np.arange(0,len(Datalogger))
            ofsets.append(selector_ofset(x[s:p],Datalogger['PressureIn'][s:p],'Select point where pressure starts to increase.')[0]-s)
    #plt.show()
    else:
        print('loading the earlier determined ofsets')
        with open('Processed/pressure_ofset.json','r') as inter:
            ofsets=json.load(inter)
    print()
    print(ofsets)
    print()
    plt.close()
    fig,ax=plt.subplots(1,1) 
    color=['r','b','g','c']
    #ofset=int(np.mean(ofsets))
    for s,p,c,ofset in zip(start,stop,color,ofsets):
#    T_air=np.nanmean(np.array(Radiosonde['T'][idc[ofset:]]))
        T_air=np.nanmean(np.array(Datalogger['TemperatureIn'][s+ofset:p]))+Tstp
        data=Datalogger[s+ofset:p]
#        t_ofset=Datalogger['AbsTime'][s+ofset]-Datalogger['AbsTime'][s]
        p_bag=data['PressureIn']*1000
        p_air=(Datalogger['PressureOut'][s+ofset:p])

        Time=data['AbsTime']-data['AbsTime'][0]
        opt,popt=curve_fit(expsumfit,Time,p_bag,xtol=1e-12,ftol=1e-12,maxfev=100000)
        p_model=expsumfit(Time,*opt)/1000
#        sampling_time.append(Datalogger['AbsTime'][p]-Datalogger['AbsTime'][s] )
        weights=np.diff(p_model)
        dt=np.diff(Time)
        weights=np.append(np.repeat(weights[0],ofset),weights)

        sel=[True if m>=s+1 and m<p else False for m in range(0,len(Datalogger))]
#        print(weights/np.nansum(weights))
        Weights[sel]=weights/np.nansum(weights)
        sample_interval[sel]=np.repeat(counter,len(weights))
        pmean=np.round( np.nansum(Datalogger['PR'][s+1:p]*weights/np.nansum(weights)),2 )
        avep.append(np.nansum(Datalogger['PR'][s+1:p]*weights/np.nansum(weights)))
        counter+=1
#        print(Weights[sel])
        ax.plot(Time,p_air,c,label='Outside air p={}'.format(pmean))

        ax.plot(Time,p_bag/1000,c,label='Bag air p={}'.format(pmean))
        ax.plot(Time,p_model,c,label='Fit bag air p={}'.format(pmean))

        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Pressure (mbar)')
        ax.legend()
    return Weights,sample_interval,avep,fig,ofsets

def fetch_rs_at_dl(Datalogger,Radiosonde):
    """TODO: Docstring for fetch_rs_at_dl.
    Returns
    -------
    TODO

    """
    Datalogger['PR']=get_rs_data(Radiosonde,Datalogger,'P')
    Datalogger['TR']=get_rs_data(Radiosonde,Datalogger,'T')
    Datalogger['Speed']=get_rs_data(Radiosonde,Datalogger,'Speed')
    Datalogger['Alt']=get_rs_data(Radiosonde,Datalogger,'Height')
    Datalogger['Lat']=get_rs_data(Radiosonde,Datalogger,'Lat')
    Datalogger['Lon']=get_rs_data(Radiosonde,Datalogger,'Lon')
    Datalogger['Theta']=theta(Datalogger['TR'],Datalogger['PR'])
    Datalogger['RH']=get_rs_data(Radiosonde,Datalogger,'RH')
    return Datalogger 

def process_met_data(datalogger_file,radiosonde_file):
    Pmax_set,Pump_time_set,Datalogger=import_logger(datalogger_file)
    Radiosonde,Flight_date,RS_type,Launch_Lat,Launch_Lon,Launch_Alt=import_sonde(radiosonde_file)
    interval=clip_datalogger(Datalogger,Radiosonde)
    Datalogger=Datalogger[interval[0]:interval[-1]]
    Datalogger=fetch_rs_at_dl(Datalogger,Radiosonde)
    start,stop=sampling_interval(Datalogger,Pump_time_set,Sampling_start,Sampling_stop)
    Datalogger['Weights'], Datalogger['SampleFlag'], avep,fig,ofsets=get_weights(Datalogger,start,stop)
    df=make_data(start,stop,Datalogger,avep,ofsets)
    filename_str='''
Flight info\n 
Launch Time: {0} UTC\n
Launch latitude: {1} N \n
Launch longitude: {2} E \n
Launch Altitude: {3} m \n
Radiosonde: {4}\n
Datalogger: LISA-DLV1\n
end Flight info\n
'''.format(Flight_date,Launch_Lat,Launch_Lon,Launch_Alt,RS_type)
    return Radiosonde,Datalogger,filename_str,df,fig,ofsets
