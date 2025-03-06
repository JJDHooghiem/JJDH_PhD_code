#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Don't remove the line below, it is checked by "one to run them all"
# --otrta-p--
# extension p means parallel, s is for single
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from lodautil import LISA_load
from lodautil import AirCore_load
import scan.lisasd as lisasd
import config
import scantools
AirCore = AirCore_load()
LISA = LISA_load()
# Obtain only the keys for which we can make the comparison
flight_dates = lisasd.get_flightdates()
sel=[]
for i,f in enumerate(flight_dates):
    # if "RUG002" in f[1] and not "26" in f[0]:
    if "RUG002" in f[1]:
        sel.append(True)
    else:
        sel.append(False)
flight_dates=np.array(flight_dates)[sel]
AC_at_LISA = {}
for n in flight_dates:
    aircore = AirCore[n[1]]
    averageCO2 = lisasd.pwMean_at_LISA(
        aircore['P'], aircore['CO2'], n[0])
    averageCH4 = lisasd.pwMean_at_LISA(
        aircore['P'], aircore['CH4'], n[0])
    averageCO = lisasd.pwMean_at_LISA(
        aircore['P'], aircore['CO'], n[0])
    averagep = lisasd.pwMean_at_LISA(aircore['P'], aircore['P'], n[0])
    conairc = pd.DataFrame(
        data={'CO2': averageCO2, 'CH4': averageCH4, 'CO': averageCO, 'P': averagep})
    conairc = conairc.sort_values('P', ascending=False).reset_index()
    AC_at_LISA[n[1]] = conairc
# ==============================================================================
# One one plot aircore vs sampler and differences
# ==============================================================================
oneone = np.array([0, 5000])
# f, axes_array=plt.subplots(2, 3, gridspec_kw = {'height_ratios':[2, 1]}, sharex=False, sharey=False, figsize=(12, 5), squeeze=True)

xlabs = [config.axl['dco2'],config.axl['dch4'],config.axl['dco']]
xlims = [(-3, 3), (-40, 40), (-40, 40)]
ylabs = [config.axl['ph']]*3
ylims = [(200, 0)]*3
fig_p, axes_p = scantools.plot_init( 1, 3, xlabs, ylabs, xlims=xlims, ylims=ylims)

# xlabs = ['Lisa '+config.axl['co2'],'Lisa '+config.axl['ch4'],'Lisa '+config.axl['co'],'Lisa '+config.axl['co2'],'Lisa '+config.axl['ch4'],'Lisa '+config.axl['co']]
xlabs = ['Lisa\n'+config.axl['co2'],'Lisa\n'+config.axl['ch4'],'Lisa\n'+config.axl['co']]
xlims = [(392, 412), (600, 2000), (0, 100), (392, 406), (600, 2000), (0, 60)]
ylabs = ['AirCore '+config.axl['co2'],'AirCore '+config.axl['ch4'],'AirCore '+config.axl['co'],'AirCore '+config.axl['co2'],'AirCore '+config.axl['ch4'],'AirCore '+config.axl['co']]
xlims = [(392, 412), (600, 2000), (0, 100), (392, 406), (600, 2000), (0, 60)]
ylims = [(392, 412), (600, 2000), (0, 100), (-2, 2), (-20, 20), (-15, 15)]
fig, axes = scantools.plot_init( 1, 3, xlabs, ylabs, xlims=xlims, ylims=ylims)

markers = config.Markers
# colors=['g','b','k','r','steelblue']
colors = config.GruvBoxColors
species = ['CO2', 'CH4', 'CO']
diff=np.array([])
diffs ={ 'CO2':diff, 'CH4':diff, 'CO':diff}
for n, m, c in zip(flight_dates, markers, colors):
    if "RUG002" in n[1]:
        Data_load = LISA[n[0]]
        conairc = AC_at_LISA[n[1]]
        # for i in range(0, 3):
        # axes[0, i].plot(oneone, oneone, color='k', linestyle='-.')
        # for i in range(1):
        #     #    conairc=Aircore_conc[i]
        for ax, s,ax2 in zip(axes.ravel(), species,axes_p.ravel()):
            scantools.axoneone(ax, Data_load[s], conairc[s], xerr=Data_load[s+' un'], color=c, marker=m, lab=n[0],with_r2=False)
            x = np.array(Data_load[s]-conairc[s])
            diffs[s]=np.concatenate((diffs[s],x))
            # diffs=np.concatenate((diffs,x))
            y = np.array(Data_load['p'])
            # print(x,y)
            scantools.plot_add(ax2,x, y,  color=c, marker=m, label=n[1].replace('_',' '),linestyle='-')

    # axes[0, 0].errorbar(
    # Data_load['CO2'], conairc['CO2'], xerr=Data_load['CO2 un'], fmt=m, color=c)

    # axes[0, 1].errorbar(
    # Data_load['CH4'], conairc['CH4'], xerr=Data_load['CH4 un'], fmt=m, color=c)

    # axes[0, 2].errorbar(
    # Data_load['CO'], conairc['CO'], xerr=Data_load['CO un'], fmt=m, color=c)

    # axes[1, 0].plot(Data_load['p'], -
    # (Data_load['CO2']-conairc['CO2']), linestyle='', marker=m, color=c)
    # axes[1, 1].plot(Data_load['p'], -
    # (Data_load['CH4']-conairc['CH4']), linestyle='', marker=m, color=c)
    # axes[1, 2].plot(Data_load['p'], -
    # (Data_load['CO']-conairc['CO']), linestyle = '', marker = m, color = c)

    # axes[1, 0].axhline(
    #     np.nanmean(-(Data_load['CO2']-conairc['CO2'])), color='k')
    # axes[1, 1].axhline(
    #     np.nanmean(-(Data_load['CH4']-conairc['CH4'])), color='k')
    # axes[1, 2].axhline(
    #     np.nanmean(-(Data_load['CO']-conairc['CO'])), color='k', label=n[1])
# fig.subplots_adjust(wspace=0.4, hspace=0.4)

unit={"CO2" : r"\unit{\textrm{\textmugreek}mol\,mol^{-1}}","CO":r"\unit{nmol\,mol^{-1}}", "CH4":r"\unit{nmol\,mol^{-1}}" }

texfile = open(config.TabDir+'lisa_ac_comp.tex' , 'w')
for prec,key in zip([1,0,0],diffs.keys()):
    x=diffs[key]
    a=np.nanmean(x)
    b=np.nanstd(x,ddof=1)

    s="$({0}\pm{1})$".format(np.round(a,prec),np.round(b,prec))+unit[key]
    dat=np.array(['\ch{'+key+'}',s])
    # print(dat)
    scantools.npa_to_tex_table(dat,np.array(['','']),texfile) 
texfile.close()
# fig.tight_layout(rect=[0, 0.15, 1, 1])
# fig_p.tight_layout(rect=[0, 0.15, 1, 1])
#
# fig.tight_layout()
fig_p.tight_layout()
# for ax,ax2 in zip(axes.ravel(),axes_p.ravel()):
    # ax.legend()
    # ax2.legend()

for ax in axes.ravel():
    ax.legend()
# axes[1].legend(ncol=3, loc='lower center', bbox_to_anchfr=(0.5, -0.08), bbox_transform=fig.transFigure)
# axes_p[1].legend(ncol=3, loc='lower center', bbox_to_anchor=(0.5, 0.0), bbox_transform=fig.transFigure)
fig.tight_layout()
fig.savefig(config.FigDir+'lisasd_oneone.pdf')
fig_p.savefig(config.FigDir+'lisasd_dif_vs_p.pdf')
