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

ylabs = [config.axl['th']]
xlabs = [config.axl['colife']]
# xlabs = [r'$n(\ch{OH})$ (y)']
fig, axes = scantools.plot_init(1, 1, xlabs, ylabs)
# limo.colifetime(axes=axes, interpolated=True, experiment='eq1z', linestyle=':')
limo.colifetime(axes=axes, interpolated=True, linestyle='-')

# axes.set_ylim(1000, 0.01)
# axes.set_yscale('log')
# axes.set_xlim(0, 1E-12)
axes.set_ylim(300, 700)
axes.legend()
fig.tight_layout()
fig.savefig(config.FigDir+'limo_colife.pdf')
