#/usr/bin/env python
# -*- coding: utf-8 -*-

# Define a dicionary containg flight info 
import TrainRadCore as TRC
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats
from statistics import NormalDist
def confidence_interval(data, confidence=0.95):
  dist = NormalDist.from_samples(data)
  z = NormalDist().inv_cdf((1 + confidence) / 2.)
  h = dist.stdev * z / ((len(data) - 1) ** .5)
  print(dist.stdev)
  return dist.mean - h, dist.mean + h


TrainData=TRC.LoadDataAll()
#TrainDataDelta={}
dT=np.array([])
dZ=np.array([])
dRH=np.array([])
a=np.array([])
t=np.array([])
for d in TrainData:
    data=TrainData[d]
    dat=TRC.processMet(data)
    dat['Alt'].iloc[:]=dat['Alt'].interpolate()
    i=data["Alt"].idxmax()
    j=dat["Alt"].idxmax()
    key='T'
    plt.plot(dat['time_s']-dat['time_s'][j],dat[key],'o')
    plt.plot(data['time_s']-data['time_s'][i],data[key],'*')
    plt.savefig('test.pdf')
    # dZ  =np.concatenate((dZ,dz))
    
    # b=np.diff(data['RH'])
    # dRH =np.concatenate((dRH,np.diff(data['RH'])))

#    delta={}
#    delta['dt']=a
#    delta['dT']=np.diff( data['T'])
#    delta['dZ']= np.diff(data['Alt'])
#    delta['dRH']=np.diff(data['RH'])
#    TrainDataDelta[d]=delta
# Reproducibility is 0.2 K
# plt.ylim(-2,2)
# bins=np.linspace(-10,10,201)
# sel=(a==1)&(np.abs(dT)>=0.1)
# print( confidence_interval(dT[sel],0.99999))
# m=np.mean(dT[sel])
# print(m)
# print(scipy.stats.norm.interval(0.95, loc=m, scale=scipy.stats.sem(dT[sel])))
# plt.hist(dRH[sel],bins=bins)
# plt.hist(dT,bins=bins)
# plt.ylim(0,10)
# plt.xlabel('$dT$ ' )
# plt.show()
# print(len(dT[(a==1)]))

