#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  8 09:39:23 2019

@author: joram
"""
import scan.wisman as wisman
import numpy as np
from lodautil.lisa import LISA_load
import sys
data = LISA_load()
temp = data['20170905']['T'][0]
pres = data['20170905']['p'][0]*100  # pa
co = np.round(data['20170905']['CO'][0], 0)
co_bg = np.round(data['20170906']['CO'][0], 0)
c13o_bg = data['20170906']['d13C(CO)'][0]
co18_bg = data['20170906']['d18O(CO)'][0]
C13O = data['20170905']['d13C(CO)'][0]
C18O = data['20170905']['d18O(CO)'][0]
dt = 25*3600*24
print()
print('temperature and pressure: ', temp, pres)
print()
print('Plume CO d13C d18O ', co, C13O, C18O)
print()
print('background CO d13C d18O ', co_bg, c13o_bg, co18_bg)
fstrat = float(sys.argv[1])
print(wisman.chem_mix_model(temp, pres, co, 1.2E6, co_bg, c13o_bg, co18_bg, C13O, C18O, dt, fstrat))
number = 10000

# def calc(i):
#    fstrat=np.random.normal(0.69,0.12)
#    results[i]=chem_mix_model(temp,pres,co,1.2E6,co_bg,c13o_bg,co18_bg,C13O,C18O,dt,fstrat)
#    return
# manager=multiprocessing.Manager()
# results=manager.list([None]*number)
#
#pool = multiprocessing.Pool()
#pool.map(calc, range(0, number))
# pool.close()
# print "pool finished"
# res=np.array(results).T
# for i in res:
#    print np.nanmean(i), np.nanstd(i)
