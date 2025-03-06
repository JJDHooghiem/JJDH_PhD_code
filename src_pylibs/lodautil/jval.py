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
from scipy.interpolate import interpn

def fortran2py(string):
    string=string.split('=')[-1]
    string=string.replace('(/','').replace('/)','')
    string=string.split(',')
    string=[float(i) for i in string]
    string=np.array(string)
    return string

def obtain_jval(path):
    '''
    Obtains press in Pa, ozone mole fraction and temp.
    '''
    with open(path) as jvalf90:
        for l in jvalf90.readlines():
            if 'press' in l and '=' in l:
                press=fortran2py(l) # for some reason we are still working in mbar instead of si units ow well 
            if 'relo3' in l and '=' in l:
                ozone=fortran2py(l)[:-1] 
            if 'temp' in l and '=' in l:
                temp=fortran2py(l)[:] 
        jvalf90.close()
    return press,ozone,temp

# Deprecated function? 
def jvalnc(ncdata,key,sza):
    nc_fid=Dataset(ncdata)
    filt=[['sza',sza,sza]]
    interest=netcdf.data_selector(key,filt,nc_fid)
    x=nc_fid[key][:,interest]
    return x

def get_jvalues(ncf,key,sza,lev,method='linear'):
    """TODO: Docstring for function.
    parameters:
    ncf: netcdf_file
    key: The target photolysis rate
    sza: The targeted sza
    lev: The Targeted level
    method : str, optional
        The method of interpolation to perform. Supported are "linear" and
        "nearest", and "splinef2d". "splinef2d" is only supported for
        2-dimensional data.

    """
    try:
        len(sza)
    except TypeError:
        sza=np.array([sza])
    try:
        len(lev)
    except TypeError:
        lev=np.array([lev])
    mesh=np.array(np.meshgrid(lev,sza))
    mesh=np.rollaxis(mesh,0,3).reshape(len(lev),2)
    value=interpn((ncf['lev'][:],ncf['sza'][:]),ncf[key][:],mesh,method=method)
    return value
