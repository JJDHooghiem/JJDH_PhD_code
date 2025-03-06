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
import scantools

ylabs = [config.axl['th']]*3
xlabs = [config.axl['cl'],config.axl['osd'],config.axl['oh']]
ylims = [(300, 500)]*3
xlims = [(0, 6), (0, 1), (0, 400)]
fig, axes = scantools.plot_init(1, 3, xlabs, ylabs, ylims=ylims, xlims=xlims)

echamy = 'ECHAM5_tpot'
echamkeys = ['Cl', 'O1D', 'OH']
limo.plot_profiles(axes, echamy, echamkeys, interpolated=True, daymean=True)

# axes.set_ylim(20000,1000)
# axes.set_ylim(300, 700)
fig.tight_layout()
axes[0].legend()
fig.savefig(config.FigDir+'limo_ch4_los_spec.pdf')
