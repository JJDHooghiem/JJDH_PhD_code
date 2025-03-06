# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 13:28:41 2017

@author: Joram
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Jun 29 13:59:58 2016

@author: Joram Hooghiem, Huilin Chen, Bert Scheeren
"""
#==============================================================================
# Script for appling watervapor corrections and linear calibration based on icos values from 2016 ask Bert Scheeren about green deal picaroo
### Calibrations functions according to ICOS calibration of picarro. Conform ICOS. Calibration was done in paris spring 2016 for icos purposes
### Functions obtained from 
#%%
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import csv
import pandas as pd
#%%

def time_stamp(data):
    data.index=pd.to_datetime(data['DATE']+' '+data['TIME'],format='%Y-%m-%d %H:%M:%S.%f')  
    timetosec(data)
    return
#%%
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


#%%

def co2vcor(data):
    a=-0.01216
    b=-0.0002165
    H2OREP=data['h2o_reported']
    CO2raw=data['CO2_raw']
    CO2dry=CO2raw/(1+a*H2OREP+b*H2OREP**2)
    return CO2dry
    
#%%    
def ch4vcor(data): 
    a=-0.01043
    b=0.00006975  
    H2OREP=data['h2o_reported']
    CH4raw=data['CH4_raw']
    CH4dry=CH4raw/(1+a*H2OREP+b*H2OREP**2)    
    return CH4dry
    
#%%
def covcor(data):
    a,b,c=0.000278, -0.03069, 0.004945
    data["deltaCO"]= a + b*data["b_h2o_pct"] + c*data["b_h2o_pct"]**2 
    CO_cor=(data["CO_raw"]-data["deltaCO"])/(1-0.0124*data["h2o_reported"]-0.0006*data["h2o_reported"]**2)
    return CO_cor 
#%%

def co2cavcor(data):
    CO2raw=data['CO2']-0.471*(data['CavityPressure']-140)
    return CO2raw
    
#%%
def ch4cavcor(data):   
    CH4raw=data['CH4']-(8.09*(data['CavityPressure']-140)/1000)
    return CH4raw
#%%
         
def co2cal(data,co2drift=0):
    CO2cal=((data['CO2_cor']*1.006107)+0.383767)+co2drift
    return CO2cal
    
def ch4cal(data,ch4drift=0):
    CH4Cal=((data['CH4_cor']*1.001572)+1.154117)+ch4drift
    return CH4Cal

def cocal(data,codrift=0):
    COcal=((data['CO_cor']*0.985814)+3.243767)+codrift
    return COcal 

#%%
def cavitycutoff(pcutoff,tcutoff,data):
   data['CO2']=[np.nan if abs(data['CavityPressure'][i]-140)>pcutoff or abs(data['CavityTemp'][i]-45)>tcutoff else data['CO2'][i] for i in range(0,len(data['CavityPressure']))]
   data['CH4']=[np.nan if abs(data['CavityPressure'][i]-140)>pcutoff or abs(data['CavityTemp'][i]-45)>tcutoff else data['CH4'][i] for i in range(0,len(data['CavityPressure']))]
   data['peak84_raw']=[np.nan if abs(data['CavityPressure'][i]-140)>pcutoff or abs(data['CavityTemp'][i]-45)>tcutoff else data['peak84_raw'][i] for i in range(0,len(data['CavityPressure']))]  
   return    
#%%
def removefill(data):
   data["CO2"]=[data["CO2"][i] if data["species"][i]==1 else np.nan for i in xrange(len(data["CO2"]))]     
   data['peak84_raw']=[data['peak84_raw'][i] if data["species"][i]==4 else np.nan for i in xrange(len(data["CO"]))] 
   data["CH4"]=[data["CH4"][i] if data["species"][i]==2 else np.nan for i in xrange(len(data["CH4"]))] 
   return
#%%
def datacorrect(data,pcutoff,tcutoff,co2drift=0,ch4drift=0,codrift=0):
    data=data
    removefill(data)
    time_stamp(data)
    timetosec(data)
    cavitycutoff(pcutoff,tcutoff,data)
    
    data['CO2_raw']=co2cavcor(data)
    data['CH4_raw']=ch4cavcor(data)*1000
    data['CO_raw']=data['peak84_raw']*0.427*1000
    
    data['CO2_cor']=co2vcor(data)    
    data['CH4_cor']=ch4vcor(data) 
    data['CO_cor']=covcor(data)
    
    data['CO2_cor']=co2cal(data,co2drift)
    data['CH4_cor']=ch4cal(data,ch4drift)
    data['CO_cor']=cocal(data,codrift)
    
    return 'data corrected'
 
 #%%
 
#==============================================================================
#  Plotting tools below
#==============================================================================









 
#%%    
def intervalmatch(minutes,duration,data):
    a=minutes*60
    b=a+duration*60
    match=[]
    for i in range(0,len(data['RelTime'])):    
        if data['RelTime'][i]>=a and data['RelTime'][i]<=b:
            match.append(i)
    return match[0],match[-1]
#%%
def meanplot(start, stop, data, filename):
    a,b=intervalmatch(start,stop,data)  
    mean=intervalmean(start,stop,data)
    f, axes_array=plt.subplots(5,sharex=True,sharey=False, figsize=(10,20))
   
  
    
    axes_array[0].plot(data["RelTime"][np.isfinite(data['CO2_cor'])]/60,data['CO2_cor'][np.isfinite(data['CO2_cor'])])
    axes_array[0].plot(data["RelTime"][a:b][np.isfinite(data['CO2_cor'])]/60,data['CO2_cor'][a:b][np.isfinite(data['CO2_cor'])],'r',linewidth=2)
    
    axes_array[1].plot(data["RelTime"][np.isfinite(data['CH4_cor'])]/60,(data['CH4_cor'][np.isfinite(data['CH4_cor'])]))
    axes_array[1].plot(data["RelTime"][a:b][np.isfinite(data['CH4_cor'])]/60,(data['CH4_cor'][a:b][np.isfinite(data['CH4_cor'])]),'r',linewidth=2)
    
    axes_array[2].plot(data["RelTime"][np.isfinite(data['CO_cor'])]/60,(data['CO_cor'][np.isfinite(data['CO_cor'])]))
    axes_array[2].plot(data["RelTime"][a:b][np.isfinite(data['CO_cor'])]/60,(data['CO_cor'][a:b][np.isfinite(data['CO_cor'])]),'r',linewidth=2)
    
    axes_array[3].plot(data["RelTime"]/60,data['H2O'])
    axes_array[3].plot(data["RelTime"][a:b]/60,data['H2O'][a:b],'r',linewidth=2)  
        
    axes_array[4].plot(data["RelTime"]/60,data['CavityPressure'])
    axes_array[4].plot(data["RelTime"][a:b]/60,data['CavityPressure'][a:b],'r',linewidth=2)  
    
    
    axes_array[0].set_ylabel('CO$_2$ (ppm)')
    axes_array[1].set_ylabel('CH$_4$(ppb)')
    axes_array[2].set_ylabel('CO(ppb)')
    axes_array[3].set_ylabel('H$_2$O(%)') 
    axes_array[4].set_ylabel('Cavity Pressure (Torr)')
    axes_array[4].set_xlabel('time (min)')
        
    
    d=filename
    t1=data.index[a]
    t2=data.index[b]
    
    
    axes_array[0].set_title('Mean CO$_2$: {0}$\pm${1}'.format(mean[0],mean[1]))
    axes_array[1].set_title('Mean CH$_4$: {0}$\pm${1}'.format(mean[2],mean[3]))
    axes_array[2].set_title('Mean CO: {0}$\pm${1}'.format(mean[4],mean[5]))
    axes_array[3].set_title('Mean H$_2$O: {0}$\pm${1}'.format(mean[6],mean[7]))
    f.suptitle('Processed data {0}\nStart red interval: {1}\nEnd red interval: {2}\n Mean values and standard deviation correspond to red interval'.format(d,t1,t2),fontsize=14)
    return f
    
#%%
    
    
    
    
    
def intervalplot(start, stop, data, filename,mean=True):
    a,b=intervalmatch(start,stop,data)  
    f, axes_array=plt.subplots(5,sharex=True,sharey=False, figsize=(10,20))
    axes_array[0].plot(data["RelTime"][a:b][np.isfinite(data['CO2_cor'])]/60,data['CO2_cor'][a:b][np.isfinite(data['CO2_cor'])],'r',linewidth=2)
    axes_array[1].plot(data["RelTime"][a:b][np.isfinite(data['CH4_cor'])]/60,(data['CH4_cor'][a:b][np.isfinite(data['CH4_cor'])]),'r',linewidth=2)
    axes_array[2].plot(data["RelTime"][a:b][np.isfinite(data['CO_cor'])]/60,(data['CO_cor'][a:b][np.isfinite(data['CO_cor'])]),'r',linewidth=2)
    axes_array[3].plot(data["RelTime"][a:b]/60,data['H2O'][a:b],'r',linewidth=2)  
        

    axes_array[4].plot(data["RelTime"][a:b]/60,data['CavityPressure'][a:b],'r',linewidth=2)  
        
    
    axes_array[0].set_ylabel('CO$_2$ (ppm)')
    axes_array[1].set_ylabel('CH$_4$(ppb)')
    axes_array[2].set_ylabel('CO(ppb)')
    axes_array[3].set_ylabel('H$_2$O(%)') 
    axes_array[4].set_ylabel('Cavity Pressure (Torr)')
    axes_array[4].set_xlabel('time (min)')
        
    
    d=filename
    t1=data.index[a]
    t2=data.index[b]
    if mean==True:
        mean=intervalmean(start,stop,data)
        axes_array[0].set_title('Mean CO$_2$: {0}$\pm${1}'.format(mean[0],mean[1]))
        axes_array[1].set_title('Mean CH$_4$: {0}$\pm${1}'.format(mean[2],mean[3]))
        axes_array[2].set_title('Mean CO: {0}$\pm${1}'.format(mean[4],mean[5]))
        axes_array[3].set_title('Mean H$_2$O: {0}$\pm${1}'.format(mean[6],mean[7]))
    
    f.suptitle('Processed data {0}\nData Starts: {1}\nData ends: {2}'.format(d,t1,t2),fontsize=14)
    return f
#%%
def intervalmean(start,stop,data):
    a,b=intervalmatch(start,stop,data)
    
    co2=np.nanmean(data['CO2_cor'][a:b])
    co2s=np.nanstd(data['CO2_cor'][a:b])

    ch4=np.nanmean(data['CH4_cor'][a:b])
    ch4s=np.nanstd(data['CH4_cor'][a:b])

    co=np.nanmean(data['CO_cor'][a:b])
    cos=np.nanstd(data['CO_cor'][a:b])

    h2o=np.nanmean(data['H2O'][a:b])
    h2os=np.nanstd(data['H2O'][a:b])
    return co2, co2s, ch4, ch4s,co,cos,h2o,h2os

    
#%%
def meantxt(outfile,mean):    
    filename=outfile+'.csv'
    mean=mean
    l=('CO2(ppm)', 'CO2 std(ppm)','CH4(ppb)','CH4 std(ppb)','CO(ppb)','CO std(ppb)','H2O','H20 std')  
    firstline=[]
    for i in range(0,len(l)):
        firstline.append(l[i]+'\t')
    s=",".join(firstline)
    secondline=[]
    for i in range(0,len(mean)):
        secondline.append(str(mean[i])+'\t')
    s2=",".join(secondline)    
    txt=open(filename, 'w') 
    txt.write(s+'\n')
    txt.write(s2+'\n')
    txt.close() 
    return 'data saved'


#%%
#%%
def qcplot(data,filename):
    f, axes_array=plt.subplots(4,sharex=True,sharey=False, figsize=(10,10))
    data=data
    s,t=timetosec(data)
    time=np.array(s)/60.
    axes_array[0].plot(time,data['CO2_dry'])
    axes_array[1].plot(time,(data['CH4_dry']*1000))
    axes_array[2].plot(time,(data['CO']*1000))
    axes_array[3].plot(time,data['H2O'])
        
    axes_array[0].set_ylabel('CO$_2$ (ppm)')
    axes_array[1].set_ylabel('CH$_4$(ppm)')
    axes_array[2].set_ylabel('CO(ppm)')
    axes_array[3].set_ylabel('H$_2$(%)') 
    axes_array[3].set_xlabel('time (min)')
        
    s=filename.split('/')
    d=s[-2]
    t1='Time: '+data['TIME'][0]+', Date: '+data['DATE'][0]
    t2='Time: '+data['TIME'][-1]+', Date: '+data['DATE'][-1]
    f.suptitle('quick plot: unprocessed data {0}\nStart: {1}\nEnd: {2}'.format(d,t1,t2),fontsize=14)
    return f, axes_array    
    
#%%
    
#%%
#==============================================================================
# Check tool if cavitycorrection is properly applied
#==============================================================================
#for i in range(0,len(data['CavityPressure'])):
#    if abs(data['CavityPressure'][i]-140)>0.5:
#        print(data['CO_cor'][i])
         