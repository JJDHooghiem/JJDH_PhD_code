"""
Author: Joram Jan Dirk Hooghiem

This code was written for the analysis presented in the disseration of Joram Jan Dirk Hooghiem
Functions that do the core analysis are presented in here.  

This program is free software: you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software Foundation, 
version 3. This program is distributed in the hope that it will be useful, but 
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS 
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. 

You should have received a copy of the GNU General Public License along with this 
program. If not, see <http://www.gnu.org/licenses/>.
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from stisolib import calc_d17o_mif
from stisolib import calc_mif


def dC13CO2(CO2):
    """TODO: Docstring for dC13CO2.
    relationship used in 
    Beale2016 based on data from assonov et al. 
    :CO2: mole fraction
    :returns: TODO
    CO2 is converted to ppm internally
    """
    CO2 = CO2*1E6
    dc13 = 6.47*1E3/CO2-25.3
    return dc13


def dO18CO2(N2O):
    """TODO: Docstring for dO18CO2.
    :args:N2O mole fraction 
    :returns: d18O in per mil
    ! the N2O mole fraction is transformed to ppb internally
    not detrended 
    """
    N2O = N2O*1E9
    d18O = -0.0157*N2O+46.2416
    return d18O


def ch42n2o(CH4):
    """TODO: Docstring for ch42n2o.
    own fit from Mrozek data. update with values 
    ! the CH4 mole fraction is transformed to ppb internally
    :arg1: TODO
    :returns: TODO
    """
    CH4 = CH4*1E9
    N2O = -3.55084031e-07*CH4**3+1.42606218e-03*CH4**2-1.60477288*CH4+6.52866133e+02
    return N2O*1E-9


def N2O2D17(N2O):
    """TODO: Docstring for dO18CO2.
    :args:N2O mole fraction 
    :returns: D18 in per mil
    ! the N2O mole fraction is transformed to ppb internally
    ! relation from thesis by Dorota Mrozek page 70
    """
    N2O = N2O*1E9
    D17o = -0.0224*N2O+6.9932
    return D17o


def CO2iso(CO2, CH4):
    """TODO: Docstring for function.

    :CO2 CH4, mole fractions
    :returns: deltavalues

    """
    d13C = dC13CO2(CO2)
    N2O = ch42n2o(CH4)
    d18O = dO18CO2(N2O)
    d17O = calc_d17o_mif(d18O, N2O2D17(N2O))
    return d13C, d17O, d18O
