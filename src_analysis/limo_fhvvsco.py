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

xlabs=[config.axl['co']]
ylabs=[config.axl['fco2co']]
xlims=[(10,60)]
ylims=[(0,1)]
fig,axes=scantools.plot_init(1,1,xlabs=xlabs,ylabs=ylabs,xlims=xlims,ylims=ylims)
limo.plot_fhvvsco(axes, interpolated=False)

# Layout and text
handles, labels = scantools.getUniqueLegend(axes)
fig.tight_layout()
axes.legend(handles=handles, labels=labels)
plt.savefig(config.FigDir+'limo_fhvvsco.pdf', format='pdf', bbox_inches='tight')
