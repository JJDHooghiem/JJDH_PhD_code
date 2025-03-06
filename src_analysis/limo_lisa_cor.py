#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Don't remove the line below, it is checked by "one to run them all"
# --otrta-p--
# extension p means parallel, s is for single
"""
This code was written for the analysis presented in the dissertation of Joram Jan Dirk Hooghiem
"""
import scan.limo as limo
import matplotlib.pyplot as plt
import config
import scantools
import numpy as np

xlabs = [config.axl['ls']+' '+config.axl['co'], config.axl['ls']+' '+config.axl['ch4'], config.axl['ls']+' '+config.axl['n2o'], config.axl['ls']+' '+config.axl['co2']]
ylabs = [config.axl['echam']+' '+config.axl['co'], config.axl['echam']+' '+config.axl['ch4'], config.axl['echam']+' '+config.axl['n2o'], config.axl['echam']+' '+config.axl['co2']]


lisakeys = ['CO', 'CH4', 'N2O', 'CO2']
echamkeys = ['tracer_gp_CO', 'tracer_gp_CH4', 'tracer_gp_N2O', 'tracer_gp_CO2']

xylims = [(0, 50), (700, 1900), (210, 330), (390, 410)]

fig, axes = scantools.plot_init( 2, 2, xlabs=xlabs, ylabs=ylabs, xlims=xylims, ylims=xylims)
data_dif = limo.eval_echam_oneone(axes, lisakeys, echamkeys)
fig.tight_layout()
for a in axes.ravel():
    a.legend(loc='best')
fig.savefig(config.FigDir+'limo_cor_tracers.pdf', format='pdf')


tex_object = open(config.TabDir+'limo_dif_tracer.tex', 'w')
for key in data_dif.keys():
    means = [np.sqrt(np.mean(data_dif[key][spec]**2)) for spec in data_dif[key].keys()]
    stds = [np.mean(data_dif[key][spec]) for spec in data_dif[key].keys()]

    stds=np.where(np.round(stds,1)==0,0,stds) 
    texline = np.array([r"$%.1f$&$%.1f$" % (mean, std) for mean, std in zip(means, stds)])
    texline = np.append(key, texline)
    scantools.npa_to_tex_table(texline, 1, tex_object)
tex_object.close()
###

fig = limo.compareModel(lisakeys, echamkeys)
fig.tight_layout()

leg = plt.legend(ncol=2, loc='center', bbox_to_anchor=( 0.25, 0.5), bbox_transform=fig.transFigure)
plt.savefig(config.FigDir+'limo_taylor_tracers.pdf', format='pdf')
plt.close()
# physics
xlabs = [config.axl['ls']+' '+config.axl['T'],config.axl['ls']+' '+config.axl['th'], config.axl['ls']+' '+config.axl['ph']]
ylabs = [config.axl['echam']+' '+config.axl['T'],config.axl['echam']+' '+config.axl['th'], config.axl['echam']+' '+config.axl['ph']]


lisakeys = ['T',      'PT',      'p']
echamkeys = ['ECHAM5_tm1', 'ECHAM5_tpot', 'p']

xylims = [(205, 235), (350, 650), (0, 250)]

fig, axes = scantools.plot_init( 1, 3, xlabs=xlabs, ylabs=ylabs, xlims=xylims, ylims=xylims)
data_dif = limo.eval_echam_oneone(axes, lisakeys, echamkeys)
fig.tight_layout()
for a in axes.ravel():
    a.legend()
plt.savefig(config.FigDir+'limo_cor_ptt.pdf',
            format='pdf', bbox_inches='tight')

tex_object = open(config.TabDir+'limo_dif_ptt.tex', 'w')
for key in data_dif.keys():
    means = np.array([np.sqrt(np.mean(data_dif[key][spec]**2)) for spec in data_dif[key].keys()])
    stds = np.array([np.mean(data_dif[key][spec]) for spec in data_dif[key].keys()])
    stds=np.where(np.round(stds,1)==0,0,stds) 
    texline = np.array([r"$%.1f$&$%.1f$" % (mean, std) for mean, std in zip(means, stds)])
    texline = np.append(key, texline)
    scantools.npa_to_tex_table(texline, 1, tex_object)
tex_object.close()
fig = limo.compareModel(lisakeys, echamkeys)
fig.tight_layout()
leg = plt.legend(ncol=1, loc='center', bbox_to_anchor=( 0.25, 0.5), bbox_transform=fig.transFigure)
plt.savefig(config.FigDir+'limo_taylor_ptt.pdf', format='pdf')
