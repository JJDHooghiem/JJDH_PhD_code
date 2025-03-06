"""
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
import pandas as pd
from lodautil import AirCore_load, LISA_load, LISA_load_weights
from scipy.interpolate import interp1d
import config
V_b = 0.00258             # Volume of sampling bag in m^3
Tofset = 19.738245025  # time after which compression starts


def AnalyseStorage():
    """ Docstring for AnalyseStorage.
    Loads data, and returns the computed differences to be plotted
    from the preprocessed AnalyseStorage analyses 
    """
    # Reftank values order is CO2, CO2 std, CH4 std, 
    lowcyl = [398.11724605680973,
              0.016016983442485037,
              1969.4999367527473,
              0.053415906140376182,
              121.45926159965326,
              0.17950521732834687]
    highcyl = [449.84785044561835,
               0.017498494413322293,
               2086.2237019649765,
               0.010087482587273168,
               260.53584839560432,
               0.60209667272469714]

    index = [0, 1, 2]
    cylc = [lowcyl, highcyl]
    cyl = ['Low', 'High']
    col = ['o', 's']

    datadir = config.DataDir+'/LISA_Sampler_Development/2016_09_Sampling_bag_storage_tests/Processed_Data/'

    # ==============================================================================
    # Import data and calculate differences etc
    # ==============================================================================
    data = pd.read_csv(datadir+'low.csv')

    data['Measurement'] = data['When']

    ran = range(0, len(data['CO2(ppm)']))

    CO2res = [data['CO2(ppm)'][i+1]-data['CO2(ppm)'][i]
              for i in ran if data['When'][i] == 'Direct']
    CO2std = [np.sqrt(data['CO2 std(ppm)'][i+1]**2+data['CO2 std(ppm)'][i]**2)
              for i in ran if data['When'][i] == 'Direct']

    CH4res = [data['CH4(ppb)'][i+1]-data['CH4(ppb)'][i]
              for i in ran if data['When'][i] == 'Direct']
    CH4std = [np.sqrt(data['CH4 std(ppb)'][i+1]**2+data['CH4 std(ppb)'][i]**2)
              for i in ran if data['When'][i] == 'Direct']

    COres = [data['CO(ppb)'][i+1]-data['CO(ppb)'][i]
             for i in ran if data['When'][i] == 'Direct']
    COstd = [np.sqrt(data['CO std(ppb)'][i+1]**2+data['CO std(ppb)'][i]**2)
             for i in ran if data['When'][i] == 'Direct']

    H2Ores = [data['H2O'][i+1]-data['H2O'][i]
              for i in ran if data['When'][i] == 'Direct']
    H2Ostd = [np.sqrt(data['H20 std'][i+1]**2+data['H20 std'][i]**2)
              for i in ran if data['When'][i] == 'Direct']

    reslist = np.array([CO2res, CO2std, CH4res, CH4std,
                        COres, COstd, H2Ores, H2Ostd])
    headerlist = ['CO2(ppm)', 'CO2 std(ppm)', 'CH4(ppb)',
                  'CH4 std(ppb)', 'CO(ppb)', 'CO std(ppb)', 'H2O', 'H2O std']
    resdatalow = pd.DataFrame(reslist.T, columns=headerlist)
    resdatalowmlf = resdatalow[:2]
    resdatalowted = resdatalow[2:]

    data = pd.read_csv(datadir+'data_combined_Ted.csv')
    data['Measurement'] = data['When']
    ran = range(0, len(data['CO2(ppm)']))
    # datatted['flag']=[1,2,3,1,2,3,1,2,3,1,2,3,1,2,3,1,2,3]
    # datatted['flush']=[1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2]
    samplenum = 6
    ran = range(0, len(data['CO2(ppm)']))

    CO2res = [data['CO2(ppm)'][i+1]-data['CO2(ppm)'][i]
              for i in ran if data['When'][i] == 'Direct']
    CO2std = [np.sqrt(data['CO2 std(ppm)'][i+1]**2+data['CO2 std(ppm)'][i]**2)
              for i in ran if data['When'][i] == 'Direct']

    CH4res = [data['CH4(ppb)'][i+1]-data['CH4(ppb)'][i]
              for i in ran if data['When'][i] == 'Direct']
    CH4std = [np.sqrt(data['CH4 std(ppb)'][i+1]**2+data['CH4 std(ppb)'][i]**2)
              for i in ran if data['When'][i] == 'Direct']

    COres = [data['CO(ppb)'][i+1]-data['CO(ppb)'][i]
             for i in ran if data['When'][i] == 'Direct']
    COstd = [np.sqrt(data['CO std(ppb)'][i+1]**2+data['CO std(ppb)'][i]**2)
             for i in ran if data['When'][i] == 'Direct']

    H2Ores = [data['H2O'][i+1]-data['H2O'][i]
              for i in ran if data['When'][i] == 'Direct']
    H2Ostd = [np.sqrt(data['H20 std'][i+1]**2+data['H20 std'][i]**2)
              for i in ran if data['When'][i] == 'Direct']

    reslist = np.array([CO2res, CO2std, CH4res, CH4std,
                        COres, COstd, H2Ores, H2Ostd])

    resdatated = pd.DataFrame(reslist.T, columns=headerlist)
    resdatated = resdatated[1:].reset_index()

    data = pd.read_csv(datadir+'data_combined_MLF.csv')
    data['Measurement'] = data['When']
    ran = range(0, len(data['CO2(ppm)']))
    ran = range(0, len(data['CO2(ppm)']))

    CO2res = [data['CO2(ppm)'][i+1]-data['CO2(ppm)'][i]
              for i in ran if data['When'][i] == 'Direct']
    CO2std = [np.sqrt(data['CO2 std(ppm)'][i+1]**2+data['CO2 std(ppm)'][i]**2)
              for i in ran if data['When'][i] == 'Direct']

    CH4res = [data['CH4(ppb)'][i+1]-data['CH4(ppb)'][i]
              for i in ran if data['When'][i] == 'Direct']
    CH4std = [np.sqrt(data['CH4 std(ppb)'][i+1]**2+data['CH4 std(ppb)'][i]**2)
              for i in ran if data['When'][i] == 'Direct']

    COres = [data['CO(ppb)'][i+1]-data['CO(ppb)'][i]
             for i in ran if data['When'][i] == 'Direct']
    COstd = [np.sqrt(data['CO std(ppb)'][i+1]**2+data['CO std(ppb)'][i]**2)
             for i in ran if data['When'][i] == 'Direct']

    H2Ores = [data['H2O'][i+1]-data['H2O'][i]
              for i in ran if data['When'][i] == 'Direct']
    H2Ostd = [np.sqrt(data['H20 std'][i+1]**2+data['H20 std'][i]**2)
              for i in ran if data['When'][i] == 'Direct']

    reslist = np.array([CO2res, CO2std, CH4res, CH4std,
                        COres, COstd, H2Ores, H2Ostd])

    resdatamlf = pd.DataFrame(reslist.T, columns=headerlist)
    resdatamlf = resdatamlf[1:].reset_index()
    return resdatalowmlf, resdatalowted, resdatamlf, resdatated


def pump_time(time):
    """
    Calculates the time factor a(t) assumes time in seconds. 
    Using this V_stp can be calculated accordint to V_stp=a(t)*p_b
    were p_b is the pressure in the bag. 
    """
    return 0.008056787-0.005056757*np.exp(-time/59.61067416)


def inverse_pump_time(V_over_P):
    return -59.61067416*np.log((V_over_P-0.008056787)/-0.005056757)

def pump_error(time):
    """
    Calculates the error in the slope of the pump model. assumes covariances are zero
    """
    sigma_x = 0.000026**2
    sigma_b = ((-np.exp(-time/59.61067431))**2)*0.000020**2
    sigma_tau = (((-np.exp(-time/59.61067431)) *
                  (time*0.004990631/(59.61067431)**2))**2)*0.81542568**2
    return np.sqrt(sigma_x+sigma_b+sigma_tau)


def r_value(x, y):

    yhat = np.mean(y)

    sstot = np.sum([(y[i]-yhat)**2 for i in range(0, len(y))])

    ssres = np.sum([(y[i]-x[i])**2 for i in range(0, len(y))])

    r_value = 1-(ssres/sstot)
    return r_value


def get_flightdates():
    AirCore = AirCore_load()
    LISA = LISA_load()
# Obtain only the keys for which we can make the comparison
    flight_dates = []
    for date in LISA.keys():
        for ac in AirCore.keys():
            if date in ac:
                flight_dates.append([date, ac])
    return flight_dates


def pwMean_at_LISA(p, var, key):
    ''' Computes the pressure weighte mean of 
    an 
    p is a flat pressure array 
    var is a flat variable array, to be pressure weighted averaged
    key is the flight dates of the lisa sampler

    it will return a list of pweighted means with the dimensions (lenght) of the LISA data of date key
    '''

    interpolate = interp1d(p[np.isfinite(var)], var[np.isfinite(var)])

    weights = LISA_load_weights()[key]

    pweight_mean = []
    for w in np.unique(weights['SampleFlag']):
        weight = weights[weights['SampleFlag'] == w]['Weights']
        PR = weights[weights['SampleFlag'] == w]['PR']
        try:
            pweight_mean.append(np.nansum(interpolate(PR)*weight))
        except ValueError:
            pweight_mean.append(np.nan)
    return pweight_mean
