#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Don't remove the line below, it is checked by "one to run them all"
# --otrta-p--
# extension p means parallel, s is for single
"""
This code was written for the analysis presented in the dissertation of Joram Jan Dirk Hooghiem
"""
import lodautil
import scantools
import config
import numpy as np
data_info = lodautil.get_headers()
data_sets = lodautil.LISA_load()
table = open(config.TabDir+'lisa_flight_info.tex', 'w')


pieces_info = ["Launch Time", "Launch latitude", "Launch longitude",
               "Launch Altitude", "Radiosonde"]
deg = "$^{\circ}$"
for key in sorted(data_info.keys()):
    info = []
    for line in data_info[key].split('\n'):
        if any(pi in line for pi in pieces_info):
            info.append(line.split(": ")[1].replace(' UTC', '').replace(
                ' m', '').replace(' N', '').replace(' E', '').replace('m10', 'M10').replace('imet', 'iMet'))
    info.append(len(data_sets[key]))
    prec = np.array([0, 3, 3, 1, 0, 0])
    post = np.array(['', deg, deg, '', '', ''])
    scantools.npa_to_tex_table(info, prec, table, post=post)
