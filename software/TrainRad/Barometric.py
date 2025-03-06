#!/usr/bin/env python
import numpy as np

# Ks = 0.0019318                  
# e = 0.081819                    
# Gamma_e = 9.780325              #m/s(^2)
Rd = 287.04                     #J/(kg * K)
# K1 = 0.051859                   
# K2 = 0.000003086                   
# H_S = 1.3                       
# M = 0.0289644                   #kg/mol

g45=9.80665 

# def GammaFromZ(Z,Lat):
#     g0=9.780318
#     k1=5.3024E-3
#     k2=5.8E-6
#     k3=3.085E-6
#     Lat_rad=Lat*np.pi/180 
#     Gamma=g0*(1+(k1*np.sin(Lat_rad)**2)-(k2*np.sin(2*Lat_rad)**2))-k3*Z
#     return Gamma

def saturation_pressure(T):
    """
    Temperature in Kelvin
    returns: Saturation pressure in Pa
    """
    Ps = 0.01 * np.exp(-2991.2729*(T**-2) - 6017.0128*(T**-1) + 18.87643854 - 0.028354721 * T +(0.17838301 * 10**-4) * (T**2) -(0.84150417 * (10**-9)) * (T**3) + (0.44412543 * (10**-12)) * (T**4) + 2.858487 * np.log(T))

    return Ps*100

# def heigth_to_geopotmetpy(z):
#     '''
#     Taken from metpy, removed the units part. 
#     g=9.80665 standard gravity at 45.542 degrees Lat m/s^2.
#     Re=6.3712e6 Earhts radius in metres 
#     Input altitude in metre 
#     '''
#     g=9.80665 
#     Re=6.3712e6  
#     geopot= (g * Re * z) / (Re + z) 
#     return geopot

def R_phi(Lat):
    """TODO: Docstring for Rphi.
    :returns: TODO
    """
    Re=6.378137E6 # 
    x=np.sin(Lat*np.pi/180)**2
    Rp=Re/(1.006803-0.006706*x)
    return Rp 

def gamma_s(Lat):
    """ Somigliana's equation ffor normal gravity of the surface of an ellipsoid.
    According to Worlds geodetic system 1984  
    :returns: TODO
    """
    gamma_e=9.780325 # Gravity at the equator m/s**2
    ks=1.9318E-3 # Somiglianas constant
    e=0.081819 # Eccentricity of WGS84 ellipsoid World geodetic system 1984
    x0=np.sin(np.pi*Lat/180)**2
    x1=1+ks*x0
    x2=np.sqrt(1-(e**2 )*x0)
    Gs=gamma_e*(x1/x2) 
    return Gs 

def heigth_to_geopotH(Z,Lat):
    """TODO: Docstring for heigth_to_geopotDirksen.
    :returns: TODO
    Computes the Geopotential height from geometric altitude using WGS-84 
    Ellipsoid to compute the normal gravity on the surface of an ellipsoid
    
    """
    Rphi=R_phi(Lat)
    gs=gamma_s(Lat) 
    geopot=( gs/g45 )* ( (Rphi*Z)/(Rphi+Z) )
    return geopot 

def average_virtual_temperature(T_avg, RH_avg,  Pressure,Ps):
    """
    T_avg is average temperature in Kelvin, RH_avg is average Relative Humidity, Ps is the Saturaion Pressure in Pa, Pcalc is the calculated pressure in Pa.
    returns: Average Virtual Temperature (Tv_avg) in Kelvin
    """

    Tv_avg = (T_avg / (1 - 0.01 * RH_avg * (1 - 0.622) * (Ps / Pressure)))
    return Tv_avg

def barometric_p(T,RH,GeopotH,Psurf):
    """
    Function that computes an atmospheric pressure profile using the barometric equation
    This work follows Dirksen et al 2014 (10.5194/amt-7-4463-2014).
    (There appear to be some inconsistencies in their calculations).
    Here the barometric equation is obtained, as a function of geopotential heigh difference
    following also recommendations by wmo. https://library.wmo.int/doc_num.php?explnum_id=3158
    
    T, RH, and Geopot are 1-dim arrays numpy arrays of equal length. 
    Psurf is a float with the surface pressure (or top pressure)
    """       
    if len(T)==len(RH)==len(GeopotH):
        p_barometric=np.array([None]*len(T))
        p_barometric[0]=Psurf#/100
    else:
        print("input variables T, RH, LAT, and Z are required to have the same length")
        exit()
    
    #compute geopotential height differences dH
    dH = np.diff(GeopotH)

    for j in range(0, len(p_barometric) - 1):
    #for j in range(0,5):
        #mean of two layers
        T_avg = 0.5 * (T[j] + T[j+1])
        RH_avg = 0.5 * (RH[j] + RH[j+1])
        # Saturation pressure here stuff is done in hPa hence division by hundred
        PS=saturation_pressure(T_avg)/100
        # Virtual temperature first guess (note recursive use of P)
        Tv_avg = average_virtual_temperature(T_avg,RH_avg,p_barometric[j],PS)
        # First geuss of next pressure level
        p2 = p_barometric[j]*np.exp(( -g45*dH[j]) / (Rd * Tv_avg))
        # Approximate mean pressure level between two layers with (as in Dirksen)
        P_avg = np.sqrt(p2 *p_barometric[j])
        # Update vertual temperature 
        Tv_avg_new = average_virtual_temperature(T_avg,RH_avg, P_avg,PS)
        # Check for converguence to find iterative solution 
        while np.round(Tv_avg,6) != np.round(Tv_avg_new, 6):
            # print( Tv_avg_new)
            # print(Tv_avg)
            Tv_avg = Tv_avg_new
            # Update pressure level
            p2 = p_barometric[j]*np.exp(( -g45*dH[j]) / (Rd * Tv_avg))
            P_avg = np.sqrt(p2 * p_barometric[j])
            Tv_avg_new = average_virtual_temperature(T_avg, RH_avg, P_avg,PS)
        p_barometric[j+1]=p2
    return p_barometric
