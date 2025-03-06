#/usr/bin/env python
# -*- encoding: utf-8 -*-
import pandas as pd
import Barometric 
import matplotlib.pyplot as plt
import numpy as np
from glob import glob
radiosonde = glob('/home/joram/research/data/LISA_Measurements/*Sampler_flight/Radiosonde/FLEDT*.tsv') #skiprows=48
data={}
for f in radiosonde:
    df1 = pd.read_csv(f,sep='\t',names=['Time', 'Pscl', 'Temperature', 'RH', 'Velocity', 'u', 'Height', 'Pressure', 'TD', 'MR', 'DD', 'FF', 'AZ', 'EI', 'Range', 'Lon', 'Lat', 'SpuKey', 'UsrKey', 'RadarH', 'Unnamed: 20'],skiprows=48)
    print(f)
    df1 = df1.replace(-32768.00, np.nan)
    df1 = df1.dropna(subset = ['RH', 'Pressure', 'Temperature', 'Lat', 'Height'])
    data[f] = df1
for dat in data:
    d=data[dat]
    d['Gamma']=Barometric.GammaFromZ(d["Height"],d["Lat"]  )
    d['Geopot']=Barometric.heigth_to_geopotH(d["Height"],d["Lat"])
    print(d['Geopot'][0])
    print(d['Temperature'][0])
    print(d['RH'][0])
    print(d['Height'][0])
    print(d['Lat'][0])
    d["Pcalc"]=Barometric.barometric_p(np.array(d['Temperature']),np.array(d['RH']),np.array(d['Geopot'])),float(d['Pressure'][0]*100))
    top=d['Height'].idxmax()
    plt.plot(d['Pressure'][:top]-d['Pcalc'][:top],d['Height'][:top])
plt.show()
