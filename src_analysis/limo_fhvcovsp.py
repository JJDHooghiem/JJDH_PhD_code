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
xlabs=[config.axl['co'],config.axl['fco2co'],config.axl['kco2']]
ylabs=[config.axl['p']]*3
xlims=[(0, 100),(0, 100),(0, 0.3E-12)]
ylims=[(100000, 100)]*3
fig,axes=scantools.plot_init(1,3,xlabs=xlabs,ylabs=ylabs,xlims=xlims,ylims=ylims)
limo.plot_FHVCOvsP(fig,axes,interpolated=True)

for i in range(0, len(axes)):
    axes[i].set_yscale('log')

handles, labels = scantools.getUniqueLegend(axes[0])
fig.tight_layout()
axes[0].legend(handles=handles, labels=labels, ncol=5, loc='lower center', bbox_to_anchor=(0.5, -0.10), bbox_transform=fig.transFigure)
fig.savefig(config.FigDir+'limo_fhvcovsp.pdf',format='pdf',bbox_inches='tight')
