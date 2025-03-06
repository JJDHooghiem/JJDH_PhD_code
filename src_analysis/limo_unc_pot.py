#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This code was written for the analysis presented in the dissertation of Joram Jan Dirk Hooghiem

Computes the uncertainty in potential temperature computed from radiosonde data.
"""
import numpy as np
import atmos 

pnot=atmos.P_sea
R_c = 2/7. 

def dth_dp(temp,pres):
    """helper for dp dt.

    Parameters
    ----------
    temp : TODO
    pres : TODO

    Returns
    -------
    TODO

    """
    dp  = (-R_c*temp*(pnot/pres)**R_c)/pres
    return dp 

def dth_dt(pres):
    """TODO: Docstring for dth_dt.

    Parameters
    ----------
    press : TODO

    Returns
    -------
    TODO

    """
    dt=(pnot/pres)**R_c
    return dt

def th_unc(temp,pres,u_t=0.5,u_p=60):
    """TODO: Docstring for th_unc.

    Parameters
    ----------
    arg1 : TODO
    Returns
    -------
    TODO

    """
    u_th=np.sqrt((u_t**2)*dth_dt(pres)**2+(u_p**2)*dth_dp(temp,pres)**2)
    return u_th
T=220
p=5000
for u_t,u_p in [(0.3,0.3),(0.3,0.3),(0.2,0.5)]:
    print(th_unc(T,p,u_t,u_p))


# T=220
# p=20000
# for u_t,u_p in [(0.3,0.3),(0.3,1),(0.2,0.5)]:
#     print(th_unc(T,p,u_t,u_p))

