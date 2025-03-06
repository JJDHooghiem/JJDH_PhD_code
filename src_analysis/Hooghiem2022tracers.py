#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Don't remove the line below, it is checked by "one to run them all"
# --otrta-p--
# extension p means parallel, s is for single
import lodautil
import config
import scantools

lisa = lodautil.var_select(lodautil.flattened_LISA(), 'd18O(CO)')
colors = config.GruvBoxColors
markers = config.Markers
# Figure 1
xlabs = [config.axl['co'], config.axl['ch4'],config.axl['18o'],config.axl['13c']]
specs=['CO', 'CH4', 'd18O(CO)', 'd13C(CO)']
errors=[2,3,0.5,0.5]
ylabs = [config.axl['th']]*4
fig, axes = scantools.plot_init( 2, 2, xlabs=xlabs, ylabs=ylabs)
for dat, m, c in zip(lodautil.get_dates(lisa), markers, colors):
    data = lodautil.date_select(lisa, dat)
    ykey = 'PT'
    for ax, xkey,er in zip(axes.ravel(),specs,errors):
        ax.errorbar(data[xkey], data[ykey], xerr=er,fmt=m, linestyle='-', color=c, label=dat)
axes[0, 0].legend()
fig.tight_layout()
fig.savefig(config.FigDir+'Hooghiemtracers2022_pot.pdf')

ylabs = [config.axl['alt']]*4
fig, axes = scantools.plot_init( 2, 2, xlabs=xlabs, ylabs=ylabs)
for dat, m, c in zip(lodautil.get_dates(lisa), markers, colors):
    data = lodautil.date_select(lisa, dat)
    ykey = 'Altitude'
    for ax, xkey,er in zip(axes.ravel(), specs,errors):
        ax.errorbar(data[xkey], data[ykey]/1000, xerr=er,fmt=m, linestyle='-', color=c, label=dat)
axes[0, 0].legend()
fig.tight_layout()
fig.savefig(config.FigDir+'Hooghiemtracers2022_alt.pdf')
exit()

xlabs = [ config.axl['co2'] ]*2
ylabs = [ config.axl['18o'], config.axl['13c']]

fig, axes = scantools.plot_init( 1, 2, xlabs=xlabs, ylabs=ylabs)

for dat, m, c in zip(lodautil.get_dates(lisa), markers, colors):
    data = lodautil.date_select(lisa, dat)
    ykey = 'CH4'
    for ax, xkey in zip(axes.ravel(), [ 'd13C(CO)','d18O(CO)']):
        ax.plot(data[xkey], data[ykey], marker=m,
                linestyle='-', color=c, label=dat)
axes[0].legend()
fig.tight_layout()
fig.savefig(config.FigDir+'stico_tr_tr.pdf',
            format='pdf', bbox_inches='tight')


