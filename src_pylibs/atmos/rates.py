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

# rates are typically reported as cm3 per second which is not typically SI unit. IUPAC is okay with it though  
import numpy as np

def rate_arr(A,E,T):
    """
    E is shorthand for E/R 
    to model Arrhenius behaviour of chemmical equations.
    k=k0 * exp(-E/(RT)
    """
    return A*np.exp(-E/T)

    
def rate_3rd(TEMP,NDENS,K_0300,n,K_inf,m,fc=0.6):

    """
    Temp in kelvin, Ndens in cm^-3. n and K_300 are the low pressure limit constants. m and K_inf the high pressure limit.
    As in the compilation of JPL (page 393 (page 2-1, after page 1-378)
    """
    k_0=K_0300*(TEMP/300.)**(-n)
    k_inf=K_inf*(TEMP/300.)**(-m)
    keff=((k_0*NDENS)/(1+((k_0*NDENS)/k_inf)))*fc**((1+(np.log10(k_0*NDENS/k_inf))**2)**(-1))    
    return keff
    

def rate_3rd_iupac(TEMP,NDENS,K_0300,n,K_inf,m,fc=0.6):
    """
    Temp in kelvin, Ndens in cm^-3. n and K_300 are the low pressure limit constants. m and K_inf the high pressure limit.

    According to the meccanism, caaba 4.0, this is a definition used by Wallington2018
    """
    k_0=K_0300*(TEMP/300.)**(-n)
    k_inf=K_inf*(TEMP/300.)**(-m)
    N=0.75-1.27*np.log10(fc)
    keff=((k_0*NDENS)/(1+((k_0*NDENS)/k_inf)))*fc**((1+(np.log10(k_0*NDENS/k_inf)/N)**2)**(-1))    
    return keff

def Rate_Kie(Reaction_I,Temp):
    ''' 
    Change E to B as in most literature
    '''
    rate=[]
    for act,kie,ex in zip(Reaction_I['E'],Reaction_I['KIE'],Reaction_I['A']):
        if act!=0:
            KIE=ex*np.exp(act/Temp)
        else:
            KIE=kie
        rate.append(KIE)
    return rate
