#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Don't remove the line below, it is checked by "one to run them all"
# --otrta-p--
# extension p means parallel, s is for single
"""
This code was written for the analysis presented in the dissertation of Joram Jan Dirk Hooghiem
"""
import numpy as np
import config
import scantools
# array convention CO2 (ppm) CH4 (ppb) CO (ppb) 
# First five terms as in Andrews 2014
# u_precision=np.array( [ 0.02 , 0.2 , 4])
u_baseline=np.array([ 0.0  , 0.0 , 0.0])
u_eq=np.array([ 0    , 0   , 0])

co2_low=[  81.45,      81.52   ]     
ch4_low=[ 399.65,     396.70   ]     
co_low =[  41.06,      41.35   ]     

a=np.diff(ch4_low)
# print(abs(a)/np.sqrt(3))
# print(np.std(ch4_low))
# print(np.std(ch4_low,ddof=1))
ch4_t=tank=1812.67
co_t=tank=137.36
ch4unc_e=(np.std(ch4_low,ddof=1)/(ch4_t-np.mean(ch4_low)))
counc_e=(np.std(co_low,ddof=1)/(co_t-np.mean(co_low)))

ch4_m=tank=700
co_m=tank=10
ch4unc=    ch4unc_e*(ch4_t-ch4_m)
counc =    counc_e*(co_t-co_m)
u_ex=np.array([ 0    , ch4unc   , counc ]) # Type B
# print(u_ex)
# wv is very low; absolute bias corrections are typically smaller then ppb 
u_wv=np.array(        [ 0.0 , 0.0 , 0.0])
# calibration uncertainty 
u_sc=np.array(        [ 0.03 , 0.3 , 2]) # Type A

u_precision=np.array( [ 0.04 , 0.5 , 1]) # Type A 
# u_precision=np.array( [ 0.0 , 0.0 , 0]) # Type A 
# dead volume
u_dead=np.array([0.002 , 0.605 , 0.056]) # Type B
# storage drift
u_drift=np.array( [ 0.11 , 2 , 0])#/np.sqrt(3)     # Type B
uncnames=['a','ex','sc','dv','rd']
types=['A','B','A','B','B']
unc_sources=np.array([u_precision,u_ex,u_sc,u_dead,u_drift])
tot=np.sqrt(np.sum(unc_sources.T**2,axis=1))
# print(unc_sources)
print("%.2f %.1f %.1f" % tuple(tot))
# texfile=open(config.TabDir+'lisasd_unc.tex','w')
for n,p,t in zip(uncnames,unc_sources,types):
    a=r"$u_{\textrm{%s}}$" % n
    ts=np.array([a,*list(p),t] )
    print(ts)
    # scantools.npa_to_tex_table(ts,np.array([0,3,3,3,0]),texfile)
# ts=np.array([r"$u_{\textrm{%s}}$" % 'tot',*list(tot),''])
# scantools.npa_to_tex_table(ts,np.array([0,2,0,1,0]),texfile)
# texfile.close()

ran=np.array([5,1200,30])
# print("%.2f %.1f %.1f" % tuple(100*tot/ran))

