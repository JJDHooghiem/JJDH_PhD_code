#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Don't remove the line below, it is checked by "one to run them all"
# --otrta-p--
# extension p means parallel, s is for single
"""
This code was written for the analysis presented in the dissertation of Joram Jan Dirk Hooghiem
"""
import scan.limo as limo
import config
import matplotlib.pyplot as plt
import scantools
import config
import numpy as np
datamodel = limo.echam_st(800, 4.8, interpolated=True)
datamodel_noT = limo.echam_st(800, 0, interpolated=True)
datamodel_noP = limo.echam_st(0, 4.8, interpolated=True)
# datamodel = limo.echam_st(0, 10, interpolated=False)
# datamodel_noT = limo.echam_st(0, 0, rO1D='v', interpolated=False)
# datamodel_noP = limo.echam_st(0, 0, rO1D='v', interpolated=False)
colors = config.GruvBoxColors
ylabs = [config.axl['ph']]*2
xlabs = [config.axl['dco'], config.axl['dlch4']]

ylims = [(200, 0), (200, 0)]
xlims = [(-0.5, 2), (0, 50)]
fig, axes = scantools.plot_init( 1, 2, xlabs=xlabs, ylabs=ylabs, xlims=xlims, ylims=ylims)
for dat, m in zip(datamodel.keys(), config.Markers):
    c = colors[0]
    scantools.plot_add(axes[0], datamodel[dat]['dif'], datamodel[dat]['pres'] / 100, argsort=False,linestyle=':', marker=m, color=c, label="$E_T$ and $E_p$")
    scantools.plot_add(axes[1], datamodel[dat]['sink'], datamodel[dat] ['pres']/100, argsort=False,linestyle=':', marker=m, color=c, label="$E_T$ and $E_p$")
    c = colors[1]
    scantools.plot_add(axes[0], datamodel_noP[dat]['dif'], datamodel_noP[dat] ['pres']/100, argsort=False,linestyle=':', marker=m, color=c, label="$E_T$ only")
    scantools.plot_add(axes[1], datamodel_noP[dat]['sink'], datamodel_noP[dat] ['pres']/100,argsort=False, linestyle=':', marker=m, color=c, label="$E_T$ only")
    c = colors[3]
    scantools.plot_add(axes[0], datamodel_noT[dat]['dif'], datamodel_noT[dat] ['pres']/100, argsort=False,linestyle=':', marker=m, color=c, label="$E_p$ only")
    scantools.plot_add(axes[1], datamodel_noT[dat]['sink'], datamodel_noT[dat] ['pres']/100,argsort=False, linestyle=':', marker=m, color=c, label="$E_p$ only")
for ax in axes.ravel():
    handles, labels = scantools.getUniqueLegend(ax)
    ax.legend(handles=handles, labels=labels, loc='best')
plt.tight_layout()
plt.savefig(config.FigDir+'limo_dp_dt_st.pdf',
            format='pdf', bbox_inches='tight')


ylabs = [config.axl['ph']]*2
xlabs = [config.axl['lch4'], config.axl['ch4']]

ylims = [(200, 0), (200, 0)]
xlims = [(0, 200), (700, 2000)]
fig, axes = scantools.plot_init(
    1, 2, xlabs=xlabs, ylabs=ylabs, xlims=xlims, ylims=ylims)
for dat, m in zip(datamodel.keys(), config.Markers):
    c = colors[0]
    p=datamodel[dat]['pres']/100
    mask=(p>50)&(p<200)
    print(np.nanmean(datamodel[dat]['sinkCH4'][mask]))
    scantools.plot_add(axes[0], datamodel[dat]['sinkCH4'], datamodel[dat]['pres'] / 100,argsort=False, linestyle=':', marker=m, color=c, label="$E_T$ and $E_p$")
    scantools.plot_add(axes[1], datamodel[dat]['CH4'], datamodel[dat] ['pres']/100,argsort=False, linestyle=':', marker=m, color=c, label="$E_T$ and $E_p$")
    c = colors[1]
    scantools.plot_add(axes[0], datamodel_noP[dat]['sinkCH4'], datamodel_noP[dat] ['pres']/100,argsort=False, linestyle=':', marker=m, color=c, label="$E_T$ only")
    scantools.plot_add(axes[1], datamodel_noP[dat]['sink'], datamodel_noP[dat] ['pres']/100,argsort=False, linestyle=':', marker=m, color=c, label="$E_T$ only")
    c = colors[3]
    scantools.plot_add(axes[0], datamodel_noT[dat]['sinkCH4'], datamodel_noT[dat] ['pres']/100,argsort=False, linestyle=':', marker=m, color=c, label="$E_p$ only")
    scantools.plot_add(axes[1], datamodel_noT[dat]['CH4'], datamodel_noT[dat] ['pres']/100,argsort=False, linestyle=':', marker=m, color=c, label="$E_p$ only")
for ax in axes.ravel():
    handles, labels = scantools.getUniqueLegend(ax)
    ax.legend(handles=handles, labels=labels, loc='best')
plt.tight_layout()
plt.savefig(config.FigDir+'limo_ch4loss.pdf',
            format='pdf', bbox_inches='tight')

ylabs = [config.axl['ph']]
xlabs = [config.axl['co']]

ylims = [(200, 0)]
xlims = [(0, 50)]
fig, axes = scantools.plot_init( 1, 1, xlabs=xlabs, ylabs=ylabs, xlims=xlims, ylims=ylims)

for dat, m in zip(datamodel.keys(), config.Markers):
    c = colors[0]
    scantools.plot_add(axes, datamodel[dat]['COst'], datamodel[dat]['pres'] / 100, argsort=False,linestyle=':', marker=m, color=c, label="Steady state")
    c = colors[3]
    scantools.plot_add(axes, datamodel[dat]['COm'], datamodel[dat]['pres'] / 100, argsort=False,linestyle=':', marker=m, color=c, label="ECHAM5")

handles, labels = scantools.getUniqueLegend(axes)
axes.legend(handles=handles, labels=labels, loc='best')
plt.tight_layout()
plt.savefig(config.FigDir+'limo_co_stvsm.pdf', format='pdf')
