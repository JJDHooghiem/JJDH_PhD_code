#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Don't remove the line below, it is checked by "one to run them all"
# --otrta-p--
# extension p means parallel, s is for single
"""
This code was written for the analysis presented in the dissertation of Joram Jan Dirk Hooghiem
"""

from lodautil import LISA_load
from lodautil import AirCore_load
import atmos
import config
import scantools

def main():
    # Load AirCore and LISA data
    LISA = LISA_load()
    data = AirCore_load()
    # =============================================================================
    # Plot purpose: show CO2/CO against altitude
    # nothing special here just plot the data
    # =============================================================================
    colors = config.GruvBoxColors
    xlabs = [config.axl['co']]
    ylabs = [config.axl['alt']]*2
    xlims = [(20, 120)]
    ylims = [(10, 15)]
    fig, axes_array = scantools.plot_init( 1, 1, xlabs=xlabs, ylabs=ylabs, xlims=xlims, ylims=ylims)
    AC_keys = ['RUG002_20170904', 'RUG002_20170905',
               'RUG002_20170906', 'RUG002_20170907']
    labels = ['AC 04-Sep', 'AC 05-Sep', 'AC 06-Sep', 'AC 07-Sep']
    for dat, c, l in zip(AC_keys, colors, labels):
        #    sel=[True if p>120 and p<200 else False for p in data[dat]['p.mbar.']]
        tropopause = atmos.tropopause_calculator(
            data[dat]['GPS_ALT'], data[dat]['T'])
        # axes_array[1].axhline(tropopause, linestyle=':', color=c, alpha=0.7)
        axes_array.axhline(tropopause, linestyle=':', color=c, alpha=0.7)
        # x=data[dat]['P']
        # y=data[dat]['CO2'] 
        # mask,x=scantools.asym_convolve(x,y,2,return_mask=True)
        # y=data[dat]['GPS_ALT'][mask]/1000
        # axes_array[1].plot(x, y, color=c, label=l, alpha=0.7)
        # axes_array[1].plot(data[dat]['CO2'], data[dat]['GPS_ALT']/1000, color=c, alpha=0.7)
        x=data[dat]['P']
        y=data[dat]['CO'] 
        mask,x=scantools.asym_convolve(x,y,2,return_mask=True)
        y=data[dat]['GPS_ALT'][mask]/1000
        axes_array.plot(x, y, color=c, label=l, alpha=0.7)

    LISA_keys = ['20170905', '20170906']
    markers = config.Markers
    # colors = [colors2[3], colors2[0], colors2[2]]

    labels = [
        # 'LISA 04-Sep',
        'LISA 05-Sep',
        'LISA 06-Sep']
    for dat, m, l, c in zip(LISA_keys, markers, labels, colors[1:]):
        yerr = [(LISA[dat]['Altitude']-LISA[dat]['Altitude start']) /
                1000, (LISA[dat]['Altitude stop']-LISA[dat]['Altitude'])/1000]
        # axes_array[1].errorbar(LISA[dat]['CO2'], LISA[dat]['Altitude']/1000,yerr=yerr,fmt=m,color=c)       #xerr=LISA[dat]['CO2 std(ppm)']
        axes_array.errorbar(LISA[dat]['CO'], LISA[dat]['Altitude']/1000,
                               yerr=yerr, fmt=m, color=c, label=l)  # xerr=LISA[dat]['CO std(ppb)']

    # text=axes_array[0].set_ylabel('Altitude (km)',rotation="horizontal") # For presentation

    # axes_array[0].yaxis.set_label_coords(-0.4,0.45)
    #leg=axes_array[0].legend(ncol=1,bbox_to_anchor=(-1,0.6), fontsize=18)
    # fig.subplots_adjust(wspace=0.5)
    fig.tight_layout()
    leg = axes_array.legend(ncol=3, loc='lower center', bbox_to_anchor=(
        0.5, -0.09), bbox_transform=fig.transFigure)
    fig.savefig(config.FigDir+'wisman_molefraction_coonly.pdf',
                bbox_extra_artists=[leg], bbox_inches='tight')
    return


if __name__ == "__main__":
    main()
