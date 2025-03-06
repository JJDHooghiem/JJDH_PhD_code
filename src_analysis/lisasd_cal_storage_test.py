#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scantools

data=pd.read_csv(config.DataDir+'/LISA_Sampler_Development/2016_09_Sampling_bag_storage_tests/Picarro_data_samplebag_tests/Calcylinders.csv')
data['t']=pd.to_datetime(data['Time'],format='%Y-%m-%d %H:%M:%S.%f')
# print(data.keys())
# for  l in data['Calcyl']:
l='L'
x=np.array(data['t'][(data['Calcyl']==l)].values.astype('float64'))
x=(x-np.min(x))/(3600*1E9)
print(x)

fitparams, r2, fittedvalues, cb_low, cb_upp, pb_low, pb_upp, ci=scantools.regression(x,np.array(data['CO2(ppm)'][(data['Calcyl']==l)]))
print(4*fitparams[1])
plt.plot(x,data['CO2(ppm)'][(data['Calcyl']==l)],'o')
plt.plot(x,fitparams[0]+fitparams[1]*x,'o')
plt.savefig('testlol.pdf')
