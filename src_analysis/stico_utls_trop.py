#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Don't remove the line below, it is checked by "one to run them all"
# --otrta-p--
# extension p means parallel, s is for single
"""
This code was written for the analysis presented in the dissertation of Joram Jan Dirk Hooghiem
"""
from netCDF4 import Dataset
import config
import matplotlib.pyplot as plt
import numpy as np
data_CARIB=Dataset(config.DataDir+'/CO_stable_isotope_data/isoCO_C1_ext.nc')
bound=30
a=data_CARIB['strat_mask'][:]
b=data_CARIB['press'][:]
b[b.mask]=np.nan
a[a.mask]=1
mask=(data_CARIB['lat'][:]>-bound)&(data_CARIB['lat'][:]<bound)&(a==0)&(b<300)
# mask=(data_CARIB['strat_mask'][:]==)
time=data_CARIB['timeax'][mask]
time-=time[0]
time/=365
x=data_CARIB['d13co_ozc'][mask]
y=data_CARIB['d18co_ozc'][mask]
y=data_CARIB['co_ozc'][mask]
# Whatever we find here is going to be a mix of CH4 + (wildfire + fossil fuel + nmhc) 
# y=data_CARIB['CO2'][mask]
# y=a[mask] #data_CARIB['strat_mask'][mask]


plt.plot(time,y,'o')
plt.show()
exit()
xlabs=['config.td']*2
ylabs=['tbd']
xlims=[]
ylims=[]
fig,axes=scantools.plot_init(1,2,xlabs=xlabs,ylabs=ylabs,xlims=xlims,ylims=ylims)

