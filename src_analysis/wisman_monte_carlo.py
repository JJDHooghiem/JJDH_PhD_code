#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Don't remove the line below, it is checked by "one to run them all"
# --otrta-s--
# extension p means parallel, s is for single
"""
This code was written for the analysis presented in the dissertation of Joram Jan Dirk Hooghiem
"""
import multiprocessing
import time

import atmos
import matplotlib.pyplot as plt
import numpy as np
import config
import scan.wisman as wisman
import scantools
import stisolib
from lodautil import LISA_load
from scipy.optimize import nnls as nnls
# Create models from data
# mpl.style.use('/home/joram/.matplotlib/stylelib/paper_copernicus.mplstyle')
# Data obtained from noaa ftp-server. februari 2019.
midwayCO = np.round( np.mean([73.34, 71, 86.42, 87.01, 61.91, 61.49, 71.53, 72.57, 69.24, 70.46]))
midwayCO_std = np.round( np.std([73.34, 71, 86.42, 87.01, 61.91, 61.49, 71.53, 72.57, 69.24, 70.46]))
# run = sys.argv[1]
data = LISA_load()  # work with up to date data for the calculations
# define uncurtainties

iso_un_obs = 1 
mole_un_obs = 1.4 
mole_un = 1.4  # 7 from variability in aircore background
iso_un = 1 

weights = np.array([1E3, 1, 1, 1])

temp = data['20170905']['T'][0]
pres = data['20170905']['p'][0]*100  # in Pa
alt = data['20170905']['Altitude'][0]

CO = np.round(data['20170905']['CO'][0], 0)
C13O = data['20170905']['d13C(CO)'][0]
C18O = data['20170905']['d18O(CO)'][0]

CO_bg = np.round(data['20170906']['CO'][0], 0)
C13O_bg = data['20170906']['d13C(CO)'][0]
CO18_bg = data['20170906']['d18O(CO)'][0]

t = 25.0  # days
nden = atmos.ndens(temp, pres)

C12O16 = nden*CO*10**(-9)
C13O16 = C12O16*stisolib.delta_to_ratio(C13O, 'VPDB13')
C12O18 = C12O16*stisolib.delta_to_ratio(C18O, 'VSMOW18')
# back_calc returns final_strat, final
dt = 3600
C12O16, x = wisman.back_calc(temp, pres, C12O16, t*24*3600., 5*3600., dt, alt)
C13O16, x = wisman.back_calc(
    temp, pres, C13O16, t*24*3600., 5*3600., dt, alt, iso='C13')
C12O18, x = wisman.back_calc(
    temp, pres, C12O18, t*24*3600., 5*3600., dt, alt, iso='O18')
co_oh = np.round(C12O16/(nden*10**(-9)), 0)
C13_oh = np.round(stisolib.ratio_to_delta(C13O16/C12O16, 'VPDB13'), 1)
O18_oh = np.round(stisolib.ratio_to_delta(C12O18/C12O16, 'VSMOW18'), 1)


def solve_once():
    res = False
    while res != True:

        observation, plume, troposphere, stratosphere = monte_carlo_draw_input()
        fraction, error, errorcalc = wisman.monte_carlo_solve(
            observation, wisman.transform_end_members(plume, troposphere, stratosphere), weights)
        if np.round(np.sum(fraction), 7) == 1.0 and np.round(fraction[1], 4) > 0.0 and np.round(fraction[2], 4) > 0.000:

            residual = wisman.calc_residuals(
                observation, plume, troposphere, stratosphere, fraction)
            if abs(residual[0]) < mole_un_obs and abs(residual[1]) < 0.5 and abs(residual[2]) < 0.5:

                res = True
    return fraction


def processer(number):
    fractions[number] = solve_once()
    return


def run_monte_carlo_mp(number):
    global fractions
    manager = multiprocessing.Manager()
    fractions = manager.list([None]*number)
    pool = multiprocessing.Pool()
    pool.map(processer, range(number))

    pool.close()
    pool.join()

    return np.array(fractions[:])


table = '''
 Air mass                                   & Variable                 & Mean                                       & $\sigma$ & Distribution \\\\ \midrule
				           & \ch{{CO}}                & $0.5\cdot 10^{{6}}$ to $1.5\cdot 10^{{6}}$ & -          & uniform      \\\\
 \multicolumn{{1}}{{l}}{{Wildfire smoke}}  & $\delta ^{{13}}$\ch{{C}} & $-24.4$ to $-21.3$                         & -          & uniform      \\\\
	                                   & $\delta ^{{18}}$\ch{{O}} & $16.3$ to $18.0$                           & -          & uniform      \\\\ \midrule
                                           & \ch{{CO}}                & ${CO_bg:.0f}$                                  & ${mole_un:.1f}$        & normal       \\\\
 \multicolumn{{1}}{{l}}{{Stratosphere}}    & $\delta ^{{13}}$\ch{{C}} & ${C13O_bg:.1f}$                                & ${iso_un:.1f}$        & normal       \\\\
	                                   & $\delta ^{{18}}$\ch{{O}} & ${CO18_bg:.1f}$                                & ${iso_un:.1f}$        & normal       \\\\ \midrule
                                           & \ch{{CO}}                & ${midwayCO:.0f} $                                      & ${midwayCO_std:.0f}$        & normal       \\\\
 \multicolumn{{1}}{{l}}{{Troposphere}}     & $\delta ^{{13}}$\ch{{C}} & $-32$ to $-28$                             & -          & uniform      \\\\
	                                   & $\delta ^{{18}}$\ch{{O}} & $ -4$ to $0$                               & -          & uniform      \\\\ \midrule
                                           & \ch{{CO}}                & ${COl:.0f}      $                              & ${mole_un:.1f}$        & normal       \\\\
 \multicolumn{{1}}{{l}}{{ap}}              & $\delta ^{{13}}$\ch{{C}} & ${C13O:.1f}      $                             & ${iso_un_obs:.1f}$        & normal       \\\\
	                                   & $\delta ^{{18}}$\ch{{O}} & ${C18O:.1f}        $                           & ${iso_un_obs:.1f}$        & normal       \\\\ \midrule
                                           & \ch{{CO}}                & $  {co_oh:.1f}$                                & ${mole_un_obs:.1f}$        & normal       \\\\
 \multicolumn{{1}}{{l}}{{ap OH-Corrected}} & $\delta ^{{13}}$\ch{{C}} & ${C13_oh:.1f}  $                               & ${iso_un_obs:.1f}$        & normal       \\\\
					   & $\delta ^{{18}}$\ch{{O}} & ${O18_oh:.1f}      $                           & ${iso_un_obs:.1f}$        & normal       \\\\ \\bottomrule
'''.format(
    COl=CO,
    C13O=C13O,
    C18O=C18O,
    CO_bg=CO_bg,
    C13O_bg=C13O_bg,
    CO18_bg=CO18_bg,
    co_oh=co_oh,
    C13_oh=C13_oh,
    O18_oh=O18_oh,
    iso_un_obs=iso_un_obs,
    mole_un_obs=mole_un_obs,
    iso_un=iso_un,
    mole_un=mole_un,
    midwayCO=midwayCO,
    midwayCO_std=midwayCO_std
)
with open(config.TabDir+'wisman_input.tex', 'w') as f:
    f.write(table)
    f.close()

def monte_carlo_draw_input():
    '''
    Draws Monte carlo imput for smoke, troposphere, stratosphere end-members,
    and the observations. Changin the distribution type, or their parameters requires modification of the source code.
    OH can be set True if the OH corrected observation is to be used. THis is currently calculated using chemistry in the stratosphere only. Calculated ofline.
    in order to asses the effect of OH, the plume can be entered as variables.
    since the data can change these values have to be given as wel:

    '''
    O18_cp = np.random.normal(C18O, iso_un_obs)
    C13_cp = np.random.normal(C13O, iso_un_obs)
    CO_cp = np.random.normal(CO, mole_un_obs)

    observation = [CO_cp, C13_cp, O18_cp]

    # Our observations, most recent so lower uncertainty
    xs = np.random.normal(CO_bg, mole_un)
    # Our observations, most recent so lower uncertainty
    Cs = np.random.normal(C13O_bg, iso_un)
    # Our observations, most recent so lower uncertainty
    Os = np.random.normal(CO18_bg, iso_un)
    stratosphere = [xs, Cs, Os]

    xt = np.random.normal(midwayCO, midwayCO_std)  # ppb
    Ct = np.random.uniform(-32., -28)  # equal probability
    Ot = np.random.uniform(-4, 0)
    # Ct = np.random.normal(-32., iso_un)  # equal probability
    # Ot = np.random.normal(-4, iso_un)

    troposphere = [xt, Ct, Ot]

    xp = np.random.uniform(500000, 1500000)  # ppb
    Cp = np.random.uniform(-24.4, -21.3)
    Op = np.random.uniform(16.3, 18.0)

    plume = [xp, Cp, Op]

    return observation, plume, troposphere, stratosphere


t = time.time()

window = 5
bins = 100

number = 1000000
result = run_monte_carlo_mp(number)
print(time.time()-t)

# Redifine plume for OH correction

C18O = O18_oh
C13O = C13_oh
CO = co_oh

t = time.time()

result_oh = run_monte_carlo_mp(number)
print(time.time()-t)

# plot results
colors = config.GruvBoxColors
xlabs = [config.axl['f']]
ylabs = [config.axl['pdens']]
xlims = [(0, 1)]
ylims = [(0,5)]
fig, ax = scantools.plot_init(1, 1, xlabs=xlabs, ylabs=ylabs, xlims=xlims, ylims=ylims)
res1 = result.T[1]
res2 = result.T[2]

# mode1=statistics.mode(res1)
# mode2=statistics.mode(res2)

mad1 = scantools.mad(res1)
mad2 = scantools.mad(res2)
l1 = 'Troposphere\n'+'Median: '+str(np.round(np.median(res1), 2))+'\nMean: '+str(np.round(np.mean(
    res1), 2))+'\nMAD: '+str(np.round(mad1, 2))+'\nStd: '+'{:.2f}'.format(np.round(np.std(res1), 2))

l2 = 'Stratosphere\n'+'Median: '+str(np.round(np.median(res2), 2))+'\nMean: '+str(np.round(np.mean(
    res2), 2))+'\nMAD: '+str(np.round(mad2, 2))+'\nStd: '+'{:.2f}'.format(np.round(np.std(res2), 2))

plt.hist(res1, bins=100, color=colors[1], alpha=0.6, density='True', label=l1)
plt.hist(res2, bins=100, color=colors[2], alpha=0.6, density='True', label=l2)

res1 = result_oh.T[1]
res2 = result_oh.T[2]

# mode1=statistics.mode(res1)
# mode2=statistics.mode(res2)

mad1 = scantools.mad(res1)
mad2 = scantools.mad(res2)


l1 = 'Troposphere, OH cor.\n'+'Median: '+str(np.round(np.median(res1), 2))+'\nMean: '+str(np.round(
    np.mean(res1), 2))+'\nMAD: '+str(np.round(mad1, 2))+'\nStd: '+'{:.2f}'.format(np.round(np.std(res1), 2))
l2 = 'Stratosphere, OH cor.\n'+'Median: '+str(np.round(np.median(res2), 2))+'\nMean: '+str(np.round(
    np.mean(res2), 2))+'\nMAD: '+str(np.round(mad2, 2))+'\nStd: '+'{:.2f}'.format(np.round(np.std(res2), 2))

plt.hist(res1, bins=100, color=colors[3], alpha=0.6, density='True', label=l1)
plt.hist(res2, bins=100, color=colors[4], alpha=0.6, density='True', label=l2)

leg = ax.legend(ncol=2, loc=9)

fig.savefig(config.FigDir+'wisman_montecarlo.pdf', bbox_inches='tight')
