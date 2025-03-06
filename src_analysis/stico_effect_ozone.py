#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Don't remove the line below, it is checked by "one to run them all"
# --otrta-p--
# extension p means parallel, s is for singleimport atmos

import numpy as np
import config
import scan.stico as stico
import scantools
import atmos
import lodautil

def oz_echam(dat,interpolated=True):
    """echamModelAtLisa.

    Parameters
    ----------
    interpolated :
        interpolated
    """
    LISA = lodautil.flattened_LISA()
    ncfid = lodautil.get_ncfid(interpolated=interpolated, daymean=True)#,experiment='eq1z'
    data = lodautil.date_select(LISA, dat)
    time = np.floor(lodautil.get_sample_dt(data)[0][-1])+0.5

    O3 = lodautil.echam.get_ECHAM_tt(time, 'tracer_gp_O3', ncfid)
    O3P = lodautil.echam.get_ECHAM_tt(time, 'tracer_gp_O3P', ncfid)
    press = lodautil.echam.get_ECHAM_pp(time, ncfid)
    temp = lodautil.echam.get_ECHAM_tt(time, 'ECHAM5_tm1', ncfid)
    return O3, press,temp , O3P
altitude = np.linspace(2000, 74000, 37)
press = []
temp = []
for a in altitude:
    p, t = atmos.Standard_atmos(a)
    press.append(p)
    temp.append(t)
press = np.array(press)
temp = np.array(temp)
o3 = 1*atmos.Standard_ozone(altitude)*1E-6
# for dat in lodautil.lisa.get_unique_dates()[1]:
#     o3, press,temp,o3p =oz_echam(dat)
#     ma=(o3p/o3)[np.argmax(o3)]

#     print(ma)
# print(press,temp,o3)
# for t in temp:
# result_noO3,result_withO3=map(np.array,zip(*[stico.ozone_in_CO(p,t,o) for p,t,o in zip(press,temp,o3)]))
# print(stico.ozone_in_CO(press,temp,o3))

ylabs = [config.axl['p']]*2
xlabs = [config.axl['fx'], config.axl['D18o']]
fig, axes = scantools.plot_init(1, 2, xlabs, ylabs)
result_noO3, result_withO3, nk_o, nk_o2, nk_o3 = stico.ozone_in_CO(
    press, temp, o3)
f_nk_o, f_nk_o2, f_nk_o3 = stico.rel_o(nk_o, nk_o2, nk_o3)

axes[0].plot(100*f_nk_o, press, 'k:', label=r'$\textrm{O}$, $k_{\textrm{JPL}}$, $\times100$')
axes[0].plot(f_nk_o3, press, 'k-', label=r'$\textrm{O}_{3}$, $k_{\textrm{JPL}}$')
axes[1].plot(result_withO3-result_noO3, press,
             'k-', label=r"$k_{\textrm{JPL}}$")

result_noO3, result_withO3, nk_o, nk_o2, nk_o3 = stico.ozone_in_CO(
    press, temp, o3, rates='caaba')
f_nk_o, f_nk_o2, f_nk_o3 = stico.rel_o(nk_o, nk_o2, nk_o3)

axes[0].plot(100*f_nk_o, press, ':', color="grey", label=r'$\textrm{O}$, $k_{\textrm{CAABA}}$, $\times100$')
axes[0].plot(f_nk_o3, press, '-', color="grey", label=r'$\textrm{O}_{3}$, $k_{\textrm{CAABA}}$')
axes[1].plot(result_withO3-result_noO3, press, 'k:', label=r"$k_{\textrm{CAABA}}$")

# plt.plot(result_withO3-result_noO3,press,'-',label='T (K) = {:.0f}'.format(t))

# result_noO3,result_withO3,nk_o, nk_o2,nk_o3=stico.ozone_in_CO(press,temp,o3,rates='caaba')

# o3=o3*10
# result_noO3,result_withO3,nk_o, nk_o2,nk_o3=stico.ozone_in_CO(press,temp,o3)
# plt.plot(result_withO3-result_noO3,press,'-',label='T (K) = {:.0f}'.format(t))

# result_noO3,result_withO3,nk_o, nk_o2,nk_o3=stico.ozone_in_CO(press,temp,o3,rates='caaba')
# plt.plot(result_withO3-result_noO3,press,':',label='T (K) = {:.0f}'.format(t))
# plt.plot(o3,press)
axes[0].set_yscale('log')
axes[0].set_ylim(100000, 1)
axes[0].set_xlim(0, 0.005)
axes[0].legend()
axes[1].set_yscale('log')
axes[1].set_ylim(100000, 1)
axes[1].legend()
fig.tight_layout()
fig.savefig(config.FigDir+'stico_effect_ozone.pdf')
