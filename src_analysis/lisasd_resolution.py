#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Don't remove the line below, it is checked by "one to run them all"
# --otrta-p--
# extension p means parallel, s is for single
# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
from lodautil import LISA_load
from scipy.interpolate import interp1d
import atmos
import scan.lisasd as lisasd
import config
import scantools
LISA = LISA_load()

gas_constant = atmos.constants.R_univ
Pstp = atmos.constants.P_stp/100  # Standard atmospheric pressure in mbar or hPa
# Standard atmospheric temperature STP in Kelvin
Tstp = atmos.constants.T_stp

h = np.linspace(0, 40000, 40001)
# to hPa
p = np.array([atmos.Standard_atmos(i)[0]/100 for i in h])


inverse = interp1d(p, h)
xlabs = [config.axl['pa']]*2
ylabs = [config.axl['vsize'], config.axl['vres']]
xlims = [(0, 200), (0, 200)]
ylims = [(0, 1), (0, 2000)]
fig, axes = scantools.plot_init( 1, 2, xlabs=xlabs, ylabs=ylabs, xlims=xlims, ylims=ylims)

markers = config.Markers
# ['saddlebrown','Darkgreen','lime','tomato']
colors = config.GruvBoxColors
for n, m, c, c2 in zip(LISA.keys(), markers, colors, colors):
    if not "2019" in n:
        Data_load = LISA[n]
        # axes[0].errorbar(Data_load['p'], Data_load['Samplesize'], xerr=0, yerr=0, fmt=m, color=c2, label=n)
        # axes[1].errorbar(Data_load['p'], Data_load['Vertical resolution'], xerr=0, yerr=0, fmt=m, color=c2)
        axes[0].plot(Data_load['p'], Data_load['Samplesize'],  marker=m, color=c2, label=n,linestyle='')
        axes[1].plot(Data_load['p'], Data_load['Vertical resolution'],marker=m, color=c2,linestyle='')
leg = axes[0].legend(loc='lower center', bbox_to_anchor=(
    0.5, -0.12), bbox_transform=fig.transFigure)
fig.savefig(config.FigDir+'lisasd_Resoltionandsamplesize_V2.pdf',
            format='pdf', bbox_inches='tight')
plt.close()
xlabs = [config.axl['vsize'],config.axl['vres'] ]
ylabs = [config.axl['alt']]*2
xlims = [(0, 1), (0, 2000)]
ylims = [(10, 30)]*2
fig, axes = scantools.plot_init(
    1, 2, xlabs=xlabs, ylabs=ylabs, xlims=xlims, ylims=ylims)
# calculate the modelled value for
P_model = np.linspace(10, 300, 100)
V = lisasd.pump_time(200-lisasd.Tofset)*P_model
vmax = lisasd.V_b*1000*280/1000.
Vsample = [V[m] if V[m] < vmax else vmax for m in range(0, len(V))]
pump_t = lisasd.inverse_pump_time(Vsample/P_model)
vert_res_model = (pump_t+lisasd.Tofset)*5  # vertical resolution assuming 5 m/s
vert_res_model2 = (pump_t+lisasd.Tofset)*8
vert_res_model3 = (pump_t+lisasd.Tofset)*3
Height = inverse(P_model)
# colors=['darkblue','Darkgreen','lime','tomato']
for n, m, c, c2 in zip(LISA.keys(), markers, colors, colors):
    if not "2019" in n:
        Data_load = LISA[n]

        axes[0].errorbar(Data_load['Samplesize'], Data_load['Altitude'] / 1000,marker=m, color=c2, label=n,linestyle='')
        axes[1].errorbar(Data_load['Vertical resolution'], Data_load['Altitude']/1000, marker=m, color=c2,linestyle='')
        labels = ('Sampler', 'Sampler', 'Sampler', 'Sampler')
colors = np.append(colors, colors)
axes[0].plot(Vsample, Height/1000, color='k')
axes[1].plot(vert_res_model, Height/1000, linestyle='-' ,label='model $w=5$ m s$^{-1}' ,color='k')
axes[1].plot(vert_res_model2, Height/1000,linestyle=':' ,label='model $w=8$ m s$^{-1}' ,color='k')
axes[1].plot(vert_res_model3, Height/1000,linestyle='-.',label='model $w=3$ m s$^{-1}' ,color='k')

fig.tight_layout()
leg = axes[0].legend(ncol=4, loc='lower center', bbox_to_anchor=( 0.5, -0.08), bbox_transform=fig.transFigure)
fig.savefig(config.FigDir+'lisasd_resolution.pdf', format='pdf', bbox_inches='tight')
plt.close()
