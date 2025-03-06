#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Don't remove the line below, it is checked by "one to run them all"
# --otrta-p--
# extension p means parallel, s is for single
"""
This code was written for the analysis presented in the dissertation of Joram Jan Dirk Hooghiem
"""
import numpy as np
import scan.wisman as wisman
from lodautil import LISA_load

data = LISA_load()

iso_un = 0.5
mole_un = 0.002

CO = data['20170905']['CO'][0]
C13O = data['20170905']['d13C(CO)'][0]
C18O = data['20170905']['d18O(CO)'][0]

CO_bg = data['20170906']['CO'][0]
C13O_bg = data['20170906']['d13C(CO)'][0]
CO18_bg = data['20170906']['d18O(CO)'][0]

O18_Measurements = np.array([CO18_bg, C18O])
C13_Measurements = np.array([C13O_bg, C13O])
CO_Measurements_inf = 1000/np.array([CO_bg, CO])

CO_err = np.sqrt((mole_un**2)*CO_Measurements_inf**2)
O18_Measurements_err = np.array([iso_un, iso_un])
C13_Measurements_err = np.array([iso_un, iso_un])
wisman.mixing_keeling(CO_Measurements_inf, O18_Measurements,
                      C13_Measurements, CO_err, O18_Measurements_err, C13_Measurements_err)
