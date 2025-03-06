#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Don't remove the line below, it is checked by "one to run them all"
# --otrta-p--
# extension p means parallel, s is for single
"""
This code was written for the analysis presented in the dissertation of Joram Jan Dirk Hooghiem
"""
import scan.stico as stico
import config
import scantools
xlabs = [config.axl['invco']]*2
ylabs = [config.axl['18o'], config.axl['13c']]
xlims = [(0, 0.12)]*2
fig, axes = scantools.plot_init(1, 2, xlabs, ylabs, xlims=xlims)
stico.keeling_co2(axes,echam_enrich=True)
fig.tight_layout()
axes[0].legend()
axes[1].legend()
fig.savefig(config.FigDir+'stico_keeling_to_co2_new.pdf')
