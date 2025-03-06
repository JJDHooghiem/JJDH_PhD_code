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
import lodautil
import matplotlib.pyplot as plt
import scantools

import config

colors = config.GruvBoxColors
markers = config.Markers
#
# AirCore LISA ECHAM plots
#

def plot_TracerTracer(axes,LISA,AC=[0]):
    """plot_TracerTracer.

    Parameters
    ----------
    LISA :
        LISA
    AC :
        AC
    """
    species1='CH4'
    var1='tracer_gp_'+species1
    species=['CO2','CO','N2O','P']
    ppb=1E9
    units=[1E6,1E9,1E9]
    sp=0
    for i in range(0,2):
        for j in range(0,2):
            species2=species[sp] 
            if species2!='P':
                unit=units[sp]
                var2='tracer_gp_'+species2
                times,_=lodautil.get_sample_dt(LISA)
                ncfid=Dataset('/home/joram/research/data/ECHAM/LISA/SICM-z4/SICM-z4_LISA-ni.nc')
                for t in times:
                    x,y=get_echam_trtr(var1,var2,t,ncfid)
                    axes[i,j].plot(x*ppb,y*unit,'go',label='SICM-ni')
                ncfid=Dataset('/home/joram/research/data/ECHAM/LISA/SICM-z4/SICM-z4_LISA.nc')
                for t in times:
                    x,y=get_echam_trtr(var1,var2,t,ncfid)
                    axes[i,j].plot(x*ppb,y*unit,'ro',label='SICM')
                if (species1 in LISA)&(species2 in LISA):
                    axes[i,j].plot(LISA[species1],LISA[species2],linestyle='',marker='d',color='cyan',label='LISA')
                #check if aircores exist
                if any(AC):
                    for A in AC.keys():
                        if (species1 in AC[A])&(species2 in AC[A]):
                            axes[i,j].plot(AC[A]['CH4'][(AC[A]['P']>=5)&(AC[A]['P']<=200)],AC[A][species[sp]][(AC[A]['P']>=5)&(AC[A]['P']<=200)],linestyle='',marker='*',color='blue', label=A.replace('_','\_'))
                axes[i,j].set_xlabel(config.axl[species1.lower()])
                sp+=1
            else:
                ncfid=Dataset('/home/joram/research/data/ECHAM/LISA/SICM-z4/SICM-z4_LISA.nc')
                for t in times:
                    echam_p_profile(axes[1,1],ppb,t,var1,ncfid,color='g',linestyle='',marker='o',label='SCIM')
                ncfid=Dataset('/home/joram/research/data/ECHAM/LISA/SICM-z4/SICM-z4_LISA-ni.nc')
                for t in times:
                    echam_p_profile(axes[1,1],ppb,t,var1,ncfid,color='r',linestyle='',marker='o',label='SCIM-ni')
                if any(AC):
                    for A in AC.keys():
                        axes[1,1].plot(AC[A]['CH4'],AC[A]['P']*100,linestyle='',marker='*',color='b',label=A.replace('_','\_'))
    axes[1,1].plot(LISA[species1],LISA['p']*100,linestyle='',marker='d',color='cyan',label='LISA')
    return     


def echam_p_profile(axes, unit, t, var, ncfid, **kwargs):
    y = lodautil.echam.get_ECHAM_pp(t, ncfid)
    x = lodautil.echam.get_ECHAM_tt(t, var, ncfid)
    axes.plot(x*unit, y, **kwargs)
    return


def plot_TracerTracerALL(AC=[0], interpolated=False):
    """plot_TracerTracer.

    Parameters
    ----------
    LISA :
        LISA
    AC :
        AC
    """
    LISADATA = lodautil.lisa.LISA_load()

    ncfid = lodautil.get_ncfid(interpolated)
    fig, axes = plt.subplots(2, 2, figsize=(5, 5))
    species1 = 'CH4'
    var1 = 'tracer_gp_'+species1
    species = ['CO2', 'CO', 'N2O', 'P']
    ppb = 1E9
    units = [1E6, 1E9, 1E9]
    for dat, c in zip(LISADATA.keys(), colors):
        LISA = LISADATA[dat]
        sp = 0
        for i in range(0, 2):
            for j in range(0, 2):
                species2 = species[sp]
                if species2 != 'P':
                    unit = units[sp]
                    var2 = 'tracer_gp_'+species2
                    times, _ = lodautil.get_sample_dt(LISA)
                    for t in times:
                        x, y = get_echam_trtr(var1, var2, t, ncfid)
                        axes[i, j].plot(x*ppb, y*unit, color=c,
                                        marker='', alpha=0.4, label='ECHAM5-'+dat)
                    if (species1 in LISA) & (species2 in LISA):
                        axes[i, j].plot(
                            LISA[species1], LISA[species2], linestyle='', marker='d', color=c, label='LISA'+dat)
                    # check if aircores exist
                    if any(AC):
                        for A in AC.keys():
                            if (species1 in AC[A]) & (species2 in AC[A]):
                                axes[i, j].plot(AC[A]['CH4'][(AC[A]['P'] >= 5) & (AC[A]['P'] <= 200)], AC[A][species[sp]][(
                                    AC[A]['P'] >= 5) & (AC[A]['P'] <= 200)], linestyle='', marker='*', color='blue', label=A)
                    sp += 1
                else:
                    axes[1, 1].plot(LISA[species1], LISA['p']*100,
                                    linestyle='', marker='d', color=c, label='LISA'+dat)
                    for t in times:
                        y = lodautil.echam.get_ECHAM_pp(t, ncfid)
                        x = lodautil.echam.get_ECHAM_tt(t, var1, ncfid)
                        axes[1, 1].plot(x*ppb, y, color=c, marker='',
                                        alpha=0.3, label='ECHAM-'+dat)

                    if any(AC):
                        for A in AC.keys():
                            axes[1, 1].plot(AC[A]['CH4'], AC[A]['P']*100, linestyle='',
                                            marker='*', color='b', label=A.replace('_', '\_'))
    sp = 0
    for i in range(0, 2):
        for j in range(0, 2):
            species2 = species[sp]
            if species2 != 'P':
                axes[i, j].set_xlabel( config.axl[species1.lower()])
                if unit == 1E6:
                    axes[i, j].set_ylabel(config.axl[species2.lower()])
                else:
                    axes[i, j].set_ylabel(config.axl[species2.lower()])
                axes[i, j].set_xlim(500, 2000)
                sp += 1
    axes[1, 1].set_xlabel( config.axl[species1.lower()])
    axes[1, 1].set_ylabel(config.axl['p'])
    axes[1, 1].set_ylim(20000, 0)
    handles, labels = scantools.getUniqueLegend(axes[1, 1])
    axes[1, 1].set_xlim(500, 2000)
    fig.tight_layout()
    axes[1, 1].legend(handles=handles, labels=labels, ncol=4, loc='lower center',
                      bbox_to_anchor=(0.5, -0.13), bbox_transform=fig.transFigure)
    return fig, axes
