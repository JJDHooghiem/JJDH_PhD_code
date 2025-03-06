#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Don't remove the line below, it is checked by "one to run them all"
# --otrta-p--
# extension p means parallel, s is for single
"""
This code was written for the analysis presented in the dissertation of Joram Jan Dirk Hooghiem
"""
import scantools
import config
import scan.limo as limo

for key,xlim in zip(['ch4','co2','co'],[(600, 2000), (390, 410), (0, 120)]):
    xlabs=[config.axl[key]]*9
    ylabs=[config.axl['ph']]*9
    xlims=[xlim]*9
    ylims=[(200,0)]*9
    fig,axes=scantools.plot_init(3,3,xlabs=xlabs,ylabs=ylabs,xlims=xlims,ylims=ylims)
    limo.plot_tracer_profiles(axes,key.upper())
    fig.tight_layout()
    fig.savefig(config.FigDir+'limo_profiles_%s.pdf' % key.upper())

