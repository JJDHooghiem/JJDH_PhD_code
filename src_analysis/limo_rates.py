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

xlabs = [config.axl['kch4cl'], config.axl['kch4oh'], config.axl['kcooh' ]]
ylabs = [config.axl['ph']]*3


ylims = [(20000, 0)]*3

fig, axes = scantools.plot_init( 1, 3, xlabs=xlabs, ylabs=ylabs,  ylims=ylims)
data_dif = limo.plot_rel_rates(axes)
fig.tight_layout()
fig.tight_layout(rect=[0, 0.2, 1, 1])
axes[1].legend(ncol=4, loc='lower center', bbox_to_anchor=(0.5, 0.0), bbox_transform=fig.transFigure)
plt.savefig(config.FigDir+'limo_rates.pdf', format='pdf', bbox_inches='tight')

plt.close()
xlabs = [config.axl['DT'], config.axl['Dph'], config.axl['Dph'], config.axl['DT']]

ylabs = [config.axl['ph'], config.axl['ph'],config.axl['dco'], config.axl['dco']]


ylims = [(20000, 0), (20000, 0)]

fig, axes = scantools.plot_init( 2, 2, xlabs=xlabs, ylabs=ylabs,  ylims=ylims)
data_dif = limo.plot_dtdp(axes)
fig.tight_layout()
fig.tight_layout(rect=[0, 0.2, 1, 1])

axes[1, 0].legend()
axes[1, 1].legend()
plt.savefig(config.FigDir+'limo_dtdp.pdf', format='pdf')
