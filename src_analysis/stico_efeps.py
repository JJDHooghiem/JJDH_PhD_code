#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Don't remove the line below, it is checked by "one to run them all"
# --otrta-p--
# extension p means parallel, s is for single
"""
This code was written for the analysis presented in the dissertation of Joram Jan Dirk Hooghiem
"""
import scantools
import lodautil
import config
import numpy as np
import lodautil
import stisolib 
pdummy=np.linspace(200,0,20)
edummy=-1000*(stisolib.alpha_oh_o18(pdummy*100)-1)
# print(edummy)
colors = config.GruvBoxColors
LISA = lodautil.flattened_LISA()
LISA = lodautil.var_select(LISA,'d18O(CO)')
ncfid = lodautil.get_ncfid(interpolated=True, daymean=False)
xlabs = [config.axl['enr']]*2
ylabs = [config.axl['ph']]
xlims = [(-20,-10)] 
ylims = [(200,25)]
fig, axes = scantools.plot_init(1,1 , xlabs=xlabs, ylabs=ylabs, xlims=xlims, ylims=ylims)
scantools.plot_add(axes,edummy,pdummy,argsort=False,marker='',color=config.GruvBoxColors[4],linestyle='-',label="equilibrium")
meth='hyb'
for dat,c in zip(lodautil.get_dates(LISA),config.GruvBoxColors):
# for dat in ['2017-09-04']:
    data = lodautil.date_select(LISA, dat)
    # 12:00 utc:
    echamy=['E13pCO','E18pCO','CO']
    # time = np.floor(lodautil.get_sample_dt(data)[0][2])+0.5
    time = lodautil.get_sample_dt(data)[0][2]
    # axes.plot(data['d18O(CO)'],data['p'], color=colors[4], marker='o', label=r"$^{18}\textrm{ O }$")
    # for meth,m in zip(['hyb'],['p','d']):
    # echam_data=lodautil.get_echam_tracers_gp(time,data['p']*100,echamy,ncfid,method=meth,ch4=data['CH4'])

    COeps18 = 1e3*(echam_data['E18pCO']/echam_data['CO']-1)
    print(dat,data['p'],COeps18)
    # d=1000*((1+data['d18O(CO)']/1000)/(1+COeps18 /1000)-1)
    m='d'
    # press = lodautil.echam.get_ECHAM_pp(time, ncfid)
    axes.plot(COeps18,data['p'], color=c, marker=m, label=dat) #r"$^{18}\textrm{O}$"+
        # axes[1].plot(d,data['p'], color=c, marker=m, label=r"$^{18}\textrm{ O }$"+dat)

    # # press = lodautil.echam.get_ECHAM_pp(time, ncfid)
    COeps18 = 1e3*(echam_data['E13pCO']/echam_data['CO']-1)
    print(dat,data['p'],COeps18)
    # d=1000*((1+data['d13C(CO)']/1000)/(1+COeps18 /1000)-1)
    m='o'
    # axes.plot(COeps18,data['p'], color=c, marker=m, linestyle=':',label=r"$^{13}\textrm{C}$"+dat)

    
# for ax in axes.ravel():
handles, labels = scantools.getUniqueLegend(axes)
axes.legend(handles=handles, labels=labels, loc='best')
fig.tight_layout()
fig.savefig(config.FigDir+'stico_efeps_with_meso.pdf')
