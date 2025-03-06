# -*- coding: utf-8 -*-
"""
Created on Thu Dec 14 15:09:44 2017

@author: joram

Script to analyse the potential biomass burning event in the stratosphere.

"""
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import atmos
#import pandas as pd#__VERSION__:'1.15.3'
# scipy version '1.1.0'
from scipy import stats
import config
import scan.wisman as wisman
from lodautil import AirCore_load
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d
colors2=['#1f77b4','#bcbd22','#2ca02c','#d62728','#9467bd','#7f7f7f', '#e377c2','#8c564b','#ff7f0e','#17becf']

data=AirCore_load()
def linfit(x,a,b):
    return a*x+b

keys='RUG002_20170906'
p=[190.,135.]         # Earlier determined plume edges
datacobackgrounds=[]
sel=data[keys][(data[keys]['P']<=p[0]) & (data[keys]['P']>=p[1])]
def runingmean(x,N):
    y=np.convolve(x, np.ones((N,))/N, mode='valid')
    return y
N=25
print(N/2)
middle=int(np.ceil(N/2)-1)
co_smooth_bg=runingmean(sel['CO'],N)
co2_smooth_bg=runingmean(sel['CO2'],N)
thetha_smooth_bg=runingmean(sel['THETA'],N)
cointer=interp1d(thetha_smooth_bg,co_smooth_bg)
co2inter=interp1d(thetha_smooth_bg,co2_smooth_bg)
plt.plot(thetha_smooth_bg,co2_smooth_bg)
plt.plot(sel['THETA'],sel['CO2'],'o')
# plt.plot(data[keys]['GPS_ALT'],data[keys]['CO2'])
plt.close()
keys=['RUG002_20170904','RUG002_20170905']
time_days=[24,25]
colors=['navy','royalblue','darkorange','orange']
markers=['+','*']
pres=[[175.,140.],[175,140.]]         # Earlier determined plume edges
data_selected={}
labels=['AirCore 04/Sep','AirCore 05/Sep']

for dat,t,p,c,m in zip(keys,time_days,pres,range(2),markers):
    data_selected[dat]={}
    sel=data[dat][(data[dat]['P']<=p[0]) & (data[dat]['P']>=p[1])]
    modeled_end=[]
    modeled_strat=[]
    for i in sel.index:
        co_end,co_final=wisman.back_calc(sel['T'][i],sel['P'][i]*100,sel['CO'][i]*1E-9,t*24*3600.,5*3600.,500.,sel['GPS_ALT'][i]/1000.)
        modeled_end.append(co_final/1E-9)
        modeled_strat.append( co_end/1E-9)

    data_selected[dat]['CO_OH_cor']=modeled_strat
    data_selected[dat]['CO2']=sel['CO2']
    data_selected[dat]['CO']=sel['CO']
    # data_selected[dat]['CH4']=sel['CH4']
    data_selected[dat]['THETA']=sel['THETA']
    # data_selected[dat]['P']=sel['P']
    # data_selected[dat]['T']=sel['T']
    data_selected[dat]['THETA2']=atmos.theta(sel['T'],sel['P']*100)
    # data_selected[dat]['CObg']=curve(data_selected[dat]['THETA'],*CO_opt)
    # data_selected[dat]['CO2bg']=curve(data_selected[dat]['THETA'],*CO2_opt)
for dat,t,p,c,m,l in zip(keys,time_days,pres,range(2),markers,labels):     
    print(dat)
    co_smooth=runingmean(data_selected[dat]['CO'],N)
    co_smooth_oh=runingmean(data_selected[dat]['CO_OH_cor'],N)
    co2_smooth=runingmean(data_selected[dat]['CO2'],N)
    thetha_smooth=runingmean(data_selected[dat]['THETA'],N)
    
    co_bg=cointer(thetha_smooth)
    co2_bg=co2inter(thetha_smooth)

    difCO2=co2_smooth-co2_bg
    difCO=co_smooth-co_bg
    difCO_OH=co_smooth_oh-co_bg
    sel=(difCO2>=0.2)
    enhenc=difCO[sel]/difCO2[sel]
    enhenc_OH=difCO_OH[sel]/difCO2[sel]
    print(len(enhenc))
    print("%.2f %.2f" % (np.mean(enhenc), np.std(enhenc)))
    print("%.2f %.2f" % (np.mean(enhenc_OH), np.std(enhenc_OH)))
    # plt.plot(data_selected[dat]['THETA'][sel],enhenc)
    # plt.plot(data_selected[dat]['P'][sel],data_selected[dat]['THETA'][sel])
    # plt.plot(data_selected[dat]['P'][sel],data_selected[dat]['THETA2'][sel])
    # plt.plot(data_selected[dat]['CH4'][sel],enhenc_OH)
    # plt.plot(data_selected[dat]['THETA'][sel],enhenc,label="Or.")
    # plt.plot(data_selected[dat]['THETA'][sel],enhenc_OH,label="OH corrected")
    # print(stats.linregress(difCO2,difCO))
    plt.plot(co2_bg,co_bg)
    plt.plot(data_selected[dat]['CO2'],data_selected[dat]['CO'])
    plt.plot(data_selected[dat]['CO2'],data_selected[dat]['CO_OH_cor'])
    plt.plot(co2_smooth,co_smooth_oh)
    plt.plot(co2_smooth,co_smooth)
    plt.legend()
    plt.ylabel('Enhancement ratio')
    plt.xlabel('THETA')
plt.savefig(config.FigDir+'testenhencement.pdf')

