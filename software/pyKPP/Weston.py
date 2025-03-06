#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 13:10:26 2019

@author: joram
"""

import numpy as np
import matplotlib.pyplot as plt
#%%

TEMP=np.array([200.,300.,400.])
##-k1p-##
Keq=np.array([1.056,1.0256,1.0133])
kd=np.array([0.9937,1.0008,0.9978])
fr=kd*Keq
##-k1pp-##
Keq_pp=np.array([0.9699,0.9772,0.9823])
kd_pp=np.array([1.0239,1.0272,1.0206])
fr_pp=Keq_pp*kd_pp


weston_perMil=(fr*(1-kd_pp*0.00204800952)-1)*1000
#%%
R_MAJ=6.34E15
#%%

