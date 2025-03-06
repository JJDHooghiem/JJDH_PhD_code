# -*- coding: utf-8 -*-
"""
Created on Thu Dec 14 15:09:44 2017

@author: joram

Script to analyse the potential biomass burning event in the stratosphere.

"""
import matplotlib.pyplot as plt
import numpy as np
#import pandas as pd#__VERSION__:'1.15.3'
# scipy version '1.1.0'
from scipy import stats
import config
import scan.wisman as wisman
from lodautil import AirCore_load

colors2=['#1f77b4','#bcbd22','#2ca02c','#d62728','#9467bd','#7f7f7f', '#e377c2','#8c564b','#ff7f0e','#17becf']

data=AirCore_load()
def linfit(x,a,b):
    return a*x+b

keys=['RUG002_20170905', 'RUG002_20170904','RUG002_20170906','RUG002_20170907']
p=[195.,130.]         # Earlier determined plume edges
backgrouds=['RUG002_20170906','RUG002_20170907']
datacobackgrounds=[]
for dat in keys:
    sel=data[dat][(data[dat]['P']<=p[0]) & (data[dat]['P']>=p[1])]
    std=np.std(sel['CO'])
    if dat in backgrouds:
        for val in sel['CO']:
            datacobackgrounds.append(val)
    print("%.2f -- %.2f" % ( sel['GPS_ALT'].iloc[0]/1000,sel['GPS_ALT'].iloc[-1]/1000))
    plt.plot(sel['CO'],sel['GPS_ALT'],label=dat+' std %.1f' % std )
plt.legend()
plt.xlabel('\ch{CO} ppb')
plt.ylabel('Altitude (m)')
# plt.savefig('testAirCorvar.pdf')
print(np.std(np.array(datacobackgrounds)))
