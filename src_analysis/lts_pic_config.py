#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 30 14:50:24 2018

@author: Joram

Picarro settings for analysis during RINGO 2018 campaign held in sodankylä
"""

#=============================================================================
# Picarro Configuration 
#=============================================================================

#=============================================================================
# Linear Calibration curve if a=1 and b=0 no calibration is performed
#=============================================================================
co2_cal_a=1.004784
co2_cal_b=0.796467

ch4_cal_a=1.000211
ch4_cal_b=-0.543137

# CO peak raw calibration:
co_peak84_a=0.427        # in ppm/UNIT?
co_peak84_b=0        # in ppm
#CO calibration:
co_cal_a=1.015910
co_cal_b=3.619401

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
Cav_P_cutoff=0.1 # Largest deviation allowed from setpoint

Cav_T_set=45.0 # Cavity Temperature setpoint Normal is 45
Cav_T_cutoff=0.05 # Largest deviation allowed from setpoint

co2_pres_a=-0.471

ch4_pres_a=-8.09         #in ppb per torr

#==============================================================================
# Call/fill gas values
#==============================================================================
co2_cal_tar=390.80     #ppm
ch4_cal_tar=2010.86    #ppb
co_cal_tar=156.29      #ppb


