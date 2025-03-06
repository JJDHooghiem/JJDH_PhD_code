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
import scan.wisman as wisman
import scantools
from lodautil import AirCore_load

data = AirCore_load()


def linfit(x, a, b):
    return a*x+b


keys = ['RUG002_20170904', 'RUG002_20170905']
time_days = [24, 25]
colors = config.GruvBoxColors
markers = config.Markers
pres = [[167., 140.], [175, 140.]]         # Earlier determined plume edges
data_selected = {}
labels = ['AC 04/Sep', 'AC 05/Sep']
for dat, t, p, c, m in zip(keys, time_days, pres, range(2), markers):
    data_selected[dat] = {}
    sel = data[dat][(data[dat]['P'] <= p[0]) & (data[dat]['P'] >= p[1])]
    modeled_end = []
    modeled_strat = []
    for i in sel.index:
        co_end, co_final = wisman.back_calc(
            sel['T'][i], sel['P'][i]*100, sel['CO'][i]*1E-9, t*24*3600., 5*3600., 500., sel['GPS_ALT'][i]/1000.)
        modeled_end.append(co_final/1E-9)
        modeled_strat.append(co_end/1E-9)
#    only stratoshephere
    print(dat)
    print('min altitude ', np.round(np.min(sel['GPS_ALT'])/1000, 1))
    print('max altitude ', np.round(np.max(sel['GPS_ALT'])/1000, 1))
    data_selected[dat]['CO_OH_cor'] = modeled_strat
    data_selected[dat]['CO2'] = sel['CO2']
    data_selected[dat]['CO'] = sel['CO']
# regression_statistics={}
# for dat,t,p,c,m,l in zip(keys,time_days,pres,range(2),markers,labels):
#     regression_statistics[dat]={}
#     # print("slope %.0f, 95  ci=[ %.0f, %.0f ]" % (fitparams[1],*cis))
#     # print("r2 %.2f" % r2)
#     # y=np.array(data_selected[dat]['CO'])
#     # fitparams,r2,fittedvalues,cb_low,cb_upp,pb_low,pb_upp,ci=scantools.regression(x,y)
#     # cii,cis=ci
#     # print("slope %.0f, 95  ci=[ %.0f, %.0f ]" % (fitparams[1],*cis))
#     # print("r2 %.2f" % r2)
#     regression_statistics[dat]['stats_OH_cor']=stats.linregress(data_selected[dat]['CO2'],data_selected[dat]['CO_OH_cor'])          # perfomr liner regreasion using scipy.stats.linregres
#     regression_statistics[dat]['stats_original']=stats.linregress(data_selected[dat]['CO2'],data_selected[dat]['CO'])          # perfomr liner regreasion using scipy.stats.linregres
xlabs = [config.axl['co2']]
ylabs = [config.axl['co']]
xlims = [(403.6, 405.2)]
ylims = [(25, 200)]
fig, axes = scantools.plot_init( 1, 1, xlabs=xlabs, ylabs=ylabs, xlims=xlims, ylims=ylims)
for dat, t, p, c, m, l in zip(keys, time_days, pres, range(2), markers, labels):
    data_selected[dat]

    x = np.array(data_selected[dat]['CO2'])
    y = np.array(data_selected[dat]['CO_OH_cor'])
    fitparams, r2, fittedvalues, cb_low, cb_upp, pb_low, pb_upp, ci,p = scantools.regression(
        x, y)
    cii, cis = ci
    axes.plot(data_selected[dat]['CO2'], data_selected[dat]['CO_OH_cor'], marker=m, color=colors[c*2],
              linestyle='', label='%s, OH-cor.\n $a=%.0f$ ci=[%.0f,%.0f], $r^2=%.2f$' % (l, fitparams[1], *cis, r2))
    axes.plot(np.linspace( 403.5, 405.5, 2), linfit(np.linspace( 403.5, 405.5, 2), fitparams[1], fitparams[0]), color=colors[c*2])

    # .format(l,np.round(regression_statistics[dat]['stats_OH_cor'][0])))
    y = np.array(data_selected[dat]['CO'])
    fitparams, r2, fittedvalues, cb_low, cb_upp, pb_low, pb_upp, ci,p = scantools.regression( x, y)
    cii, cis = ci

    axes.plot(data_selected[dat]['CO2'], data_selected[dat]['CO'], marker=m, color=colors[c*2+1], linestyle='', label='%s, original\n $a=%.0f$ ci=[%.0f,%.0f], $r^2=%.2f$' % (l, fitparams[1], *cis, r2))
    axes.plot(np.linspace(403.5, 405.5, 2), linfit(np.linspace( 403.5, 405.5, 2), fitparams[1], fitparams[0]), color=colors[c*2+1])
fig.tight_layout()
axes.legend()
fig.savefig(config.FigDir+'wisman_enhancement.pdf'             )
