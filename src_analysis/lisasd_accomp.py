#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Don't remove the line below, it is checked by "one to run them all"
# --otrta-p--
# extension p means parallel, s is for single
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import config
import scan.lisasd as lisasd
import scantools
from lodautil import AirCore_load, LISA_load

AirCore = AirCore_load()
LISA = LISA_load()
# Obtain only the keys for which we can make the comparison
flight_dates = lisasd.get_flightdates()
# f, axes_array=plt.subplots(1, 3,figsize=(4.7244094488, 5), sharex=False, sharey=True, squeeze=True)
# f, axes_array=plt.subplots(1, 3,figsize=(6, 5), sharex=False, sharey=True, squeeze=True)

xlims = [(390, 410), (500, 2000), (0, 100)]
ylims = [(11,26)]*3

xlabs= [config.axl['co2'],config.axl['ch4'], config.axl['co']]
ylabs = [config.axl['alt']]*3
f, axes_array = scantools.plot_init(1, 3, xlabs=xlabs, ylabs=ylabs, xlims=xlims, ylims=ylims)
    
colors = config.GruvBoxColors
markers = config.Markers
linestyles = ['-']*16
# key_1='p.mbar.'
# key_2='p'
# key_3=['p start','p stop']
# axes_array[0].set_ylabel('Pressure (hPa)')
# axes_array[0].set_ylim([200,0])
key_1 = 'GPS_ALT'
key_2 = 'Altitude'
key_3= ['Altitude start', 'Altitude stop']

bins = np.linspace(100, 30000, 300)
for n, m, c, c2, l in zip(flight_dates, markers, colors, colors, linestyles):
    lisakey, ackey= n
    if "RUG002" in ackey:
        Data_load = LISA[lisakey]
#        conairc=AC_at_LISA[n]
        dataAirC = AirCore[ackey]
        yerr= [(Data_load[key_2]-Data_load[key_3[0]]), (Data_load[key_3[1]]-Data_load[key_2])]

        xerr = 0
        # fig, axes_array = plt.subplots(1, 3, sharex=False, sharey=True, figsize=(12, 5), dpi=300, squeeze=False)
        axes_array[0].plot(dataAirC['CO2'], dataAirC[key_1]/1000,
                           linewidth=2, color=c, linestyle=l, label=ackey.replace("_"," "))
        axes_array[1].plot(dataAirC['CH4'], dataAirC[key_1] / \
                           1000, linewidth=2, color=c)
#        axes_array[0].errorbar(dataAirC['co2.ppm.'],dataAirC[key_1]/1000,xerr=dataAirC['co2.un.ppm.'],linewidth=2,color=c)
#        axes_array[1].errorbar(dataAirC['ch4.ppb.'],dataAirC[key_1]/1000,xerr=dataAirC['ch4.un.ppb.'],linewidth=2,color=c)
        # dataAirC=dataAirC.resample('20S').mean()
        # groups = dataAirC.groupby(np.digitize(dataAirC['GPS_ALT'], bins))

        x,y=scantools.asym_convolve(dataAirC['P'],dataAirC['CO'],std=6.5,return_mask=True)
        axes_array[2].plot(y, dataAirC[key_1][x]/1000, linewidth=2, color=c)
#    axes_array[2].plot(groups.mean()['co.ppb.'],groups.mean()['height.m.'])
for n, c, c2 in zip(flight_dates, colors, colors):

    lisakey, ackey= n
    if "RUG002" in ackey:
        Data_load = LISA[lisakey]
    # conairc=AC_at_LISA[n]
    # dataAirC=AirCore[n]

        yerr= [(Data_load[key_2]-Data_load[key_3[0]])/1000, (Data_load[key_3[1]]-Data_load[key_2])/1000]

        # x,y=scantools.asym_convolve(Data_load['p'],Data_load['CO2'],std=13.5,return_mask=True)
        # axes_array[0].errorbar(y, Data_load[key_2]/1000, xerr=Data_load['CO2 un'], yerr=yerr, fmt=m, color=c2, linestyle='', markersize=8, label='LISA001_'+lisakey)
        axes_array[0].errorbar(Data_load['CO2'], Data_load[key_2]/1000, xerr=Data_load['CO2 un'], yerr=yerr, fmt='o', color=c2, linestyle='', label='LISA001 '+lisakey)
        axes_array[1].errorbar(Data_load['CH4'], Data_load[key_2]/1000, xerr=Data_load['CH4 un'], yerr=yerr, fmt='o', color=c2, linestyle='')
        axes_array[2].errorbar(Data_load['CO'], Data_load[key_2]/1000, xerr=Data_load['CO un'], yerr=yerr,   fmt='o', color=c2, linestyle='' )

#    axes_array[1].set_xticks([500,1000,1500,2000])
# axes_array[0].set_title('(a)')
# axes_array[1].set_title('(b)')
# axes_array[2].set_title('(c)')
# colors_duplicat = []
# for w in colors:
#     colors_duplicat.append(w)
#     colors_duplicat.append(w)
# flight_dates_duplicat = []
# for w in flight_dates:
#     flight_dates_duplicat.append(w)
#     flight_dates_duplicat.append(w)
# flight_dates_duplicat= ['26-04',
#  '26-04',
#  '04-09',
#  '04-09',
#  '05-09',
#  '05-09',
#  '06-09',
#  '06-09']
# labels= ('LISA', 'AirCore', 'LISA', 'AirCore', 'LISA', 'AirCore', 'LISA', 'AirCore')

# linestyles= ("", "-", "", "-", "", "-", "", "-")
# handles = []
# for label, c, m, l, d in zip(labels, colors_duplicat, markers, linestyles, flight_dates_duplicat): 
    # handles.append(matplotlib.lines.Line2D([], [], color=c, marker=m, linestyle=l, label=label+' '+d, linewidth=3))
# labels=('AirCore','AirCore','AirCore','AirCore')
# linestyles=("-","-","-","-")
# for label, c, m, l,d in zip(labels, colors, markers, linestyles, flight_dates):
#    handles.append(matplotlib.lines.Line2D([], [], color=c, marker='',
#                                                   linestyle=l, label=label+' '+d, linewidth=3))
# axes_array[0].set_yticklabels(np.linspace(10,30,5))
# axes_array[1].set_yticklabels(np.linspace(10,30,5))
# axes_array[2].set_yticklabels(np.linspace(10,30,5))
# leg=axes_array[0].legend(handles=handles,ncol=4,loc='lower center', bbox_to_anchor=(0.5,-0.06), bbox_transform=f.transFigure)
# f.tight_layout(rect=[0, 0.22, 1, 1])
f.tight_layout()
legend=axes_array[0].legend(ncol=4, loc='lower center', bbox_to_anchor=(0.5, -.12), bbox_transform=f.transFigure)
legend.get_frame().set_linewidth(.5)
# leg=axes_array[1].legend(handles=handles, loc=9, frameon=True,bbox_to_anchor=(0., -.04, 1., -.04),
# f.subplots_adjust(wspace=0.5)
f.savefig(config.FigDir+'lisasd_accomp.pdf')
plt.close()
