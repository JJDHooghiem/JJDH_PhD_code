"""
This code was written for the analysis presented in the disseration of Joram Jan Dirk Hooghiem
Functions that do the core analysis are presented in here.  

This program is free software: you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software Foundation, 
version 3. This program is distributed in the hope that it will be useful, but 
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS 
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. 

You should have received a copy of the GNU General Public License along with this 
program. If not, see <http://www.gnu.org/licenses/>.
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import atmos
import lodautil
import matplotlib.pyplot as plt
import numpy as np
import scantools
import stisolib
from scipy.interpolate import interp1d
from scipy.stats import pearsonr
import config


ncfid=lodautil.get_ncfid(interpolated=True,daymean=True)
LISA=lodautil.flattened_LISA()
for dat in lodautil.get_dates(LISA):
    data=lodautil.date_select(LISA,dat)
    lisa_time=np.floor(lodautil.get_sample_dt(data)[0][-1])+0.5
    lisa_p=data['p']*100
    ch4=data['CH4']
    # lisarates=eval_rates(lisa_p,data['T'])[1:]
    # for axes,x in zip(axes_array.ravel(),lisarates):
        # axes.plot(x,lisa_p,color=c,marker='d',label=dat)
    coLife= lodautil.get_echam_at_LISA(lisa_time,lisa_p,'tauCO',ncfid,ch4=ch4,method='hyb')
    for p,col in zip(lisa_p,coLife):
        print('CO in the stratosphere of sample on %s at pressure %.0f Pa has a lifetime %.0f days' % (dat,p,col/(3600*24)))

