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
import numpy as np
from .Standards import *


def delta_to_ratio(delta, standard):
    """
    takes a delta value and the reference material and calculates the ratio. Assumed delta unit is per mil
    """
    r = Isotope_Standards_ratios[standard]
    ratio = ((delta/1000.)+1)*r
    return ratio


def ratio_to_delta(ratio, standard):
    """
    Takes in istope ratio and standard, and returns the delta value in per mil.
    example:
    >>>ratio_to_delta(0.01122,'VPDB13')
    if a molecular ratio, is provide, the ratio should have been corrected for the abundance of the molecule, e.g.
    18r(CO2) = 1/2 * [OCQ]/[OCO]
    """
    r = Isotope_Standards_ratios[standard]
    delta = (ratio/r-1)*1000
    return delta


def stat_distr_simple_main(dvalue, standard, weight):
    """ Calculates the statistical distribution
    of molecules. 
    needs:
    dvalue or deltavalue in per mill
    standard is the standard to which the enrichment(depletion) is expresend
    weight, the amount of places the molecule occupies. example:
    in ozone, OOO, there are 3 places with an oxygen atom so weight =3 
    """
    r = delta_to_ratio(dvalue, standard)
    x = 1.0/(1.0+r)**weight

    return x


def stat_distr_simple(dvalue, standard, weight):
    """ Calculates the statistical distribution
    of molecules. 
    needs:
    dvalue or deltavalue in per mill
    standard is the standard to which the enrichment(depletion) is expresend
    weight, the amount of places the molecule occupies. example:
    in ozone, OOO, there are 3 places with an oxygen atom so weight =3 
    """
    r = delta_to_ratio(dvalue, standard)
    x = weight * r/(1+r)**weight
    return x


def stat_distr_full_O(d17O, d18O, weight):
    """ Calculates the statistical distribution.
    of an isotopic compound in a molecule, currently only
    VSMOW is supported 
    number densities can be calculated usin 
    n(molecule17) = n(molecule) * x17 
    returns: 
    """
    r17 = delta_to_ratio(d17O, "VSMOW17")
    r18 = delta_to_ratio(d18O, "VSMOW18")
    R_sum = 1 + r17 + r18
    x17 = weight * r17 / R_sum**weight
    x18 = weight * r18 / R_sum**weight
    x16 = 1 / R_sum**weight
    return x16, x17, x18


def stat_distr_full_C(d13C, weight):
    """ Calculates the statistical distribution.
    of an isotopic compound in a molecule, currently only
    VSMOW is supported 
    number densities can be calculated usin 
    n(molecule17) = n(molecule) * x17 
    returns: 
    """
    r13 = delta_to_ratio(d13C, "VPDB13")
    R_sum = 1 + r13
    x13 = weight * r13 / R_sum**weight
    x12 = 1 / R_sum**weight
    return x12, x13


def stat_distr_full_CO(d13C, d17O, d18O):
    """ Calculates the statistical distribution.
    of an isotopic compound in a molecule, currently only
    VSMOW is supported 
    number densities can be calculated usin 
    n(molecule17) = n(molecule) * x17 
    returns: 
    """
    r13 = delta_to_ratio(d13C, "VPDB13")
    r17 = delta_to_ratio(d17O, "VSMOW17")
    r18 = delta_to_ratio(d18O, "VSMOW18")
    R_sum = (1 + r13) * (1 + r17 + r18)
    x26 = 1 / R_sum

    x36 = r13 / R_sum
    x28 = r18 / R_sum
    x27 = r17 / R_sum

    x37 = r13 * r17 / R_sum
    x38 = r13 * r18 / R_sum
    return x26, x36, x28, x27, x37, x38


def stat_distr_full_CO2(d13C, d17O, d18O):
    """ Calculates the statistical distribution.
    of an isotopic compound in a molecule, currently only
    VSMOW is supported 
    number densities can be calculated usin 
    n(molecule17) = n(molecule) * x17 
    returns: 
    """
    weightC = 1
    weightO = 2
    r13 = delta_to_ratio(d13C, "VPDB13")
    r17 = delta_to_ratio(d17O, "VSMOW17")
    r18 = delta_to_ratio(d18O, "VSMOW18")
    R_sum = (1 + r13)**weightC * (1 + r17 + r18)**weightO
    x626 = 1 / R_sum

    x636 = weightC * r13 / R_sum
    x627 = weightO * r17 / R_sum
    x628 = weightO * r18 / R_sum

    x637 = weightO * weightC * r13 * r17 / R_sum
    x638 = weightO * weightC * r13 * r18 / R_sum

    x728 = weightO * r17 * r18 / R_sum
    x738 = weightO * weightC * r17 * r18 * r13 / R_sum

    x727 = r17**2 / R_sum
    x828 = r18**2 / R_sum

    x737 = r13 * r17**2 / R_sum
    x838 = r13 * r18**2 / R_sum
    return x626, x636, x628, x627, x637, x638, x728, x738, x727, x828, x737, x838


mdf_slope = 0.52

def calc_mif_approx(d17o, d18o):
    mif = d17o - mdf_slope * d18o
    return mif

def calc_mif(d17o,d18o):
    mif=1000*np.log(1+d17o/1000)-0.52*np.log(1+d18o/1000)*1000
    return mif

def calc_d17o_mif(d18o, mif):
    """
    assuming mif (vsmow)
    """
    d17o =(np.exp(((mif/1000)+0.52*np.log(1+d18o/1000)))-1)*1000
    return d17o


def calc_d17o_mdf_approx(d18o):
    """
    assuming mdf (vsmow)
    """
    d17o = mdf_slope * d18o
    return d17o

def calc_d17o_mdf(d18o):
    d17o=1000*((1+d18o/1000)**mdf_slope-1)
    return d17o

def calc_d18o_mdf(d17o):
    d18o=1000*((1+d17o/1000)**(1/mdf_slope)-1)
    return d18o

def calc_mif_cor(mif):
    """
    Calculates the correction to 13C based on MIF with respect to VSMOW.
    e.g. mif = d17o - 0.52 * d18o 

    """
    error=-mif/29.6
    return error


def ch4_to_c13(CH4, time):
    '''
    Function that transforms methane mole fraction of methane into C13 (CH4) in per mill VPDB


    Parameters
    ----------
    CH4 : array_like
        Array containing mole fraction to be calculated
    time : string
        string specifying the type of profile:
        'wv'    'Winter Vortex'
        'w'     'Winter_non_vortex'
        's'     'Summer'
        'es'    'Extended summer'   

    Returns
    -------
    C13(CH$) : array_like
        the modelled arctic profile of c13ch4

    '''

    key = time
    # optained from fits through balloon data from Rockmann 2011 
    opt = {
        'wv': [-3.54574878461, -0.059925867126, 2.90405008109e-05, -5.18519551365e-09],
        'w': [-3.497122633, -0.0723283471856, 4.4351782608e-05, -9.99956105036e-09],
        's': [-4.10876345315, -0.0611286350897, 3.12909478767e-05, -6.02819339316e-09],
        'es': [-1.63863220447, -0.0673637996103, 3.65518611225e-05, -7.45099020146e-09]}
    if type(CH4) == np.ndarray:
        C13_CH4 = opt[key][0]+opt[key][1]*CH4 + \
            opt[key][2]*CH4**2+opt[key][3]*CH4**3
    else:
        CH4 = np.array(CH4)
        C13_CH4 = opt[key][0]+opt[key][1]*CH4 + \
            opt[key][2]*CH4**2+opt[key][3]*CH4**3
    return C13_CH4
