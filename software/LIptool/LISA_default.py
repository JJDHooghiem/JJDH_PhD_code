#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 30 14:50:24 2018

@author: Joram

Picarro settings for analysis during april RINGO 2017 campaign held in sodankylä

The analysis order was 50,100,150,200 hpa samples (cal gas in front)
Datalogger PressureIn data was synthesised using the model presented in LISA a lightwight stratospheric air sammpler by hooghiem et al 2018. 
"""
picarro='RUG_mobile'
#date=2017-04-26

#=============================================================================
# Picarro Configuration
#=============================================================================

#=============================================================================
# Linear Calibration curve if a=1 and b=0 no calibration is performed
#=============================================================================
co2_cal_a=1.005673599
co2_cal_b=0.434573159

ch4_cal_a=0.99913183
ch4_cal_b=3.335009436

# CO peak raw calibration:
co_peak84_a=0.427        # in ppm/UNIT?
co_peak84_b=0        # in ppm
#CO calibration:
co_cal_a=1.00382352365
co_cal_b=9.82758190299

#==============================================================================
# Water correction funcitons
#==============================================================================

co2_water_a = -0.0124404
co2_water_b = -0.0000303

ch4_water_a = -0.010575
ch4_water_b = 0.000165

Dco_water_a = 2.306
Dco_water_b = 4.405
Dco_water_c = -2.093
Dco_water_d = 0.315

co_water_a = -0.0124
co_water_b = -0.0006




#==============================================================================
# Pressure corrections
#==============================================================================
Cav_P_set=140.0 # Cavity Pressure setpoint Normal is 140 Torr
Cav_P_cutoff=0.5 # Largest deviation allowed from setpoint

Cav_T_set=45.0 # Cavity Temperature setpoint Normal is 45
Cav_T_cutoff=0.05 # Largest deviation allowed from setpoint

co2_pres_a=-0.471
co2_temp_a=0.0
ch4_pres_a=-8.09         #in ppb per torr
ch4_temp_a=0.0
#==============================================================================
#
#==============================================================================

#==============================================================================
# Call/fill gas values (based on calibratoin against FMI cylinder (1 Point))
#==============================================================================
#co2_cal_tar=390.74     #ppm
#ch4_cal_tar=2008.93    #ppb
#co_cal_tar=159.99      #ppb
#==============================================================================
# Call/fill gas values (based on calibratoin rug calibration ICOS/NOAA 09-Oct-18)
#==============================================================================
co2_cal_tar=390.76     #ppm
ch4_cal_tar=2010.08   #ppb
co_cal_tar=159.10      #ppb


#==============================================================================
# Datalogger valvues
#==============================================================================

Sampling_start=-15  #or 13 (the amount of steps after pumping is initiad, e.g. the moment valves switch) based on the countound in the Ardino software, may differ duriong development phase
Sampling_stop=2     #or 6
ofset=20

V_b=0.00258     # Volume of sampling bag Move to

Pstp= 1000.   # Standard atmospheric pressure in mbar or hPa

Tstp=273.15     # Standard atmospheric temperature STP in kelvin
