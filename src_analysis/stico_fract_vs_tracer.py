#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Don't remove the line below, it is checked by "one to run them all"
# --otrta-p--
# extension p means parallel, s is for single
import scantools
import lodautil
import config
import numpy as np
colors = config.GruvBoxColors
LISA = lodautil.flattened_LISA()
ncfid = lodautil.get_ncfid(interpolated=False, daymean=False)
xlabs = [config.axl['co'], config.axl['ch4']]
ylabs = [config.axl['enr']]*2
xlims = None
ylims = None
fig, axes = scantools.plot_init(1, 2, xlabs=xlabs, ylabs=ylabs, xlims=xlims, ylims=ylims)
for i,dat in enumerate(lodautil.get_dates(LISA)):
# for dat in ['2017-09-04']:
    data = lodautil.date_select(LISA, dat)
    # 12:00 utc:
    time = np.floor(lodautil.get_sample_dt(data)[0][2])+0.5
    CO = lodautil.echam.get_ECHAM_tt(time, 'tracer_gp_CO', ncfid)
    CH4 = lodautil.echam.get_ECHAM_tt(time, 'tracer_gp_CH4', ncfid)*1E9
    COeps13 = 1e3*(lodautil.echam.get_ECHAM_tt(time, 'tracer_gp_E13pCO', ncfid)/CO-1)
    COeps18 = 1e3*(lodautil.echam.get_ECHAM_tt(time, 'tracer_gp_E18pCO', ncfid)/CO-1)
    CO = CO*1E9

    press = lodautil.echam.get_ECHAM_pp(time, ncfid)
    pmask = (press > 0) & (press < 25)
    axes[0].plot(press[pmask], COeps13[pmask], color=colors[2], marker='o', label=r"$^{13}\textrm{ C }$")
    axes[0].plot(press[pmask], COeps18[pmask], color=colors[i], marker='o', label=r"$^{18}\textrm{ O }$ "+dat)

    # axes[1].plot(CH4[pmask], COeps13[pmask], color=colors[3], marker='o', label=r"$^{13}\textrm{ C }$")
    # axes[1].plot(CH4[pmask], COeps18[pmask], color=colors[5], marker='o', label=r"$^{18}\textrm{ O }$")

    
    CO = CO*1E-9
    COeps13 = 1e3*(lodautil.echam.get_ECHAM_tt(time, 'tracer_gp_E13CO', ncfid)/CO-1)
    COeps18 = 1e3*(lodautil.echam.get_ECHAM_tt(time, 'tracer_gp_E18CO', ncfid)/CO-1)
    CO = CO*1E9
    # axes[0].plot(CO[pmask], COeps13[pmask], color=colors[2], marker='d', label=r"$^{13}\textrm{ C }$")
    # axes[0].plot(CO[pmask], COeps18[pmask], color=colors[4], marker='d', label=r"$^{18}\textrm{ O }$")

    axes[1].plot(CH4[pmask], COeps13[pmask], color=colors[3], marker='d', label=r"$^{13}\textrm{ C }$")
    axes[1].plot(CH4[pmask], COeps18[pmask], color=colors[5], marker='d', label=r"$^{18}\textrm{ O }$")
for ax in axes.ravel():
    handles, labels = scantools.getUniqueLegend(ax)
    ax.legend(handles=handles, labels=labels)
fig.tight_layout()
fig.savefig(config.FigDir+'stico_eps_vs_tracer_prof.pdf')
