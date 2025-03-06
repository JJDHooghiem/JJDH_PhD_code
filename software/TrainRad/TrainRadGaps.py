#!/usr/bin/env python
import Barometric
import sys
import numpy as np
from glob import glob
import pandas as pd
import random
import scipy.stats as stats
import scantools 
fname=sys.argv[1]
#dataSet= glob('/home/joram/research/data/LISA_Measurements/*Sampler_flight/Radiosonde/FLEDT*.tsv')[0] #skiprows=48

dataSet = pd.read_csv(fname,sep='\t',names=['Time', 'Pscl', 'Temperature', 'RH', 'Velocity', 'u', 'Height', 'Pressure', 'TD', 'MR', 'DD', 'FF', 'AZ', 'EI', 'Range', 'Lon', 'Lat', 'SpuKey', 'UsrKey', 'RadarH', 'Unnamed: 20'],skiprows=48)
dataSet =dataSet.replace(-32768.00, np.nan)
dataSet =dataSet.dropna(subset = ['RH', 'Pressure', 'Temperature', 'Lat', 'Height'])
dataSet=dataSet.reset_index()
dataSet=dataSet[:dataSet['Height'].idxmax()+1]
dataSet['Gamma']=Barometric.GammaFromZ(dataSet["Height"],dataSet["Lat"])
P_benchmark=Barometric.barometric_p(np.array(dataSet['Temperature']),np.array(dataSet['RH']),np.array(dataSet['Height']),np.array(dataSet['Gamma']),float(dataSet['Pressure'][0]*100))
Ptop=P_benchmark[-1]
gapsizes=np.linspace(20,200,10)
results=np.array([None]*len(gapsizes))
a=np.linspace(0,9,10)
# for i in range(len(gapsizes)): 
for i in range(2): 
    # -1 because python starts at 0, extra -1, we don't want to sample the top so -2 appears below
    # start_index is start gap 
    start_index=range(0,len(dataSet)-2-int(gapsizes[i]))
    result=np.array([None]*len(start_index))
    for j in range(len(start_index)):
        index=start_index[j]
        drops=range(index,index+int(gapsizes[i]))
        dat=dataSet.drop(drops)
        P=Barometric.barometric_p(np.array(dat['Temperature']),np.array(dat['RH']),np.array(dat['Height']),np.array(dat['Gamma']),float(P_benchmark[0]*100))
        Ptopdat=P[-1]
        result[j]=Ptopdat-Ptop
    results[i]=result 
import matplotlib.pyplot as plt
means=[]
stdev=[]
for l,i in zip(results,range(len(gapsizes))):
    means.append(np.mean(l))
    stdev.append(np.std(l))
    x=np.repeat(gapsizes[i],len(l))
    plt.plot(x,l,'grey')
plt.errorbar(gapsizes,means,yerr=stdev)
regresult=stats.linregress(gapsizes,means)
ylab='d$p$ (hPa)'
xlab='gap size'
plt.suptitle(fname.split('/')[-1]+' slope %.2f offset %.2f\n $r^{2}$ %.2f' % (*regresult[:2],regresult[2]**2)) 
plt.ylabel(ylab)
plt.xlabel(xlab)
plt.savefig(fname.split('/')[-1].split('.')[0]+'.pdf')
plt.close() 

scantools.statplot(x,y,xlab,ylab,fname.split('/')[-1].split('.')[0])
    


#    d['Geopot']=Barometric.heigth_to_geopot(d["Height"],d["Lat"])
 #    print(d['Geopot'][0])
 #    print(d['Temperature'][0])
 #    print(d['RH'][0])
 #    print(d['Height'][0])
 #    print(d['Lat'][0])
 #    d["Pcalc"]=Barometric.get_P(np.array(d['Temperature']),np.array(d['RH']),np.array(d['Height']),np.array(d['Gamma']),float(d['Pressure'][0]*100))
 #    top=d['Height'].idxmax()
 #    plt.plot(d['Pressure'][:top]-d['Pcalc'][:top],d['Height'][:top])
# plt.show()
