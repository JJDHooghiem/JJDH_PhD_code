# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 11:09:42 2017

@author: Joram
"""

#%%
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import csv
import pandas as pd

#==============================================================================
# Load the data:
#==============================================================================
#%%
data40=pd.read_csv('/Users/Joram/Documents/Data/40 Torr coef/40 Torr/CFKBDS2102-20170221-104423Z-DataLog_User.dat',sep='\s+',dtype=None)   
data40.index=pd.to_datetime(data40['DATE']+' '+data40['TIME'],format='%Y-%m-%d %H:%M:%S.%f')   
#%%
data140=pd.read_csv('/Users/Joram/Documents/Data/40 Torr coef/140 Torr/CFKBDS2102-20170220-102444Z-DataLog_User.dat',sep='\s+',dtype=None)   
data140.index=pd.to_datetime(data140['DATE']+' '+data140['TIME'],format='%Y-%m-%d %H:%M:%S.%f')   
#%%
#==============================================================================
# Definitions and functions.
#==============================================================================
#%%
def cavitycutoff(pcutoff,tcutoff,data):
    pcutoff=pcutoff 
    tcutoff=tcutoff
    data['CO2_cor']= [np.nan if abs(data['CavityPressure'][i]-140)>pcutoff or abs(data['CavityTemp'][i]-45)>tcutoff else data['CO2_cor'][i] for i in range(0,len(data['CavityPressure']))  ]  
    data['CH4_cor']= [np.nan if abs(data['CavityPressure'][i]-140)>pcutoff or abs(data['CavityTemp'][i]-45)>tcutoff else data['CH4_cor'][i] for i in range(0,len(data['CavityPressure']))  ]
 #   data['CO2_cor']= [np.nan if abs(data['CavityPressure'][i]-140)>pcutoff or abs(data['CavityTemp'][i]-45)>tcutoff else data['CO'][i] for i in range(0,len(data['CavityPressure']))  ]
#    for i in range(0,len(data['CavityPressure'])):
#        if abs(data['CavityPressure'][i]-140)>pcutoff or abs(data['CavityTemp'][i]-45)>tcutoff:
#            data['CO2_cor'][i]=np.nan
#            data['CH4_cor'][i]=np.nan
    return  
    
    
def datacorrect(data):
    data=data
    data['CO2_cor']=co2cavcor(data)
    data['CO2_cor']=co2vcor(data)    
    data['CH4_cor']=ch4cavcor(data)
    data['CH4_cor']=ch4vcor(data) 
    return 'data corrected'

def co2vcor(data):
    a=-0.0124404
    b=-0.0000303
    try:
        H2OREP=data['h2o_reported']
        CO2raw=data['CO2_cor']
        CO2dry=CO2raw/(1+a*H2OREP+b*H2OREP**2)
    except KeyError:       
        H2OREP=data['h2o_reported']
        CO2raw=data['CO2']
        CO2dry=CO2raw/(1+a*H2OREP+b*H2OREP**2)
    return CO2dry
    
  
def ch4vcor(data): 
    a=-0.010575
    b=0.000165
    try:    
        H2OREP=data['h2o_reported']
        CH4raw=data['CH4_cor']
        CH4dry=CH4raw/(1+a*H2OREP+b*H2OREP**2)
    except KeyError:    
        H2OREP=data['h2o_reported']
        CH4raw=data['CH4']
        CH4dry=CH4raw/(1+a*H2OREP+b*H2OREP**2)    
    return CH4dry
    
    


def co2cavcor(data):
    try:    
        CO2cor=data['CO2_cor']-0.471*(data['CavityPressure']-140)
    except KeyError:   
        CO2cor=data['CO2']-0.471*(data['CavityPressure']-140)
    return CO2cor
    

def ch4cavcor(data):
    try:    
        CH4cor=data['CH4_cor']-(8.09*(data['CavityPressure']-140)/1000)
    except KeyError:   
        CH4cor=data['CH4']-(8.09*(data['CavityPressure']-140)/1000)
    return CH4cor
    
def intervalmean40(start,stop,data):
    a,b=intervalmatch(start,stop,data)
    
    co2=np.nanmean(data['CO2'][a:b])
    co2s=np.nanstd(data['CO2'][a:b])

    ch4=np.nanmean(data['CH4'][a:b])*1000
    ch4s=np.nanstd(data['CH4'][a:b])*1000

    co=np.nanmean(data['CO'][a:b])*1000
    cos=np.nanstd(data['CO'][a:b])*1000

    h2o=np.nanmean(data['H2O'][a:b])
    h2os=np.nanstd(data['H2O'][a:b])
    return co2, co2s, ch4, ch4s,co,cos,h2o,h2os
    

    
def intervalmean40(start,stop,data):
    a,b=intervalmatch(start,stop,data)
    
    co2=np.nanmean(data['CO2'][a:b])
    co2s=np.nanstd(data['CO2'][a:b])

    ch4=np.nanmean(data['CH4'][a:b])*1000
    ch4s=np.nanstd(data['CH4'][a:b])*1000

    co=np.nanmean(data['CO'][a:b])*1000
    cos=np.nanstd(data['CO'][a:b])*1000

    h2o=np.nanmean(data['H2O'][a:b])
    h2os=np.nanstd(data['H2O'][a:b])
    return co2, co2s, ch4, ch4s,co,cos,h2o,h2os
    
def intervalmean(start,stop,data):
    a,b=intervalmatch(start,stop,data)
    
    co2=np.nanmean(data['CO2_cor'][a:b])
    co2s=np.nanstd(data['CO2_cor'][a:b])

    ch4=np.nanmean(data['CH4_cor'][a:b])*1000
    ch4s=np.nanstd(data['CH4_cor'][a:b])*1000

    co=np.nanmean(data['CO'][a:b])*1000
    cos=np.nanstd(data['CO'][a:b])*1000

    h2o=np.nanmean(data['H2O'][a:b])
    h2os=np.nanstd(data['H2O'][a:b])
    return co2, co2s, ch4, ch4s,co,cos,h2o,h2os

def timetosec(data):
    m=len(data['TIME'])
    t=[]
    for j in range(0,m):
        s=data['TIME'][j].split(':')
        t.append(float(s[0])*3600+float(s[1])*60+float(s[2]))
    s=[]
    for j in range(0,len(t)):    
        s.append(t[j]-t[0])
    return s, t

def meanplot(start, stop, data, filename):

    time,t=timetosec(data)
    a,b=intervalmatch(start,stop,data)  
    mean=intervalmean(start,stop,data)
    f, axes_array=plt.subplots(5,sharex=True,sharey=False, figsize=(10,20))
    data=data
    time=np.array(time)/60.
    
    axes_array[0].plot(time,data['CO2_cor'])
    axes_array[0].plot(time[a:b],data['CO2_cor'][a:b],'r',linewidth=2)
    axes_array[1].plot(time,(data['CH4_cor']*1000))
    axes_array[1].plot(time[a:b],(data['CH4_cor'][a:b])*1000,'r',linewidth=2)
    axes_array[2].plot(time,(data['CO']*1000))
    axes_array[2].plot(time[a:b],(data['CO'][a:b]*1000),'r',linewidth=2)
    axes_array[3].plot(time,data['H2O'])
    axes_array[3].plot(time[a:b],data['H2O'][a:b],'r',linewidth=2)  
        
    axes_array[4].plot(time,data['CavityPressure'])
    axes_array[4].plot(time[a:b],data['CavityPressure'][a:b],'r',linewidth=2)  
        
    
    axes_array[0].set_ylabel('CO$_2$ (ppm)')
    axes_array[1].set_ylabel('CH$_4$(ppb)')
    axes_array[2].set_ylabel('CO(ppb)')
    axes_array[3].set_ylabel('H$_2$O(%)') 
    axes_array[4].set_ylabel('Cavity Pressure (Torr)')
    axes_array[4].set_xlabel('time (min)')
        
    s=filename.split('/')
    d=s[-2]
    t1='Time: '+data['TIME'][a]+', Date: '+data['DATE'][0]
    t2='Time: '+data['TIME'][b]+', Date: '+data['DATE'][-1]
    
    
    axes_array[0].set_title('Mean CO$_2$: {0}$\pm${1}'.format(mean[0],mean[1]))
    axes_array[1].set_title('Mean CH$_4$: {0}$\pm${1}'.format(mean[2],mean[3]))
    axes_array[2].set_title('Mean CO: {0}$\pm${1}'.format(mean[4],mean[5]))
    axes_array[3].set_title('Mean H$_2$O: {0}$\pm${1}'.format(mean[6],mean[7]))
    f.suptitle('Processed data {0}\nStart red interval: {1}\nEnd red interval: {2}\n Mean values and standard deviation correspond to red interval'.format(d,t1,t2),fontsize=14)
    return f

def intervalmatch(minutes,duration,data):
    t, time=timetosec(data)
    a=minutes*60
    b=a+duration*60
    match=[]
    for i in range(0,len(data['TIME'])):    
        if t[i]>=a and t[i]<=b:
            match.append(i)
    return match[0],match[-1]
#%%
#==============================================================================
# 40 Torr analysis
#==============================================================================
os.chdir('/Users/Joram/Documents/Data/40 Torr coef/40 Torr/')
#%%

 

#%%
pcutoff=0.5
tcutoff=0.5
for i in range(0,len(data40['CavityPressure'])):
    if abs(data40['CavityPressure'][i]-40)>pcutoff or abs(data40['CavityTemp'][i]-45)>tcutoff:
        data40['CO2'][i]=np.nan
        data40['CH4'][i]=np.nan
        data40['CO'][i]=np.nan
#%%
time,t=timetosec(data40)
start=np.array([12,42,72,27,57,87])
stop=3
f, axes_array=plt.subplots(5,sharex=True,sharey=False, figsize=(10,20))
time1=np.array(time)/60.
mean=[]
axes_array[0].plot(time1,data40['CO2'])
axes_array[1].plot(time1,(data40['CH4']))
axes_array[2].plot(time1,(data40['CO']))
axes_array[3].plot(time1,data40['H2O'])
axes_array[4].plot(time1,data40['CavityPressure'])
for i in range(0,len(start)):
    a,b=intervalmatch(start[i],stop,data40)  
    mean.append(intervalmean40(start[i],stop,data40))
    axes_array[0].plot(time1[a:b],data40['CO2'][a:b],'r',linewidth=2)
    axes_array[1].plot(time1[a:b],(data40['CH4'][a:b]),'r',linewidth=2)
    axes_array[2].plot(time1[a:b],(data40['CO'][a:b]),'r',linewidth=2)
    axes_array[3].plot(time1[a:b],data40['H2O'][a:b],'r',linewidth=2)      
    axes_array[4].plot(time1[a:b],data40['CavityPressure'][a:b],'r',linewidth=2)  
    

axes_array[0].set_ylabel('CO$_2$ (ppm)')
axes_array[1].set_ylabel('CH$_4$(ppb)')
axes_array[2].set_ylabel('CO(ppb)')
axes_array[3].set_ylabel('H$_2$O(%)') 
axes_array[4].set_ylabel('Cavity Pressure (Torr)')
axes_array[4].set_xlabel('time (min)')

#%%
#==============================================================================
# Get mean values
#==============================================================================
hCO2_40=np.mean([mean[i][0] for i in range(0,3)])
hCH4_40=np.mean([mean[i][2] for i in range(0,3)])
hCO_40=np.mean([mean[i][4] for i in range(0,3)])
lCO2_40=np.mean([mean[i][0] for i in range(3,6)])
lCH4_40=np.mean([mean[i][2] for i in range(3,6)])
lCO_40=np.mean([mean[i][4] for i in range(3,6)])


#%%
#==============================================================================
#Coeff from old vilde a,b co2, d,e methane, e,f co 
#==============================================================================
a=1.118066358
b=-0.475159857
c=0.989641716
d=0
e=0.8738
f=0
#%%    
hCO2raw=(hCO2_40-b)/a
lCO2raw=(lCO2_40-b)/a

hCH4raw=((hCH4_40/1000)-d)/c
lCH4raw=((lCH4_40/1000)-d)/c

hCOraw=((hCO_40/1000)-f)/e
lCOraw=((lCO_40/1000)-f)/e
#%%

#==============================================================================
# 140 torr analysis. 
#==============================================================================
os.chdir('/Users/Joram/Documents/Data/40 Torr coef/140 Torr/')

#%%

datacorrect(data140)
#%%
time,t=timetosec(data140)
start=np.array([12,22,32,7,17,27])
stop=2
f, axes_array=plt.subplots(5,sharex=True,sharey=False, figsize=(10,20))
time1=np.array(time)/60.
mean140=[]
axes_array[0].plot(time1,data140['CO2_cor'])
axes_array[1].plot(time1,(data140['CH4_cor']))
axes_array[2].plot(time1,(data140['CO']))
axes_array[3].plot(time1,data140['H2O'])
axes_array[4].plot(time1,data140['CavityPressure'])
for i in range(0,len(start)):
    a,b=intervalmatch(start[i],stop,data140)  
    mean140.append(intervalmean(start[i],stop,data140))
    axes_array[0].plot(time1[a:b],data140['CO2_cor'][a:b],'r',linewidth=2)
    axes_array[1].plot(time1[a:b],(data140['CH4_cor'][a:b]),'r',linewidth=2)
    axes_array[2].plot(time1[a:b],(data140['CO'][a:b]),'r',linewidth=2)
    axes_array[3].plot(time1[a:b],data140['H2O'][a:b],'r',linewidth=2)      
    axes_array[4].plot(time1[a:b],data140['CavityPressure'][a:b],'r',linewidth=2)  
    

axes_array[0].set_ylabel('CO$_2$ (ppm)')
axes_array[1].set_ylabel('CH$_4$(ppb)')
axes_array[2].set_ylabel('CO(ppb)')
axes_array[3].set_ylabel('H$_2$O(%)') 
axes_array[4].set_ylabel('Cavity Pressure (Torr)')
axes_array[4].set_xlabel('time (min)')

#%%
#==============================================================================
# Get mean values
#==============================================================================
hCO2_140=np.mean([mean140[i][0] for i in range(0,3)])
hCH4_140=np.mean([mean140[i][2] for i in range(0,3)])/1000
hCO_140=np.mean([mean140[i][4] for i in range(0,3)])/1000
lCO2_140=np.mean([mean140[i][0] for i in range(3,6)])
lCH4_140=np.mean([mean140[i][2] for i in range(3,6)])/1000
lCO_140=np.mean([mean140[i][4] for i in range(3,6)])/1000
#%%
a_new=(hCO2_140-lCO2_140)/(hCO2raw-lCO2raw)
b_new=hCO2_140-hCO2raw*a_new
b_newc=lCO2_140-lCO2raw*a_new
c_new=(hCH4_140-lCH4_140)/(hCH4raw-lCH4raw)
d_new=hCH4_140-hCH4raw*c_new
d_newc=lCH4_140-lCH4raw*c_new
e_new=(hCO_140-lCO_140)/(hCOraw-lCOraw)
f_new=hCO_140-hCOraw*e_new
f_newc=lCO_140-lCOraw*e_new
#%%
data40['CO2_raw']=(data40['CO2']-b)/a
data40['CO2_new']=data40['CO2_raw']*a_new+b_new