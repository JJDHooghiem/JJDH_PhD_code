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


def co_3step_OH(press, temp):
    #   ! = G4110 ===== CO+OH =======================================================
    #   !
    #   ! reaction rate  k_CO_OH = (1.57E-13 + cair*3.54E-33)
    #   !
    #   !#----- older versions -----
    #   !#
    #   !#- 2nd order fit -----------------------------------------------------------
    #   !#(as p0 * x**2 + p1 * x + p2) !#  r_G4110_16k_18k    = ( -3.099415E-13_dp * (press ** 2) &
    #   !#                     + 5.724561E-08_dp * press &
    #   !#                     + 9.881126E-01_dp )
    #   !#  r_G4110_16k_17k    = ( -3.273918E-13_dp * (press ** 2) &
    #   !#                     + 7.650639E-08_dp * press &
    #   !#                     + 9.954188E-01_dp )
    #   !#  e_G4110_dc17O = (1.0_dp / r_G4110_16k_17k - 1.0) - &
    #   !#                  (1.0_dp / r_G4110_16k_18k - 1.0) * 0.5281_dp
    #   !#
    #   !#- constant values ---------------------------------------------------------
    #   !#  r_G4110_16k_18k = 1 - 10.0_dp / 1000.0_dp
    #   !#  r_G4110_16k_17k = 1 - 1.28_dp / 1000.0_dp
    #   !#
    #   ! ----- 3-step parameterisation ( 2005.JPCRD34.Troe,etal ) -----
    #   !
    #   ! low/high-pressure range rate koefficients
    k_G4110_k0 = 1.661E-11*np.exp(-8050./temp) + 1.494E-12 * \
        np.exp(-2300./temp) + 1.677E-13*np.exp(-030./temp)
    k_G4110_ki = 2.042E-09*np.exp(-7520./temp) + 1.827E-11 * \
        np.exp(-1850./temp) + 1.328E-12*np.exp(-120./temp)
#   !
#   ! pressure modifier: A0 = 5.9, TS = 161K, pressure in bars
    k_G4110_atp = 5.9 * np.exp(-temp/161) * (press*1E-5)
#   !
#   ! broadening factor calculation
    k_G4110_fc = 0.49 + 0.51 * np.exp(-temp/300.0)
    k_G4110_fx = k_G4110_fc**(1.0/(1.0 + (np.log10(k_G4110_atp *
                                                   k_G4110_k0/(k_G4110_ki - k_G4110_k0)))**2))
#   !
#   ! fractionation factors from enrichments
#   ! careful, enrichment in educt (CO) !
#   !
  # ! - 13CO - specify enrichments here

    a_G4110_k13a = 1.0-(00.00 / 1E3)
    a_G4110_k13b = 1.0-(-07.66 / 1E3)
    a_G4110_k13c = 1.0-(23.07 / 1E3)
#   ! - C18O - specify enrichments here
    a_G4110_k18a = 1.0-(00.00 / 1E3)
    a_G4110_k18b = 1.0-(-11.90 / 1E3)
    a_G4110_k18c = 1.0-(-05.74 / 1E3)
#   !
#   ! - C17O - specify enrichments here
    a_G4110_k17a = 1.0-(00.00 / 1E3)
    a_G4110_k17b = 1.0-(-04.95 / 1E3)
    a_G4110_k17c = 1.0-(06.04 / 1E3)
#   !
#   ! channel rates
    k_G4110_x = k_G4110_atp * (k_G4110_k0 / (k_G4110_ki - k_G4110_k0))
    k_G4110_kab = k_G4110_k0 * \
        (1.0 - k_G4110_fx * k_G4110_x / (1.0 + k_G4110_x))
    k_G4110_kac = k_G4110_atp * k_G4110_k0 * k_G4110_fx * \
        (1.0 + k_G4110_x / k_G4110_atp) / (1.0 + k_G4110_x)
#   ! regular rate
    k_G4110_kr = k_G4110_kab + k_G4110_kac
#   !
#   ! substituted rates
    k_G4110_k18 = a_G4110_k18a * \
        (a_G4110_k18b * k_G4110_kab + a_G4110_k18c * k_G4110_kac)
    k_G4110_k17 = a_G4110_k17a * \
        (a_G4110_k17b * k_G4110_kab + a_G4110_k17c * k_G4110_kac)
#   !
    k_G4110_k13 = a_G4110_k13a * \
        (a_G4110_k13b * k_G4110_kab + a_G4110_k13c * k_G4110_kac)
#   ! final fractionation factors
#     r_G4110_16k_18k = k_G4110_kr / k_G4110_k18
#     r_G4110_16k_17k = k_G4110_kr / k_G4110_k17
#   ! capital delta 17 enrichment in educt (CO)
#     e_G4110_dc17O = r_G4110_16k_17k / r_G4110_16k_18k**0.5281_dp - 1.0_dp
#   !
    # rename to what i know
    k_oh_co = k_G4110_kr
    k_oh_13co = k_G4110_k13
    k_oh_c18o = k_G4110_k18
    k_oh_c17o = k_G4110_k17

    return k_oh_co, k_oh_13co, k_oh_c17o, k_oh_c18o


def alpha_temp(A, B, TEMP):
    '''
    Calculates a temperature dependent fractionation factor, assuming
    alpha = A np.exp( - B /T )
    Note that when in literature a kie is definec, kie = 1 /alpha
    thus when using KIE = C np.exp( B/T )
    this function should be evaluated as 
    alpya(1/C , B , T)
    '''
    return A * np.exp(-B / TEMP)

# =============================================================================
# for the isotopes
# =============================================================================
#
# Isotope ratio as from Coplen
#
# In principle this are correct, but would be wrong to use with craig assonov definitions.
#
# As oh is constant here, it does not effect the lifetime of OH.
#


def gromov_ozone(T, p):
    """TODO: Docstring for gromov_ozone.
    Derives the ozono isotopic composition as in gromov2013
    see table 3.5 page 46
    Request pressure in Pa
    And Temperature in in K
    it doesn't yield the same values as in figure 3.4. 

    """
    T_not = 300.0
    # specific to O17 table 3.5 gromov
    p_half = 2.6E5
    enrich_not = 98.6
    b = 0.9244
    s_1 = 2.8E-3
    s_2 = -0.118
    O3d17 = ((1+p/p_half)**(-1))*enrich_not*(b+s_1*(T-T_not)+s_2*((T_not/T)-1))

    # specific to O17 table 3.5 gromov
    p_half = 2.02E5
    enrich_not = 113.7
    b = 0.9176
    s_1 = 3.7E-3
    s_2 = -0.105
    O3d18 = ((1+p/p_half)**(-1))*enrich_not*(b+s_1*(T-T_not)+s_2*((T_not/T)-1))
    return O3d17, O3d18

def inverse(x, a, b, c):
    """
    a relation used in the fractionation factors calculated below
    """
    return 1/(1+a+b*x+c*x**2)

def alpha_oh_c13(pres):
    '''c13
    takes in pressure in Pa
    data taken from Sergey Gromov Thesis:STABLE ISOTOPE COMPOSITION OF ATMOSPHERIC CARBON MONOXIDE: A MODELLING STUDY
    Pres in mbar for convinient integration with the rest of the model
    From Sergey conventional aproach table 3.6, for units of pressure in bar

    CO+OH kie	pressure dependend

    (a+b*p+c*p^2 + 1)**-1

                a	         b	           c
    C13	-0.00655     0.02269	       -0.00947
    O18	-0.01191	     0.00603	       -0.00341
    O17	-0.00472	     0.00534	       -0.00226

    '''
    pres = pres/100000.  # compute pressure in bar according to model parameters
    alpha = inverse(pres, -0.00655, 0.02269, -0.00947)
    return alpha

def alpha_oh_o18(pres):
    '''o18
    data taken from Sergey Gromov Thesis:STABLE ISOTOPE COMPOSITION OF ATMOSPHERIC CARBON MONOXIDE: A MODELLING STUDY
    Pres in mbar for convinient integration with the rest of the model
    From Sergey conventional aproach table 3.6, for units of pressure in bar

    CO+OH kie	pressure dependend

    (a+b*p+c*p^2 +1)**-1

                a	         b	           c
    C13	-0.00655     0.02269	       -0.00947
    O18	-0.01191	     0.00603	       -0.00341
    O17	-0.00472	     0.00534	       -0.00226

    '''
    pres = pres/100000.  # compute pressure in bar according to model parameters
    alpha = inverse(pres, -0.01191,     0.00603, -0.00341)
    return alpha

def alpha_oh_o17(pres):
    ''' o17
    data taken from Sergey Gromov Thesis:STABLE ISOTOPE COMPOSITION OF ATMOSPHERIC CARBON MONOXIDE: A MODELLING STUDY
    Pres in mbar for convinient integration with the rest of the model
    From Sergey conventional aproach table 3.6, for units of pressure in bar

    CO+OH kie	pressure dependend

    (a+b*p+c*p^2 +1)**-1

                a	         b	           c
    C13	-0.00655     0.02269	       -0.00947
    O18	-0.01191	     0.00603	       -0.00341
    O17	-0.00472	     0.00857	       -0.00406

    '''
    pres = pres/100000.  # compute pressure in bar according to model parameters
    alpha = inverse(pres, -0.00472,    0.00857,    -0.00406)
    return alpha

def reduced_mas(m1, m2):
    return (m1*m2)/(m1+m2)

def alpha_mu(m1, m2, m2p):
    """
    calculates alpha as the sqrt of the ratio of the squared reduced mass. 
    this the compute the difference in thermal velocity and thus reduced collision frequency. 

    """
    mu_p = reduced_mas(m1, m2p)
    mu = reduced_mas(m1, m2)
    return 1.0/np.sqrt(mu_p/mu)


