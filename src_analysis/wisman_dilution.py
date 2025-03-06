#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Don't remove the line below, it is checked by "one to run them all"
# --otrta-p--
# extension p means parallel, s is for single
"""
This code was written for the analysis presented in the dissertation of Joram Jan Dirk Hooghiem
"""
import scan.wisman as wisman
import matplotlib.pyplot as plt
from lodautil.lisa import LISA_load
import numpy as np
import config
import scantools
print('Generating dilution plot')
plt.close()
data = LISA_load()
temp = data['20170905']['T'][0]
pres = data['20170905']['p'][0]*100  # in Pa
co = data['20170905']['CO'][0]
co_bg = data['20170906']['CO'][0]
c13o_bg = data['20170906']['d13C(CO)'][0]
co18_bg = data['20170906']['d18O(CO)'][0]
C13O = data['20170905']['d13C(CO)'][0]
C18O = data['20170905']['d18O(CO)'][0]
dt = 25*3600*24
print()
print('temperature and pressure: ', temp, pres)
print()
print(co, C13O, C18O)
print()
print(co_bg, c13o_bg, co18_bg)
print(dt)

colors = config.GruvBoxColors
fstrat = np.linspace(0, 0.99, 100)
O18_noh, C13_noh, CO_noh = wisman.chem_mix_model(
    temp, pres, co, 0, co_bg, c13o_bg, co18_bg, C13O, C18O, dt, fstrat)
O18, C13, CO = wisman.chem_mix_model(
    temp, pres, co, 1.2E6, co_bg, c13o_bg, co18_bg, C13O, C18O, dt, fstrat)
O18_hoh, C13_hoh, CO_hoh = wisman.chem_mix_model(
    temp, pres, co, 2*1.2E6, co_bg, c13o_bg, co18_bg, C13O, C18O, dt, fstrat)
print(max(C13))
xlabs = [config.axl['fstrat']]*3
ylabs = [config.axl['co'],config.axl['13c'] ,config.axl['18o']]
xlims = [(0, 1)]*3
ylims = [(50, 20000), (-29, -25), (0, 20)]
fig, axes = scantools.plot_init(
    1, 3, xlabs=xlabs, ylabs=ylabs, xlims=xlims, ylims=ylims)
scantools.plot_add(axes[0], fstrat, CO_noh,
                   color=colors[0], label=r'$n(\textrm{OH})=0$ cm$^{-3}$')
scantools.plot_add(axes[0], fstrat, CO, color=colors[1],
                   label=r'$n(\textrm{OH})=1.2\cdot10^{6}$ cm$^{-3}$')
scantools.plot_add(axes[0], fstrat, CO_hoh, color=colors[2],
                   label=r'$n(\textrm{OH})=2.4\cdot10^{6}$ cm$^{-3}$')
scantools.plot_add(axes[1], fstrat, C13_noh, color=colors[0])
scantools.plot_add(axes[1], fstrat, C13, color=colors[1])
scantools.plot_add(axes[1], fstrat, C13_hoh, color=colors[2])
scantools.plot_add(axes[2], fstrat, O18_noh, color=colors[0])
scantools.plot_add(axes[2], fstrat, O18, color=colors[1])
scantools.plot_add(axes[2], fstrat, O18_hoh, color=colors[2])

axes[0].set_yscale('log')

# ax[0].legend(ncol=3,loc='lower left',bbox_to_anchor=(-0.0,-0.60))
fig.tight_layout()
leg = axes[0].legend(ncol=3, loc='lower center', bbox_to_anchor=(
    0.5, -0.06), bbox_transform=fig.transFigure)

fig.savefig(config.FigDir+'wisman_isotopemodel.pdf', bbox_inches='tight')
