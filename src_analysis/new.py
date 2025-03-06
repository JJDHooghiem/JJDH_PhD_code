#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Don't remove the line below, it is checked by "one to run them all"
# --otrta-p--
# extension p means parallel, s is for single
import lodautil
import config
import scantools

lisa = lodautil.var_select(lodautil.flattened_LISA(), 'd18O(CO)')
print(lisa.keys())
colors = config.GruvBoxColors
markers = config.Markers
# Figure 1
xlabs = [config.axl['co'], config.axl['ch4'],config.axl['18o'],config.axl['13c']]

ylabs = [config.axl['th']]*4
fig, axes = scantools.plot_init( 2, 2, xlabs=xlabs, ylabs=ylabs)
for dat, m, c in zip(lodautil.get_dates(lisa), markers, colors):
    data = lodautil.date_select(lisa, dat)
    ykey = 'PT'
    for ax, xkey in zip(axes.ravel(), ['CO', 'CH4', 'd18O(CO)', 'd13C(CO)']):
        ax.errorbar(data[xkey], data[ykey],xerr=data[xkey+' un'], marker=m, linestyle='-', color=c, label=dat)
axes[0, 0].legend()
fig.tight_layout()
fig.savefig(config.FigDir+'stico_lisa_tracers_unc.pdf')
