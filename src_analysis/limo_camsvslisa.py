#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Don't remove the line below, it is checked by "one to run them all"
# --otrta-p--
# extension p means parallel, s is for single
"""
This code was written for the analysis presented in the dissertation of Joram Jan Dirk Hooghiem
"""
import lodautil
import numpy as np
import config
import scantools

xlabs = [config.axl['ls']+' '+config.axl['co'], config.axl['ls']+' '+config.axl['ch4'], config.axl['ls']+' '+config.axl['T'] ]
ylabs = [config.axl['cams']+' '+config.axl['co'], config.axl['cams']+' '+config.axl['ch4'], config.axl['cams']+' '+config.axl['T'] ]

xylims = [(0, 50), (500,2000),(215, 235)]

fig, axes = scantools.plot_init( 1, 3, xlabs=xlabs, ylabs=ylabs, xlims=xylims, ylims=xylims)

lisakeys = ['CO','CH4' ,'T']

lab = ''

c = config.GruvBoxColors[0]

data_dif = {}
for var, ax in zip(lisakeys, axes):
    x, y = lodautil.collect_lisa_cams(var)
    scantools.axoneone(ax, x, y, color=c, lab=lab)
    data_dif[var] = y-x

for a in axes.ravel():
    a.legend()

tex_object = open(config.TabDir+'limo_dif_cams.tex', 'w')
for key in data_dif.keys():
    means = [np.sqrt(np.mean(data_dif[key]**2))]
    stds = [np.mean(data_dif[key])]

    texline = np.array([r"$%.1f$&$%.1f$" % (mean, std) for mean, std in zip(means, stds)])
    if key == "CO":
        k = "$y(\ch{CO})$"
    elif key == "CH4":
        k = "$y(\ch{CH4})$"
    else:
        k = "$T$"
    texline = np.append(k, texline)
    scantools.npa_to_tex_table(texline, 1, tex_object)

tex_object.close()
fig.tight_layout()
fig.savefig(config.FigDir+'limo_camslisa.pdf')
