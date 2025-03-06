"""
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
import os
import json
import pandas as pd
import numpy as np
from  calendar import timegm
import time
from scipy.interpolate import interp1d
from scipy.optimize import curve_fit
from scipy.stats import linregress
from glob import glob
import configparser

# Get Picarro type from name in data file set default config file
default_config='/home/joram/.local/src/python/Picarro/default_config.ini'

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
    co2_water_a       =pic_config.getfloat('vapour'      , 'co2_water_a')
    co2_water_b       =pic_config.getfloat('vapour'      , 'co2_water_b')

    H2OREP=data['h2o_reported']
    CO2raw=data['CO2_raw']
    CO2dry=CO2raw/(1+co2_water_a*H2OREP+co2_water_b       *H2OREP**2)
    return CO2dry

def ch4vcor(data):
    ch4_water_a       =pic_config.getfloat('vapour'      , 'ch4_water_a')
    ch4_water_b       =pic_config.getfloat('vapour'      , 'ch4_water_b')
    H2OREP=data['h2o_reported']
    CH4raw=data['CH4_raw']
    CH4dry=CH4raw/(1+ch4_water_a       *H2OREP+ch4_water_b       *H2OREP**2)
    return CH4dry


def co_cor_chen(data):
    '''
    Corrects for water vapour as described in Chen et al. 2013
    @Article 
    author	= {Chen, H. and Karion, A. and Rella, C. W. and Winderlich,
		  J. and Gerbig, C. and Filges, A. and Newberger, T. and
		  Sweeney, C. and Tans, P. P.},
    doi		= {10.5194/amt-6-1031-2013},
    journal	= {Atmospheric Measurement Techniques},
    number	= {4},
    pages		= {1031--1040},
    title		= {Accurate measurements of carbon monoxide in humid air
          	  using the cavity ring-down spectroscopy (CRDS) technique},
    volume	= {6},
    year		= {2013}
    }
    '''
    Dco_water_a       =pic_config.getfloat('vapour'      , 'Dco_water_a')
    Dco_water_b       =pic_config.getfloat('vapour'      , 'Dco_water_b')
    Dco_water_c       =pic_config.getfloat('vapour'      , 'Dco_water_c')
    Dco_water_d       =pic_config.getfloat('vapour'      , 'Dco_water_d')
    data["deltaCO"]= Dco_water_a       *data["b_h2o_pct"] + Dco_water_b*data["b_h2o_pct"]**2 + Dco_water_c*data["b_h2o_pct"]**3 + Dco_water_d*data["b_h2o_pct"]**4
    co_water_a        =pic_config.getfloat('vapour'      , 'co_water_a')
    co_water_b        =pic_config.getfloat('vapour'      , 'co_water_b')
    COcor=(data["CO_raw"]-data["deltaCO"])/(1+co_water_a*data['h2o_reported']+co_water_b*data['h2o_reported']**2)
    return COcor


# =============================================================================
# Pressure corrections
# =============================================================================

def co2cavcor(data):
    '''
    applies temperature and pressure correction
    '''
    co2_temp_a        =pic_config.getfloat('temperature'  , 'co2_temp_a')
    Cav_T_set         =pic_config.getfloat('temperature'  , 'Cav_T_set')
    CO2Tcor=data['CO2']+co2_temp_a        *(data['CavityTemp']-Cav_T_set         )
    
    co2_pres_a        =pic_config.getfloat('pressure'    , 'co2_pres_a')
    Cav_P_set         =pic_config.getfloat('pressure'    , 'Cav_P_set')
    CO2raw=CO2Tcor+co2_pres_a*(data['CavityPressure']-Cav_P_set         )
    return CO2raw

def ch4cavcor(data):
    '''
    applies temperature and pressure correction and converts to pbb
    '''
    ch4_temp_a        =pic_config.getfloat('temperature'  , 'ch4_temp_a')
    Cav_T_set         =pic_config.getfloat('temperature'  , 'Cav_T_set')
    CH4Tcor=1000.0*data['CH4']+ch4_temp_a        *(data['CavityTemp']-Cav_T_set         )

    ch4_pres_a        =pic_config.getfloat('pressure'    , 'ch4_pres_a')
    Cav_P_set         =pic_config.getfloat('pressure'    , 'Cav_P_set')
    CH4raw=CH4Tcor+ch4_pres_a        *(data['CavityPressure']-Cav_P_set         )
    return CH4raw


    
# =============================================================================
# Calibration
# =============================================================================

def co2cal(data,drift=0):
    co2_cal_a         =pic_config.getfloat('calibration' , 'co2_cal_a')
    co2_cal_b         =pic_config.getfloat('calibration' , 'co2_cal_b')
    data['CO2_uncal']=data['CO2_cor']
    CO2cor=((data['CO2_uncal']*co2_cal_a)+co2_cal_b)+drift
    return CO2cor

def ch4cal(data,drift=0):
    ch4_cal_a         =pic_config.getfloat('calibration' , 'ch4_cal_a')
    ch4_cal_b         =pic_config.getfloat('calibration' , 'ch4_cal_b')
    data['CH4_uncal']=data['CH4_cor']
    CH4cor=((data['CH4_uncal']*ch4_cal_a)+ch4_cal_b)+drift
    return CH4cor

def cocal(data,drift=0):
    co_cal_a          =pic_config.getfloat('calibration' , 'co_cal_a')
    co_cal_b          =pic_config.getfloat('calibration' , 'co_cal_b')
    data['CO_uncal']=data['CO_cor']
    COcor=((data['CO_uncal']*co_cal_a)+co_cal_b)+drift
    return COcor

def co_cor_icos(data):
    '''
    as in icos calibration
all$COw <- (calib["co_conc_intercept",] + calib["co_conc_slope",]* (all$Peak84 + calib["co_offset",] + (calib["co_water_linear",] * all$H2O_co) + (calib["co_water_quadratic",]* all$H2O_co^2) + (calib["co_water_co2",] * all$H2O_co * ((calib["co2_conc_slope",]*all$Peak14)+calib["co2_conc_intercept",])) + (calib["co_co2_linear",] * ((calib["co2_conc_slope",]*all$Peak14)+calib["co2_conc_intercept",]))))*1000
all$COdryLSCE <- all$COw/(calib["co_wd_quadratic",]*(all$H2Or)^2 + calib["co_wd_linear",]*(all$H2Or) + 1)
    '''

    co_conc_intercept =pic_config.getfloat('calibration' , 'co_conc_intercept')
    co_conc_slope     =pic_config.getfloat('calibration' , 'co_conc_slope')
    co_offset         =pic_config.getfloat('calibration' , 'co_offset')
    co_water_linear   =pic_config.getfloat('vapour'      , 'co_water_linear')
    co_water_quadratic=pic_config.getfloat('vapour'      , 'co_water_quadratic')
    co_water_co2      =pic_config.getfloat('vapour'      , 'co_water_co2')
    co2_conc_slope    =pic_config.getfloat('calibration' , 'co2_conc_slope')
    co2_conc_intercept=pic_config.getfloat('calibration' , 'co2_conc_intercept')
    co_co2_linear     =pic_config.getfloat('calibration' , 'co_co2_linear')

    CO_wet=(co_conc_intercept+co_conc_slope*(data['peak84_raw']+co_offset+(co_water_linear*data['b_h2o_pct'])+(co_water_quadratic*data['b_h2o_pct']**2)+(co_water_co2*data['b_h2o_pct']*((co2_conc_slope*data['peak_14'])+co2_conc_intercept))+(co_co2_linear*((co2_conc_slope*data['peak_14'])+co2_conc_intercept))))*1000

    co_wd_quadratic   =pic_config.getfloat('vapour'      , 'co_wd_quadratic')
    co_wd_linear      =pic_config.getfloat('vapour'      , 'co_wd_linear')

    CO_dry=CO_wet/(co_wd_quadratic*data['h2o_reported']**2 + co_wd_linear*data['h2o_reported'] + 1)
    #print(CO_dry
    return CO_dry

def cavitycutoff(data):

    Cav_P_set    =pic_config.getfloat('pressure','Cav_P_set')
    Cav_P_cutoff =pic_config.getfloat('pressure','Cav_P_cutoff')
    Cav_T_set    =pic_config.getfloat('temperature','Cav_T_set')
    Cav_T_cutoff =pic_config.getfloat('temperature','Cav_T_cutoff')

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


pic_config=configparser.ConfigParser()
pic_config.read(default_config)
print("reading default configuration which leaves data unaltered")  


def get_Picarro(Data_Picarro,interpolate=False,configfile=None):
    if not configfile==None:
        pic_config.read(configfile) 
        print("loaded custom config")
    print(pic_config['calibration']['co_cal_method'])
    if not isinstance(Data_Picarro,str):
        data=[pd.read_csv(dat_file,sep='\s+',dtype=None) for dat_file in Data_Picarro]

        data=pd.concat(data,axis=0)
        time_stamp(data)
        data=data.sort_index()
    else:
        data=pd.read_csv(Data_Picarro,sep='\s+',dtype=None)
        time_stamp(data)
    removefill(data)
    cavitycutoff(data)
    index=np.array(range(0,len(data['CO2'])))
    data['index']=index
    #Apply cavity correction and change units from ppm to ppb for ch4 and co
    data['CO2_raw']=co2cavcor(data)
    data['CH4_raw']=ch4cavcor(data)
    co_peak84_a=pic_config.getfloat('calibration','co_peak84_a')
    co_peak84_b=pic_config.getfloat('calibration','co_peak84_b')
    data['CO_raw']=(co_peak84_a*data['peak84_raw']+co_peak84_b)*1000
    #Interpolate water
    interpolator=interp1d(data['RelTime'][np.isfinite(data['h2o_reported'])],data['h2o_reported'][np.isfinite(data['h2o_reported'])],fill_value='extrapolate')
    data['h2o_reported']=interpolator(data['RelTime'])

    interpolator=interp1d(data['RelTime'][np.isfinite(data['H2O'])],data['H2O'][np.isfinite(data['H2O'])],fill_value='extrapolate')
    data['H2O']=interpolator(data['RelTime'])

    #apply vapor corrections
    data['CO2_cor']=co2vcor(data)
    data['CH4_cor']=ch4vcor(data)
    if pic_config['calibration']['co_cal_method']=='chen':
        data['CO_cor']=co_cor_chen(data)
    if pic_config['calibration']['co_cal_method']=='icos':
        data['CO_cor']=co_cor_icos(data)
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


def meanplot(start, stop, data, filename, whole=False,use_index=True,configfile=None):
    if not configfile==None:
        pic_config.read(configfile) 
        print("loaded custom config")
    print(pic_config['calibration']['co_cal_method'])
    import matplotlib.pyplot as plt
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
    
    Cav_P_set    =pic_config.getfloat('pressure','Cav_P_set')
    Cav_P_cutoff =pic_config.getfloat('pressure','Cav_P_cutoff')
    Cav_T_set    =pic_config.getfloat('temperature','Cav_T_set')
    Cav_T_cutoff =pic_config.getfloat('temperature','Cav_T_cutoff')

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
