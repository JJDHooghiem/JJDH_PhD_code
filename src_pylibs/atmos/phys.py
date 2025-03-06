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
from datetime import datetime
from scipy.interpolate import interp1d

def date2sec(year,month,day,hour,minutes,sec):
    """
    computes the seconds since the beginning of the year
    """
    year2=year
    if month==1 and day==1 and hour==0 and minutes==0 and sec==0:
        year2-=1
    seconds=(datetime(year,month,day,hour,minutes,sec)-datetime(year2,1,1,0,0,0)).total_seconds()
    return seconds

def mean_sza_month(latitude,month):
    """
    Computes the mean solar zenith angle for a month
    """
    start=date2sec(2000,month,1,0,0,0)
    if month==12:
        end=date2sec(2001,1,1,0,0,0)
    else:
        end=date2sec(2000,month+1,1,0,0,0)
    times=np.linspace(start,end,int(end/900)+1)
    sza_day=[]
    for t in times:
        a=sza(latitude,t)
        sza_day.append(a)
    mean_sza=np.mean(sza_day)
    return mean_sza

def mean_sza_day(latitude,month,day):
    """
    Computes the mean solar zenith angle for a day
    """
    sec=date2sec(2000,month,day,0,0,0)
    times=np.linspace(0,3600*24,int(3600*24/900)+1)+sec
    sza_day=[]
    for t in times:
        a=sza(latitude,t)
        sza_day.append(a)
    mean_sza=np.mean(sza_day)
    return mean_sza
def h2o_ppm(h2o,T,p):
    '''
    Calculates the mole fraction from temperature (K) pressure and RH
    according to saturation presse ps = 6.11 * exp(0.067*T) where T is in celcius
    p_satu is in hPa or mbar
    '''
    p_satu=6.11*np.exp(0.067*(T-273.15))
    p_h2o=p_satu*h2o
    h2o_pct=100*p_h2o/p
    return h2o_pct

def ndens(temp,pres):
    '''
    takes in pressure in Pa, T in kelvin and calculates the local number density in molecules per cm3
    This is allowed by IUPAC. 
    '''
    R=8.31446261815324 
    ndens=pres/(R*temp) #(MOL/M3)
    ndens=ndens*6.022140758e+23/10**6 #(molecules per cm3 )
    return ndens

def Calculate_params(p0, t0, a, h0, h1):
    """
    Takes in p0,t0 (layer bottom) and lapse rate and calculates t and p for
    the corresponding altitude with respect to layer bottom altitude.
    Based on hydrostatic balance and ideal gas law.
    """
    g_grav = 9.80665    # gravitational constant m/s^2
    R_Air = 287.058     # J kg^−1 K^−1
    if a != 0:
        t1 = t0 + a * (h1 - h0)
        p1 = p0 * (t1 / t0) ** (-g_grav / a / R_Air)
    else:
        t1 = t0
        p1 = p0 * np.exp(-g_grav / R_Air / t0 * (h1 - h0))
    return t1, p1
#
def Standard_atmos(altitude):
    """
    Takes a numpy array with altitudes and calculates the corresponding state parameters:
    Density pressure and temperature.
    Defines Pressure and Temperature in each of the grid points according to the
    1976 standard atmosphere. Pressure is returned in Pa
    """
    a = [-0.0065, 0, 0.001, 0.0028,0,-0.0028,-0.002]  #Lapse rate C/m of different regions
    h = [11000, 20000, 32000, 47000,51000,71000,84852] # altitude in meters of different pauses.
    p0 = 101325.
    t0 = 288.15
    prevh = 0
    g_grav = 9.80665    # gravitational constant m/s^2
    R_Air = 287.058     # J kg^−1 K^−1

    for i in range(0,len(h)):
        if altitude <= h[i]:
            t0, p0= Calculate_params(p0, t0, a[i], prevh, altitude)
            break;
        else:
            t0,  p0= Calculate_params(p0, t0, a[i], prevh, h[i])
            prevh = h[i]
    Temp=t0
    Pres=p0
    return Pres, Temp

def Standard_atmos_ar(alt):
    """
    Wrapper for dealing with numpy arrays.
    See Standard_atmos
    """ 
    t_ar=[]
    p_ar=[]
    for a in alt:
        p,t=Standard_atmos(a)
        t_ar.append(t)
        p_ar.append(p)
    return np.array(t_ar),np.array(p_ar)

def Standard_ozone(ztarget):
    """ Docstring for Standard_ozone.
    z altitude in meters
    returnsozone mole fraciotn in ppm 
    according ot \citep{Kreuger1976} 
    A mid-latitude ozone model for the 1976 U.S. Standard Atmosphere 
    doi ={10.1029/JC081i024p04477}
    """
    z=np.linspace(2000,74000,37)
    o3_ref=np.array([0.033,0.034,0.041,0.060,0.132,0.31,0.50,0.85,1.60,2.58,3.62,4.69,5.67,6.16,6.58,7.18,7.66,8.09,7.84,7.30,6.40,5.84,4.74,3.76,3.11,2.29,1.92,1.56,1.36,1.13,0.96,0.82,0.58,0.33,0.31,0.17,0.18])
    o3_target=interp1d(z,o3_ref)(ztarget)
    return o3_target 

def theta(T,p):
    '''
    Calculates potential temperature with 100000 Pa as the reference pressure.
    This was implemented as of 2018.
    '''
    return T*(100000./p)**(2./7)

def sza(latitude,time):
    '''returns the solar zenith angle in degrees 
    time in seconds
    lat in degrees
    ''' 
    pi=np.pi
    lat=latitude
    latrad=lat*2*pi/360.0
    ndays = time/86400.

    solar_declination=2*pi*(-23.44)*np.cos((2*pi/365.0)*(ndays+10.0))/360.0 

    hour=(ndays-np.floor(ndays))*24.0 

    solar_hour_angle=2*pi*(hour-12)*15/360     

    sza=np.arccos(np.cos(solar_declination)*np.cos(latrad)*np.cos(solar_hour_angle)+np.sin(solar_declination)*np.sin(latrad))
    sza=360*sza/(2*pi)
    if sza>90:
        sza=90
    return sza 

def tropopause_calculator(alt,temp):
    '''
    alt in m
    temp in K or C
    Tropopause calculator base on:
        The boundary between the troposphere and the stratosphere, where an abrupt change in lapse rate usually occurs. It is defined as the lowest level at which the lapse rate decreases to 2 °C/km or less, provided that the average lapse rate between this level and all higher levels within 2 km does not exceed 2 °C/km.

    nternational Meteorological Vocabulary (2nd ed.). Geneva: Secretariat of the World Meteorological Organization. 1992. p. 636. ISBN 92-63-02182-1.
    altitude in km
    lapse rate in C/km
    '''
    tropo_height=np.nan
    # check if alt is finite
    temp=np.array(temp[np.isfinite(alt)])
    alt=np.array(alt[np.isfinite(alt)])
    alt=alt/1000
    # lapse ret len(alt)-1
    lapse_rate_m=-(np.diff(temp)/np.diff(alt))
    alt_m=alt[:-1]+np.diff(alt)/2
    lapse_rate=interp1d(alt_m,lapse_rate_m,fill_value="extrapolate")(alt) 

    if len(alt)!=len(lapse_rate):
        print('Altitude and lapse rate should have the same length')
        return
    if alt[0]>alt[-1]:
        alt=alt[::-1]
        lapse_rate=lapse_rate[::-1]
    for i in range(0,len(lapse_rate)):
        if lapse_rate[i]<=2.0 and alt[i]>5 :
            for j in range(i+1,len(lapse_rate)):

                if alt[j]-alt[i]>=2.0:
                    break
#                else:

            if j-1!=i or j-1!=i+1:
#                print(lapse_rate[i:j-1])
                mean_lapse=np.nanmean(lapse_rate[i:j-1])
            if mean_lapse<2.0:
#                print(str(j-i)+' '+str(i)+' '+str(alt[j-1]-alt[i]))
#                print(mean_lapse)
                break

    tropo_height=interp1d(lapse_rate[i-1:i+1],alt[i-1:i+1])(2)
    return tropo_height
