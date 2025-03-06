#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Don't remove the line below, it is checked by "one to run them all"
# --otrta-p--
# extension p means parallel, s is for single
import scantools
import lodautil
import config
import numpy as np
import stisolib
colors = config.GruvBoxColors
LISA = lodautil.flattened_LISA()
ncfid = lodautil.get_ncfid(interpolated=False, daymean=False)
# xlabs = [config.axl['co'], config.axl['ch4']]
xlabs = [config.axl['enr'],config.axl['enr'],'$y$/ppb',config.axl['fco2co']]
# ylabs = [config.axl['enr']]*2
ylabs = [config.axl['ph']]*4
xlims = [(-15,0),(-15,0),(0,500),(0,1)] 
ylims = [(2,0)]*4
fig, axes = scantools.plot_init(2, 2, xlabs=xlabs, ylabs=ylabs, xlims=xlims, ylims=ylims)
# for i,dat in enumerate(lodautil.get_dates(LISA)):
for i,dat in enumerate(['2017-09-04']):
    data = lodautil.date_select(LISA, dat)
    # 12:00 utc:
    time = np.floor(lodautil.get_sample_dt(data)[0][2])+0.5
    CO = lodautil.echam.get_ECHAM_tt(time, 'tracer_gp_CO', ncfid)
    CH4 = lodautil.echam.get_ECHAM_tt(time, 'tracer_gp_CH4', ncfid)*1E9
    COeps13 = 1e3*(lodautil.echam.get_ECHAM_tt(time, 'tracer_gp_E13pCO', ncfid)/CO-1)
    COeps18 = 1e3*(lodautil.echam.get_ECHAM_tt(time, 'tracer_gp_E18pCO', ncfid)/CO-1)
    FCMCO = lodautil.echam.get_ECHAM_tt(time, 'tracer_gp_FCMCO', ncfid)/CO
    FHVCO = lodautil.echam.get_ECHAM_tt(time, 'tracer_gp_FHVCO', ncfid)/CO
    CO = CO*1E9


    press = lodautil.echam.get_ECHAM_pp(time, ncfid)
    temp = lodautil.echam.get_ECHAM_tt(time, 'ECHAM5_tm1', ncfid)
    # press = lodautil.echam.get_ECHAM_pp(time, ncfid)
    pmask = (press > 0) & (press < 2500)
    # axes[0].plot(press[pmask], COeps13[pmask], color=colors[2], marker='o', label=r"$^{13}\textrm{ C }$")
    # axes[0].plot(press[pmask], COeps18[pmask], color=colors[i], marker='o', label=r"$^{18}\textrm{ O }$ "+dat)
    axes[1,0].plot(CO[pmask], press[pmask]/100, color=colors[3], marker='o', label=r"$\textrm{ CO }$")
    axes[1,0].plot(CH4[pmask], press[pmask]/100, color=colors[5], marker='o', label=r"$\textrm{ CH_4 }$")
    axes[1,1].plot(FHVCO[pmask], press[pmask]/100, color=colors[3], marker='o', label=r"$\textrm{ CO }$")
    axes[1,1].plot(FCMCO[pmask], press[pmask]/100, color=colors[5], marker='o', label=r"$\textrm{ CO }$")

    # k_oh_co, k_oh_13co, k_oh_c17o, k_oh_c18o= stisolib.co_3step_OH(press[pmask],temp[pmask])

    edummy=-1000*(stisolib.alpha_oh_o18(press[pmask])-1)
    axes[0,0].plot(edummy, press[pmask]/100, color=colors[2],  label=r"$^{18}\textrm{ O }$-equilibrium")

    edummy=-1000*(stisolib.alpha_oh_c13(press[pmask])-1)
    axes[0,0].plot(edummy, press[pmask]/100, color=colors[1],  label=r"$^{13}\textrm{ C }$-equilibrium")

    axes[0,0].plot(COeps13[pmask], press[pmask]/100, color=colors[3], marker='d', label=r"$^{13}\textrm{ C }$-effective")
    axes[0,0].plot(COeps18[pmask], press[pmask]/100, color=colors[5], marker='d', label=r"$^{18}\textrm{ O }$-effective")

    
    CO = CO*1E-9
    COeps13 = 1e3*(lodautil.echam.get_ECHAM_tt(time, 'tracer_gp_E13CO', ncfid)/CO-1)
    COeps18 = 1e3*(lodautil.echam.get_ECHAM_tt(time, 'tracer_gp_E18CO', ncfid)/CO-1)
    CO = CO*1E9
    # axes[0].plot(CO[pmask], COeps13[pmask], color=colors[2], marker='d', label=r"$^{13}\textrm{ C }$")
    # axes[0].plot(CO[pmask], COeps18[pmask], color=colors[4], marker='d', label=r"$^{18}\textrm{ O }$")

    # axes[1].plot(CH4[pmask], COeps13[pmask], color=colors[3], marker='d', label=r"$^{13}\textrm{ C }$")

    # pdummy=np.linspace(200,0,50)
    k_oh_co, k_oh_13co, k_oh_c17o, k_oh_c18o= stisolib.co_3step_OH(press[pmask],temp[pmask])

    edummy=-1000*(k_oh_c18o/k_oh_co-1)
    axes[0,1].plot(edummy, press[pmask]/100, color=colors[2],  label=r"$^{18}\textrm{ O }$-equilibrium")

    edummy=-1000*(k_oh_13co/k_oh_co-1)
    axes[0,1].plot(edummy, press[pmask]/100, color=colors[1],  label=r"$^{13}\textrm{ C }$-equilibrium")

    axes[0,1].plot(COeps13[pmask], press[pmask]/100, color=colors[3], marker='d', label=r"$^{13}\textrm{ C }$-effective")
    axes[0,1].plot(COeps18[pmask], press[pmask]/100, color=colors[5], marker='d', label=r"$^{18}\textrm{ O }$-effective")

for ax in axes.ravel():
    handles, labels = scantools.getUniqueLegend(ax)
    ax.legend(handles=handles, labels=labels)
axes[0,1].set_title('Gromov 3-step-model')
axes[0,0].set_title('p-dependent fit')
fig.tight_layout()
fig.savefig(config.FigDir+'stico_eps_vs_tracer_prof_new.pdf')
