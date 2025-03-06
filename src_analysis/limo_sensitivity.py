#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Don't remove the line below, it is checked by "one to run them all"
# --otrta-p--
# extension p means parallel, s is for single
"""
This code was written for the analysis presented in the dissertation of Joram Jan Dirk Hooghiem
"""
from scipy.interpolate import interp1d
import scan.limo as limo
import config
import numpy as np
import scantools
import config

def fetchlabel(dat):
    dat = dat.replace('-', '')
    if "2019" in dat[0:4]:
        linestyle = ":"
        color = colors[0]
        label = "Tra. June"
        loc="Tra\^{i}nou"
    else:

        linestyle = "-"
        if "04" in dat[4:6]:
            color = colors[1]
            label = "Sod. April"
            loc="Sodankyl\"{a}"
        if "06" in dat[4:6]:
            color = colors[0]
            label = "Sod. June"
            loc="Sodankyl\"{a}"
        if "09" in dat[4:6]:
            color = colors[2]
            label = "Sod. September"
            loc="Sodankyl\"{a}"
    return color, linestyle, label, loc


colors = config.GruvBoxColors

xlabs = [config.axl['DT']]*4
ylabs = [config.axl['dco'], config.axl['dlch4']]*4
xlims = [(-7.5, 7.5)]*8
ylims = [(-5, 5), (-40, 40), (-5, 5), (-15, 15)]
fig, axes = scantools.plot_init( 2, 2, xlabs=xlabs, ylabs=ylabs, xlims=xlims, ylims=ylims)
dt = np.linspace(-10, 10, 21)

for p, r in zip([500, 5000], [0, 1]):
    dco = []
    dch = []
    for T in dt:
        datamodel = limo.echam_st(0, T, interpolated=True)

        dcoper = np.array([])
        dchper = np.array([])
        for dat in datamodel.keys():
            co = interp1d(datamodel[dat]['pres'], datamodel[dat]['dif'])(p)
            ch4 = interp1d(datamodel[dat]['pres'],
                           datamodel[dat]['sink'])(p)
            dcoper = np.append(dcoper, co)
            dchper = np.append(dchper, ch4)
        dco.append(dcoper)
        dch.append(dchper)
    dco = np.array(dco).T
    dch = np.array(dch).T

    tex_co_sens = open(config.TabDir+'limo_sensitivity_%s.tex' %
                       str(int(p/100)), 'w')
    for co, ch, dat in zip(dco, dch, datamodel.keys()):
        a = []
        c, s, l,loc = fetchlabel(dat)
        a.append(loc+' '+dat)
        fit1, _, _, _, _, _, _, _,_= scantools.regression(
            dt, co, intercept=False)
        a.append(fit1[0])
        fit1, _, _, _, _, _, _, _ ,_= scantools.regression(
            dt, ch, intercept=False)
        a.append(fit1[0])
        prec = np.array([0, 2, 2, 2, 2])
        scantools.npa_to_tex_table(np.array(a), prec, tex_co_sens)
        scantools.plot_add(axes[r, 0], dt, co, color=c, linestyle=s,
                           label=l)

        scantools.plot_add(axes[r, 1], dt, ch, color=c, linestyle=s,
                           label=l)

    tex_co_sens.close()
for ax in axes.ravel():
    handles, labels = scantools.getUniqueLegend(ax)
    ax.legend(handles=handles, labels=labels, loc='best')
fig.tight_layout()
fig.savefig(config.FigDir+'limo_co_sensitivity.pdf')
