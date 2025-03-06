#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Don't remove the line below, it is checked by "one to run them all"
# --otrta-p--
# extension p means parallel, s is for single
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import scipy.stats as stats
from lodautil import LISA_load
from lodautil import AirCore_load
import scan.lisasd as lisasd

AirCore = AirCore_load()
LISA = LISA_load()
# Obtain only the keys for which we can make the comparison
flight_dates = lisasd.get_flightdates()

AC_at_LISA = {}
for n in flight_dates:
    lisakey, ackey = n
    aircore = AirCore[ackey]
    averageCO2 = lisasd.pwMean_at_LISA(aircore['P'], aircore['CO2'], lisakey)
    averageCH4 = lisasd.pwMean_at_LISA(aircore['P'], aircore['CH4'], lisakey)
    averageCO = lisasd.pwMean_at_LISA(aircore['P'], aircore['CO'], lisakey)
    averagep = lisasd.pwMean_at_LISA(aircore['P'], aircore['P'], lisakey)
    conairc = pd.DataFrame(
        data={'CO2': averageCO2, 'CH4': averageCH4, 'CO': averageCO, 'p': averagep})
    conairc = conairc.sort_values('p', ascending=False).reset_index()
    AC_at_LISA[ackey] = conairc

diff_CO2 = []
diff_CH4 = []
diff_CO = []
pressure = []
All_co2_sampler = []
All_co2_aircore = []

for n in flight_dates:
    lisakey, ackey = n
    Data_load = LISA[lisakey]
    conairc = AC_at_LISA[ackey]
    dataAirC = AirCore[ackey]
    pressure.append(conairc['p'])
    d = conairc['CO2'] - Data_load['CO2']
    mask=(np.isfinite(conairc['CO2'])&np.isfinite(Data_load['CO2']))
    d2 = np.nanmean(conairc['CO2'][mask]) - np.nanmean(Data_load['CO2'][mask])
    print("###### lol ######\n")

    print("###### AC ######")
    print(conairc['CO2']) 
    print("###### Lisa ######")
    print(Data_load['CO2'])

    print(np.nanmean(d))
    print(d2)

    print("###### exit ######")
    # print('CO2 ', str(np.nanmean(d))+' '+str(np.nanstd(d)))
    # print('CO2 ', str(d2))
    for i in range(0, len(Data_load['CO2'])):
        All_co2_sampler.append(Data_load['CO'][i])
        All_co2_aircore.append(conairc['CO'][i])

    diff_CO2.extend(d)
    d = conairc['CH4'] - Data_load['CH4']

    # print('CH4 ', str(np.nanmean(d))+' '+str(np.nanstd(d)))
    diff_CH4.extend(conairc['CH4'] - Data_load['CH4'])
    diff_CO.extend(conairc['CO'] - Data_load['CO'])
    d = conairc['CO'] - Data_load['CO']
    # print('CO ', str(np.nanmean(d))+' '+str(np.nanstd(d)))

co2s, co2a = zip(*sorted(zip(All_co2_sampler, All_co2_aircore)))
co2s = np.array(co2s)
co2a = np.array(co2a)
stats.linregress(co2a[np.isfinite(co2a)], co2s[np.isfinite(co2a)])
lisasd.r_value(co2a[np.isfinite(co2a)], co2s[np.isfinite(co2a)])
