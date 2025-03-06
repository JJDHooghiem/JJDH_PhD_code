#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Don't remove the line below, it is checked by "one to run them all"
# --otrta-p--
# extension p means parallel, s is for single
"""
This code was written for the analysis presented in the dissertation of Joram Jan Dirk Hooghiem
"""
import scantools 
import scan.stico as stico
import lodautil 
import numpy as np
import matplotlib.pyplot as plt
import config
def osd_constraint(obs,eps):

    dO2=10
    dO1D=130
    f_osd= (obs+eps-dO2)/(dO1D-dO2)
    f_osd=f_osd/0.25 # constant branching
    return f_osd


lisa = lodautil.var_select(lodautil.flattened_LISA(), 'd18O(CO)')
lisa['ECHAM_time'], _ = lodautil.get_sample_dt(lisa)

ncfid = lodautil.get_ncfid(interpolated=False, daymean=False)
echamy=['CO2','CO','FHVCO','FCMCO','FMO1DCO','FCMCO2','FMO1DCO2','O2','FOZO2']
for t,c in zip(np.unique(lisa['ECHAM_time']),config.GruvBoxColors):
    mask=lisa['ECHAM_time']==t
    echam_data=lodautil.get_echam_tracers_gp(t,lisa['p'][mask],echamy,ncfid,ch4=lisa['CH4'][mask],method='hyb')
    fch4,fco2,fo1d,_=[float(value) for value in stico.echam_correct_fractions(echam_data)]
    # plt.plot(fo1d/0.25, lisa['p'][mask],linestyle='-',color=c,marker='d',label='mod')
    plt.plot(osd_constraint(lisa['d18O(CO)'][mask],17)-fo1d/0.25, fo1d/0.25,linestyle='-',color=c,marker='o', label='obs')

plt.show()
exit()
