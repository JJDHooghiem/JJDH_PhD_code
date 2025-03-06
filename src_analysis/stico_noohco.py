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
import scan.stico as stico
colors = config.GruvBoxColors
LISA = lodautil.flattened_LISA()
LISA = lodautil.var_select(LISA,'d18O(CO)').reset_index()
stico.get_efeps_at(LISA,interpolated=True,daymean=False,method='hyb')
LISA['c13_cor']=stico.cor_d_with_e(LISA['d13C(CO)'],LISA['sink_en_13'])
xlabs = [config.axl['13c']]
ylabs = [config.axl['p']]
xlims = [(-60,-20)] 
ylims = [(175,25)]
fig, axes = scantools.plot_init(1,1 , xlabs=xlabs, ylabs=ylabs, xlims=xlims, ylims=ylims)
meth='hyb'
for dat,c,m in zip(lodautil.get_dates(LISA),config.GruvBoxColors,config.Markers):
# for dat in ['2017-09-04']:
    data = lodautil.date_select(LISA, dat)
    # 12:00 utc:

    axes.plot(data['c13_cor'],data['p'], color=c, marker=m, label=dat) #r"$^{18}\textrm{O}$"+
    axes.plot(data['d13C(CO)']-data['sink_en_13'],data['p'], color=c, marker=m, label=dat) #r"$^{18}\textrm{O}$"+
# for ax in axes.ravel():
handles, labels = scantools.getUniqueLegend(axes)
axes.legend(handles=handles, labels=labels)
fig.tight_layout()
fig.savefig(config.FigDir+'stico_c13_cor.pdf')
