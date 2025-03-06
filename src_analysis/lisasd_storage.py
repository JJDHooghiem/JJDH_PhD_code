#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Don't remove the line below, it is checked by "one to run them all"
# --otrta-p--
# extension p means parallel, s is for single
import matplotlib as mpl
import numpy as np
import config
import scan.lisasd as lisasd
import scantools

# ==============================================================================
#
#   Making plots
#
# ==============================================================================
resdatalowmlf, resdatalowted, resdatamlf, resdatated = lisasd.AnalyseStorage()

index = np.linspace(
    1, len(resdatated['CO2(ppm)']), len(resdatated['CO2(ppm)']))
xlabs = [config.axl['sno']]*4
ylabs = [config.axl['dco2'], config.axl['dch4'], config.axl['dco'], config.axl['dh2o']]

fig, axes = scantools.plot_init(2, 2, xlabs=xlabs, ylabs=ylabs)
colors = config.GruvBoxColors
g = colors[2]
b = colors[3]
# ms=8
axes[0, 0].errorbar(index, resdatamlf['CO2(ppm)'], color=g, fmt='o')  # ,markersize=ms)
axes[0, 0].errorbar(index, resdatated['CO2(ppm)'], color=b, fmt='o')  # ,markersize=ms)
axes[0, 1].errorbar(index, resdatamlf['CH4(ppb)'], color=g, fmt='o')  # ,markersize=ms)
axes[0, 1].errorbar(index, resdatated['CH4(ppb)'], color=b, fmt='o')  # ,markersize=ms)
axes[1, 0].errorbar(index, resdatamlf['CO(ppb)'], color=g, fmt='o')  # ,markersize=ms)
axes[1, 0].errorbar(index, resdatated['CO(ppb)'], color=b, fmt='o')  # ,markersize=ms)
axes[1, 1].errorbar(index, resdatamlf['H2O'], color=g, fmt='o')  # ,markersize=ms)
axes[1, 1].errorbar(index, resdatated['H2O'], color=b, fmt='o')  # ,markersize=ms)

index = np.array([6, 7])

axes[0, 0].errorbar(index, resdatalowmlf['CO2(ppm)'], color=g, fmt='d')  # ,markersize=ms)
axes[0, 0].errorbar(index, resdatalowted['CO2(ppm)'], color=b, fmt='d')  # ,markersize=ms)
axes[0, 1].errorbar(index, resdatalowmlf['CH4(ppb)'], color=g, fmt='d')  # ,markersize=ms)
axes[0, 1].errorbar(index, resdatalowted['CH4(ppb)'], color=b, fmt='d')  # ,markersize=ms)
axes[1, 0].errorbar(index, resdatalowmlf['CO(ppb)'], color=g, fmt='d')  # ,markersize=ms)
axes[1, 0].errorbar(index, resdatalowted['CO(ppb)'], color=b, fmt='d')  # ,markersize=ms)
axes[1, 1].errorbar(index, resdatalowmlf['H2O'], color=g, fmt='d')  # ,markersize=ms)
axes[1, 1].errorbar(index, resdatalowted['H2O'], color=b, fmt='d')  # ,markersize=ms)

index = np.linspace(1, 7, 7)
for i in range(0, 2):
    axes[0, i].set_xlim([index[0]-0.5, index[-1]+0.5])
    axes[1, i].set_xlim([index[0]-0.5, index[-1]+0.5])
    axes[1, i].set_xticks([1, 2, 3, 4, 5, 6, 7])
    axes[0, i].set_xticks([1, 2, 3, 4, 5, 6, 7])

axes[1, 1].set_ylim([-0.2, 1.4])


handles = []
markers = ['o', 'o', 'd', 'd']
labels = ['MLF', 'Tedlar',
          'MLF (low mole fraction)', 'Tedlar (low mole fraction)']
colors = [g, b, g, b]
for m, l, c in zip(markers, labels, colors):
    handles.append(mpl.lines.Line2D( [], [], marker=m, label=l, linestyle='', color=c))
#lgd=axes_array[-1,0].legend(handles=handles, bbox_to_anchor=(-0.0, -0.35, 0., -.35),loc=3, frameon=True, ncol=2, numpoints=1,borderaxespad=0.)
axes[0, 0].legend(handles=handles)
fig.tight_layout()
# fig.subplots_adjust(wspace=0.3, hspace=0.3)
fig.savefig(config.FigDir+'lisasd_storage.pdf', bbox_inches="tight")
