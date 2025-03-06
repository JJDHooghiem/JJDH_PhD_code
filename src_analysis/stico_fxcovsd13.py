#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Don't remove the line below, it is checked by "one to run them all"
# --otrta-p--
# extension p means parallel, s is for single
import scan.stico as stico
import config
import scantools

xlabs = [config.axl['fch4co'], config.axl['fco2co'], config.axl['fosdco'], config.axl['fres']]
# ylabs = ['$\delta^{13}\ch{C}(\ch{CO})$']*4
ylabs = [config.axl['ph']]*4
ylabel = 'p'
ylims = [(200, 0)]*4
xlims=[(0,0.8),(0,0.8),(0,0.06),(0,0.8)]
# ylabel='d13C(CO)'

fig, axes = scantools.plot_init(2, 2, xlabs=xlabs, ylabs=ylabs,xlims=xlims, ylims=ylims)
stico.echamfxinco(axes, ylabel=ylabel, linestyle='-', marker='o')
# stico.echamfxinco(axes, interpolated=False, ylabel='d13C(CO)', linestyle=':', marker='d')
# stico.echamfxinco(axes, experiment='eq1z', ylabel=ylabel, linestyle=':', marker='d')

fig.tight_layout()
axes[0,1].legend()
fig.savefig(config.FigDir+'stico_fxcovsd13.pdf', bbox_inches='tight')



ylabs = [config.axl['18oco']]*4
ylims=[(-3,13)]*4

fig, axes = scantools.plot_init(1, 3, xlabs=xlabs, ylabs=ylabs,xlims=xlims,ylims=ylims)
stico.echamfxinco(axes, ylabel='d18O(CO)')
fig.tight_layout()
axes[0].legend()

fig.savefig(config.FigDir+'stico_fxcovsd18.pdf', bbox_inches='tight')
