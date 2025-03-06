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
import scantools.plotutil
from scipy.stats import spearmanr

lisa = lodautil.var_select(lodautil.flattened_LISA(), 'd18O(CO)')

co = []
c13 = []
o18 = []
for f in lodautil.get_dates(lisa):
    LISA = lodautil.date_select(lisa, f)
    COIRMS = LISA['CO']
    C13 = LISA['d13C(CO)']
    O18 = LISA['d18O(CO)']
    for c1, c2, c3 in zip(COIRMS, C13, O18):
        co.append(c1)
        c13.append(c2)
        o18.append(c3)

co, c13, o18 = zip(*sorted(zip(co, c13, o18)))
co = 1/np.array(co)
c13 = np.array(c13)
o18 = np.array(o18)
c13 = c13[np.isfinite(co)]
o18 = o18[np.isfinite(co)]
co = co[np.isfinite(co)]

xlabs = [config.axl['invco']]*2
ylabs = [config.axl['13c'], config.axl['18o']]
xlims = None
ylims = None
fig, axes = scantools.plot_init(1, 2, xlabs=xlabs, ylabs=ylabs, xlims=xlims, ylims=ylims)

scantools.statplot(axes[0], co, c13)
scantools.statplot(axes[1], co, o18)
for ax in axes.ravel():
    ax.legend()
fig.tight_layout()
fig.savefig(config.FigDir+'wisman_keeling_contamination.pdf')

stat, p = spearmanr(co, c13)
print(p)
stat, p = spearmanr(co, o18)
print(p)
