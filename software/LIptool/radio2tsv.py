#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import pandas as pd
import sys
import numpy as np
#
#
# Utility to convert radiosonde files into a certain format
#
#

desired_keys=['time', 'Pscl', 'T', 'RH', 'v', 'u', 'Height', 'P', 'TD',
       'MR', 'DD', 'FF', 'AZ', 'El', 'Range', 'Lon', 'Lat', 'SpuKey',
       'UsrKey', 'RadarH']


fil_value=-32768.00
wd=os.getcwd().split('/')
for element in wd:
    if '_Sampler_flight' in element:
        date=element.split('_Sampler_flight')[0].replace('_','-')
Headerstring='''
Converted from imet to match Vaisala RS format

Information about sounding:
==================================

Ignore: Station:                  xxxx
Ignore: Launch time:              {0}
Ignore: RS type:                  {rstype}
Ignore: RS number:                
Ignore: Reason for termination:   Manual stop
Ignore: Sounding SW version:      MW31 3.66.0

Ignore: PTU calculations in research mode

==================================


Information about map: FLEDT               
==================================


   Record name:    Unit:           Data type:          Divisor: Offset:
   ---------------------------------------------------------------------
    time            sec             float (4)          1        0       
    Pscl            ln scaled       float (4)          1        0       
    T               K               float (4)          1        0       
    RH              %               float (4)          1        0       
    v               m/s             float (4)          -1       0       
    u               m/s             float (4)          -1       0       
    Height          m               float (4)          1        0       
    P               hPa             float (4)          1        0       
    TD              K               float (4)          1        0       
    MR              g/kg            float (4)          1        0       
    DD              dgr             float (4)          1        0       
    FF              m/s             float (4)          1        0       
    AZ              dgr             float (4)          1        0       
    El              dgr             float (4)          1        0       
    Range           m               float (4)          1        0       
    Lon             dgr             float (4)          1        0       
    Lat             dgr             float (4)          1        0       
    SpuKey          bitfield        unsigned short (2) 1        0       
    UsrKey          bitfield        unsigned short (2) 1        0       
    RadarH          m               float (4)          1        0       

*************************************************************************************************\n'''.format('{}',rstype=sys.argv[1])

filename=sys.argv[-1]
#Datalogger=pd.read_csv('20180619.csv',delimiter=' *, *', engine='python',index_col=False)
#size=len(data) 
# Iniitalize new dataframe
if sys.argv[1]=='imet':
    index=0
    for line in open(filename):
       index+=1 
    index=index/2
    
    new=pd.DataFrame(index=[i for i in range(0,index)],columns=desired_keys)
    new=new.fillna(fil_value)
    u=0
    for line in open(filename):
        data=line.split(' ',1)
        
        if data[0]=='GPS:':
            try:
                dat=data[1].split(',')
                new.loc[u,'Lat']=float(dat[0])
                new.loc[u,'Lon']=float(dat[1])
                new.loc[u,'Height']=float(dat[2])
                new.loc[u,'time']=dat[4].split('\r')[0]
            except IndexError:
                pass
            u+=1
        if data[0]=='PTUX:':
            try:    
                dat=data[1].split(',')
                new.loc[u,'P']=float(dat[0])#+1.17 #Pressure is 1.67 mbar higher in Radiosonde
                new.loc[u,'T']=float(dat[1])+273.15
                new.loc[u,'RH']=float(dat[2])
            except IndexError:
                pass 
    
    date+=new['time'][0]       #original was: 13:22:45 should we shift? lets wait and see. 
    print(date)
    date+=' UTC'
    
    new.loc[:,'time']=np.array([float(i) for i in range(0,index)])#32 #since imet is shifted by 32 s
    #%%
    

elif sys.argv[1]=='m10':
    data=pd.read_csv(filename,sep=' ')
    date=data['Date'][0]
    index=len(data)
    new=pd.DataFrame(index=[i for i in range(0,index)],columns=desired_keys)
    new=new.fillna(fil_value)
     
    new.loc[:,'Lat']=data['Lat']
    new.loc[:,'Lon']=data['Lon']
    new.loc[:,'Height']=data['Alt']
    total_seconds=[int(data['Time'][i].split(':')[0])*3600+int(data['Time'][i].split(':')[1])*60+int(data['Time'][i].split(':')[2]) for i in range(0,index)]
    new.loc[:,'time']=np.array(total_seconds)-total_seconds[0]
    new.loc[:,'P']=data['P']
    new.loc[:,'T']=data['T']+273.15
    new.loc[:,'RH']=data['RH']
    md=np.deg2rad(270-data['WindDir'])
    new.loc[:,'v']=data['WindSpeed']*np.sin(md)
    new.loc[:,'u']=data['WindSpeed']*np.cos(md)
    date+=' '+data['Time'][0]       #original was: 13:22:45 should we shift? lets wait and see. 
    print(date)
    date+=' UTC'
    
with open('RS{}.tsv'.format(date.split(' ')[0].replace('-','')),'w') as fobj:
    fobj.write(Headerstring.format(date))
    new.to_csv(fobj,'\t',index=False)
    fobj.close()
