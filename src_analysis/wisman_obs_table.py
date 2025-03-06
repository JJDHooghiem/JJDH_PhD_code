#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Don't remove the line below, it is checked by "one to run them all"
# --otrta-p--
# extension p means parallel, s is for single
from lodautil import LISA_load
import config
# from lodautil import AirCore_load
# =============================================================================
# Select a plot_style
# =============================================================================

# mpl.style.use('/home/joram/.matplotlib/matplotlibrc/presentation.mplstyle')
# mpl.style.use('/home/joram/.matplotlib/stylelib/paper_copernicus.mplstyle')
#os.environ["PATH"] += os.pathsep + '/Library/TeX/texbin/'


LISA = LISA_load()
table = '''P (05 Sep) & {0:.1f} & {1:.1f} & {2:.0f} &  {3:.1f}  & {4:.1f} \\\\
B (06 Sep) & {5:.1f} & {6:.1f} & {7:.0f} &  {8:.1f} & {9:.1f} \\\\
'''.format(
    LISA['20170905']['Altitude'][0]/1000,
    LISA['20170905']['PT'][0],
    LISA['20170905']['CO'][0],
    LISA['20170905']['d13C(CO)'][0],
    LISA['20170905']['d18O(CO)'][0],
    LISA['20170906']['Altitude'][0]/1000,
    LISA['20170906']['PT'][0],
    LISA['20170906']['CO'][0],
    LISA['20170906']['d13C(CO)'][0],
    LISA['20170906']['d18O(CO)'][0])
with open(config.TabDir+'wisman_plumetable.tex', 'w') as tex:
    tex.write(table)
    # print table
    tex.close()
