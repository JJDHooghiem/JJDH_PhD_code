#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Don't remove the line below, it is checked by "one to run them all"
# --otrta-p--
# extension p means parallel, s is for single
"""
This code was written for the analysis presented in the dissertation of Joram Jan Dirk Hooghiem
"""
import config 
import scantools
import lodautil
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
from scan.stico import keeling_co2
xlabs = [config.axl['invco']]*2
ylabs = [r'$\delta$/(\textperthousand)']
xlims = [(0, 0.12)]




def init(**kwargs):
    fig=plt.figure(**kwargs)
    wspace=0.15
    ax2 = fig.add_axes([0.25+wspace/2, 0, 1-wspace-0.25, 1])
    ax1 = fig.add_axes([0.0, 0, 0.25-wspace/2, 1],sharey=ax2)
    # ax2.spines['right'].axis.set_ticks([])
    # mod_spines(ax2)
    ax1.spines['top'].set_color('none')
    ax1.spines['bottom'].set_color('none')
    ax1.spines['left'].set_color('none')
    # ax1.spines['left'].axis.set_ticks([])
    # ax1.spines['bottom'].axis.set_ticks([])
    ax1.spines['top'].axis.set_ticks([])
    # ax2.tick_params('y',labelright=True)

    ax2.spines['top'].set_color('none')
    ax2.spines['right'].set_color('none')
    # ax2.spines['right'].axis.set_ticks([])
    # ax2.spines['top'].axis.set_ticks([])

    # ax.xaxis.set_ticks_position('bottom')

    ax2.xaxis.set_ticks_position('bottom')
    ax2.yaxis.set_ticks_position('left')
    ax1.yaxis.set_ticks_position('right')
    ax1.tick_params('y',labelleft=False,labelright=False)

    # ax1.yaxis.set_ticks_position('right')
    axes_array=np.array([ax1,ax2])
    return fig,axes_array

fig, axes = init(figsize=(4.5,3))
keeling_co2(axes,xlims,mc=True,plot=True,echam_enrich=True)
axes[1].set_xlim(xlims[0])
axes[1].set_ylim(-50,40)
axes[1].set_xlabel(xlabs[0])
axes[1].set_ylabel(ylabs[0])
axes[0].set_xlim(axes[0].get_xlim()[::-1])
# axes[1].set_xlim(xlims[0])
fig.tight_layout()
for ax in axes:
    ax.legend(loc='best')
fig.savefig(config.FigDir+'Hooghiem2021_Keeling2_new_xyer.pdf')
