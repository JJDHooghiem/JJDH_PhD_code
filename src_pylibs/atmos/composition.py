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
import stisolib

xO2 = 0.2095  # mole fraction
O1Dd18 = 150.0  # per mil per mil \citep{zahn2006} figure 1
O1Dd17 = stisolib.calc_d17o_mif(O1Dd18, 41)
O2d18 = 23.8  # per mil
O2d17 = 11.9  # per mil
Od18 = -55.3  # per mill \citep{Zahn2006}
Od17 = -27.58  # per mill
O3d18 = 120.0
# per mil \citep{zahn2006} figure 1
O3d17 = stisolib.calc_d17o_mif(O3d18, 35)

CO2d18=47 # Figure 4.9 \citep{Mrozek2017} values range from 45.8-49
CO2D17=8 # Figure 4.4 \citep{Mrozek2017} values range from 45.8-49 Note this is capital delta (D instead of d) range appears to be 6-12 
CO2d17=stisolib.calc_d17o_mif(CO2d18, CO2D17)
 

def o3_2_col(press, O3_molefrac):
    '''
    calculates the ozone column at all pressures p
    in a strictly ascending pressure columng in Pa.
    mole fraction of ozone (unitless).
    '''
    sp = 6.022140857E23 * (1000./(28.970*9.80665)) * 1.E-4
    # /Pa /cm2 or number of molecules per cm2 per pa
#    print sp

    col_val = []
    # @P=0 then O3=0. so at the first pressure level we will apply linear interpolation.
    col_val.append(sp*(press[0]-0)*0.5*(O3_molefrac[0]+0))
    # col_val.append(3.366E+17) #oringinal JVAL first value
    for i in range(1, len(press)):
        # First element
        cv = col_val[i-1]+sp*(press[i]-press[i-1])*0.5 * \
            (O3_molefrac[i]+O3_molefrac[i-1])

        col_val.append(cv)
    return col_val
