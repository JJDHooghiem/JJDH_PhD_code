#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Don't remove the line below, it is checked by "one to run them all"
# --otrta-p--
# extension p means parallel, s is for single
"""
This code was written for the analysis presented in the dissertation of Joram Jan Dirk Hooghiem
"""
"""
Created on Fri Nov 30 10:57:28 2018

@author: meisu
"""
#%%
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import scantools 
import config
#%%
#Data per bag [d17O_corr, d17_18, D17O, CO2_corr, d13C_fit, d18O_Pfit, d18O_fit]
#Errors [sd636_Pco2, sd628_Pco2, sd627_co2]

b3m1a = np.array([-1.596566547,	-0.127379488,	-8.174630474,	422.2165192,	-8.320634002,	13.07350527,	13.0599874])
b3m1b = np.array([-1.807884095,	-0.149413708,	-8.159901031,	422.1853228,	-8.375101098,	13.92283356,	13.8961433])

err_b3m1a = np.array([0.005638109,	0.033157933,	0.034560788])
err_b3m1b = np.array([0.025355143,	0.045029405,	0.033615357])

diff_b3m1 = b3m1b - b3m1a
err_diff_b3m1 = np.sqrt(err_b3m1a**2+err_b3m1b**2)

b3m2a = np.array([-1.677853403,	-0.133730057,	-8.262637515,	422.3420444,	-8.320787716,	13.89258767,	13.84822187])
b3m2b = np.array([-1.960000591,	-0.16702155,	-8.121938799,	422.3786042,	-8.441949358,	11.4796472,	11.51080679])
b3m2c = np.array([-1.995435677,	-0.173026164,	-8.051779744,	422.3793402,	-8.441639242,	11.78620583,	11.96715906])

err_b3m2a=np.array([0.02989547,	0.032898765,	0.019158668])
err_b3m2b=np.array([0.025771219,	0.037701519,	0.067564791])
err_b3m2c=np.array([0.02297779,	0.023230477,	0.070421412])

diff_b3m2 = b3m2b - b3m2a
err_diff_b3m2 = np.sqrt(err_b3m2a**2+err_b3m2b**2)

b4m1a = np.array([-1.606977389,	-0.127622614,	-8.215144353,	422.2059711,	-8.314139885,	12.35600141,	12.56397689])
b4m1b = np.array([-1.84458147,	-0.154284153,	-8.121478373,	421.296147,	-8.359420517,	11.72721992,	11.79721519])

err_b4m1a=np.array([0.014834821,	0.00876999,	0.030068578])
err_b4m1b=np.array([0.030582083, 0.030172096,	0.047486839])

diff_b4m1 = b4m1b - b4m1a
err_diff_b4m1 = np.sqrt(err_b4m1a**2+err_b4m1b**2)

b5m1a = np.array([-1.671969396,	-0.133018801,	-8.268660123,	422.3047912,	-8.381490348,	13.30543956,	13.50427902])
b5m1b = np.array([-1.748491633,	-0.143479933,	-8.145506217,	421.9755154,	-8.390303,	11.70588739,	11.84267084])

err_b5m1a=np.array([0.037686654,	0.043953468,	0.068245547])
err_b5m1b=np.array([0.014542963,	0.028792085,	0.075801528])

diff_b5m1 = b5m1b - b5m1a
err_diff_b5m1 = np.sqrt(err_b5m1a**2+err_b5m1b**2)

b6m1a = np.array([-1.698415333,	-0.136012018,	-8.252298084,	422.4878778,	-8.390822974,	12.99557354,	13.21469993])
b6m1b = np.array([-1.851210337,	-0.152518386,	-8.223008637,	422.0715922,	-8.434879559,	12.26699259,	12.3756382])

err_b6m1a=np.array([0.020848452,	0.022396874,	0.007148518])
err_b6m1b=np.array([0.031114416,	0.011623563,	0.091436461])

diff_b6m1 = b6m1b - b6m1a
err_diff_b6m1 = np.sqrt(err_b6m1a**2+err_b6m1b**2)

b7m1a = np.array([-1.741069549,	-0.140250301,	-8.256836824,	422.3674644,	-8.406202146,	12.32293294,	12.55029779])
b7m1b = np.array([-1.633025865,	-0.133506708,	-8.053565581,	422.1878492,	-8.424828723,	12.31311764,	12.5469278])

err_b7m1a=np.array([0.034818515,	0.034913974,	0.060580887])
err_b7m1b=np.array([0.018968335,	0.026244395,	0.034849898])

diff_b7m1 = b7m1b - b7m1a
err_diff_b7m1 = np.sqrt(err_b7m1a**2+err_b7m1b**2)

cm1 = np.array([-1.663393477,	-0.132263877,	-8.263669507,	422.1599377,	-8.329617738,	11.60686131,	11.63423848])
cm2 = np.array([-1.734436079,	-0.138626241,	-8.301081691,	422.3737363,	-8.50718929,	12.98823623,	12.65661297])
cm3 = np.array([-1.933348445,	-0.153557232,	-8.541455156,	422.3605087,	-8.932229889,	12.30552858,	12.16114232])
cm4 = np.array([-1.815638053,	-0.144759937,	-8.398492912,	422.4030572,	-7.939118125,	10.93937713,	10.86862448])
cm5 = np.array([-1.454312292,	-0.115819863,	-8.044015156,	422.3793329,	-8.584425364,	14.46136076,	14.55620249])
cm6 = np.array([-1.655153696,	-0.134300083,	-8.123980091,	422.3304636,	-8.400550501,	11.73222911,	11.77451552])
cm7 = np.array([-1.580238422,	-0.128081666,	-8.055957033,	422.2952077,	-8.239061139,	12.36159851,	12.23577141])
cm8 = np.array([-1.55678364,	-0.125872923,	-8.048194715,	422.3237588,	-8.262964116,	12.81939732,	12.9423075])

err_cm1 = np.array([0.029638183,	0.024331678,	0.061486615])
err_cm2 = np.array([0.895302687,	0.054579612,	0.14416074])
err_cm3 = np.array([0.754159979,	0.042057093,	0.701568102])
err_cm4 = np.array([1.777338782,	0.037532835,	0.162735834])
err_cm5 = np.array([1.326401603,	0.069751973,	0.280255614])
err_cm6 = np.array([0.030757066,	0.016625855,	0.045297825])
err_cm7 = np.array([0.038406029,	0.01119078,	0.045708504])
err_cm8 = np.array([0.01139627,	0.012777445,	0.036946551])
#%% alle metingen
d18O_fit = np.array([b3m1a[6], b3m1b[6], b3m2a[6], b3m2b[6], b3m2c[6], b4m1a[6], b4m1b[6], b5m1a[6], b5m1b[6], b6m1a[6], b6m1b[6], b7m1a[6], b7m1b[6]])

d18O_Pfit = np.array([b3m1a[5], b3m1b[5], b3m2a[5], b3m2b[5], b3m2c[5], b4m1a[5], b4m1b[5], b5m1a[5], b5m1b[5], b6m1a[5], b6m1b[5], b7m1a[5], b7m1b[5]])
e_d18O_Pfit = np.array([err_b3m1a[1], err_b3m1b[1], err_b3m2a[1], err_b3m2b[1], err_b3m2c[1], err_b4m1a[1], err_b4m1b[1], err_b5m1a[1], err_b5m1b[1], err_b6m1a[1], err_b6m1b[1], err_b7m1a[1], err_b7m1b[1]])

d13C_fit = np.array([b3m1a[4], b3m1b[4], b3m2a[4], b3m2b[4], b3m2c[4], b4m1a[4], b4m1b[4], b5m1a[4], b5m1b[4], b6m1a[4], b6m1b[4], b7m1a[4], b7m1b[4]])
e_d13C_fit = np.array([err_b3m1a[0], err_b3m1b[0], err_b3m2a[0], err_b3m2b[0], err_b3m2c[0], err_b4m1a[0], err_b4m1b[0], err_b5m1a[0], err_b5m1b[0], err_b6m1a[0], err_b6m1b[0], err_b7m1a[0], err_b7m1b[0]])

CO2_corr = np.array([b3m1a[3], b3m1b[3], b3m2a[3], b3m2b[3], b3m2c[3], b4m1a[3], b4m1b[3], b5m1a[3], b5m1b[3], b6m1a[3], b6m1b[3], b7m1a[3], b7m1b[3]])

D17O = np.array([b3m1a[2], b3m1b[2], b3m2a[2], b3m2b[2], b3m2c[2], b4m1a[2], b4m1b[2], b5m1a[2], b5m1b[2], b6m1a[2], b6m1b[2], b7m1a[2], b7m1b[2]])

d17_18 = np.array([b3m1a[1], b3m1b[1], b3m2a[1], b3m2b[1], b3m2c[1], b4m1a[1], b4m1b[1], b5m1a[1], b5m1b[1], b6m1a[1], b6m1b[1], b7m1a[1], b7m1b[1]])

d17O_corr = np.array([b3m1a[0], b3m1b[0], b3m2a[0], b3m2b[0], b3m2c[0], b4m1a[0], b4m1b[0], b5m1a[0], b5m1b[0], b6m1a[0], b6m1b[0], b7m1a[0], b7m1b[0]])
e_d17O_corr = np.array([err_b3m1a[2], err_b3m1b[2], err_b3m2a[2], err_b3m2b[2], err_b3m2c[2], err_b4m1a[2], err_b4m1b[2], err_b5m1a[2], err_b5m1b[2], err_b6m1a[2], err_b6m1b[2], err_b7m1a[2], err_b7m1b[2]])

x = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14])

plt.figure(1)
plt.plot(x[0:5], d18O_fit[0:5], linestyle='None', marker='o', color='r')
plt.plot(x[5:7], d18O_fit[5:7], linestyle='None', marker='o', color='b')
plt.plot(x[7:9], d18O_fit[7:9], linestyle='None', marker='o', color='g')
plt.plot(x[9:11], d18O_fit[9:11], linestyle='None', marker='o', color='m')
plt.plot(x[11:13], d18O_fit[11:13], linestyle='None', marker='o', color='orange')
plt.axhline(y=cm1[6])
#plt.axhline(y=cm2[6], color='red')
#plt.axhline(y=cm3[6], color='green')
#plt.axhline(y=cm4[6], color='yellow')
#plt.axhline(y=cm5[6], color='purple')
plt.axhline(y=cm6[6], color='orange')
plt.axhline(y=cm7[6], color='pink')
plt.axhline(y=cm8[6], color='magenta')
plt.title('d18O_fit')
#xticks1=['bag 3', 'bag 3', 'bag 4', 'bag 5', 'bag 6', 'bag 7']
#plt.xticks(x,xticks1) 

plt.figure(2)
plt.errorbar(x[0:5], d18O_Pfit[0:5], e_d18O_Pfit[0:5], linestyle='None', marker='o', color='r')
plt.errorbar(x[5:7], d18O_Pfit[5:7], e_d18O_Pfit[5:7], linestyle='None', marker='o', color='b')
plt.errorbar(x[7:9], d18O_Pfit[7:9], e_d18O_Pfit[7:9], linestyle='None', marker='o', color='g')
plt.errorbar(x[9:11], d18O_Pfit[9:11], e_d18O_Pfit[9:11], linestyle='None', marker='o', color='m')
plt.errorbar(x[11:13], d18O_Pfit[11:13], e_d18O_Pfit[11:13], linestyle='None', marker='o', color='orange')
plt.axhline(y=cm1[5])
#plt.axhline(y=cm2[5], color='red')
#plt.axhline(y=cm3[5], color='green')
#plt.axhline(y=cm4[5], color='yellow')
#plt.axhline(y=cm5[5], color='purple')
plt.axhline(y=cm6[5], color='orange')
plt.axhline(y=cm7[5], color='pink')
plt.axhline(y=cm8[5], color='magenta')
plt.title('d18O_Pfit')

plt.figure(3)
plt.errorbar(x[0:5], d13C_fit[0:5], e_d13C_fit[0:5], linestyle='None', marker='o', color='r')
plt.errorbar(x[5:7], d13C_fit[5:7], e_d13C_fit[5:7], linestyle='None', marker='o', color='b')
plt.errorbar(x[7:9], d13C_fit[7:9], e_d13C_fit[7:9], linestyle='None', marker='o', color='g')
plt.errorbar(x[9:11], d13C_fit[9:11], e_d13C_fit[9:11], linestyle='None', marker='o', color='m')
plt.errorbar(x[11:13], d13C_fit[11:13], e_d13C_fit[11:13], linestyle='None', marker='o', color='orange')
plt.axhline(y=cm1[4])
#plt.axhline(y=cm2[4], color='red')
#plt.axhline(y=cm3[4], color='green')
#plt.axhline(y=cm4[4], color='yellow')
#plt.axhline(y=cm5[4], color='purple')
plt.axhline(y=cm6[4], color='orange')
plt.axhline(y=cm7[4], color='pink')
plt.axhline(y=cm8[4], color='magenta')
plt.title('d13C_fit')

plt.figure(4)
plt.plot(x[0:5], CO2_corr[0:5], linestyle='None', marker='o', color='r')
plt.plot(x[5:7], CO2_corr[5:7], linestyle='None', marker='o', color='b')
plt.plot(x[7:9], CO2_corr[7:9], linestyle='None', marker='o', color='g')
plt.plot(x[9:11], CO2_corr[9:11], linestyle='None', marker='o', color='m')
plt.plot(x[11:13], CO2_corr[11:13], linestyle='None', marker='o', color='orange')
plt.title('CO2_corr')
plt.axhline(y=cm1[3])
#plt.axhline(y=cm2[3], color='red')
#plt.axhline(y=cm3[3], color='green')
#plt.axhline(y=cm4[3], color='yellow')
#plt.axhline(y=cm5[3], color='purple')
plt.axhline(y=cm6[3], color='orange')
plt.axhline(y=cm7[3], color='pink')
plt.axhline(y=cm8[3], color='magenta')

plt.figure(5)
plt.errorbar(x[0:5], d17O_corr[0:5], e_d17O_corr[0:5], linestyle='None', marker='o', color='r')
plt.errorbar(x[5:7], d17O_corr[5:7], e_d17O_corr[5:7], linestyle='None', marker='o', color='b')
plt.errorbar(x[7:9], d17O_corr[7:9], e_d17O_corr[7:9], linestyle='None', marker='o', color='g')
plt.errorbar(x[9:11], d17O_corr[9:11], e_d17O_corr[9:11], linestyle='None', marker='o', color='m')
plt.errorbar(x[11:13], d17O_corr[11:13], e_d17O_corr[11:13], linestyle='None', marker='o', color='orange')
plt.title('d17O_corr')
plt.axhline(y=cm1[0])
#plt.axhline(y=cm2[0], color='red')
#plt.axhline(y=cm3[0], color='green')
#plt.axhline(y=cm4[0], color='yellow')
#plt.axhline(y=cm5[0], color='purple')
plt.axhline(y=cm6[0], color='orange')
plt.axhline(y=cm7[0], color='pink')
plt.axhline(y=cm8[0], color='magenta')

plt.figure(6)
plt.plot(x[0:5], D17O[0:5], linestyle='None', marker='o', color='r')
plt.plot(x[5:7], D17O[5:7], linestyle='None', marker='o', color='b')
plt.plot(x[7:9], D17O[7:9], linestyle='None', marker='o', color='g')
plt.plot(x[9:11], D17O[9:11], linestyle='None', marker='o', color='m')
plt.plot(x[11:13], D17O[11:13], linestyle='None', marker='o', color='orange')
plt.title('D17O')
plt.axhline(y=cm1[2])
#plt.axhline(y=cm2[2], color='red')
#plt.axhline(y=cm3[2], color='green')
#plt.axhline(y=cm4[2], color='yellow')
#plt.axhline(y=cm5[2], color='purple')
plt.axhline(y=cm6[2], color='orange')
plt.axhline(y=cm7[2], color='pink')
plt.axhline(y=cm8[2], color='magenta')

plt.figure(7)
plt.plot(x[0:5], d17_18[0:5], linestyle='None', marker='o', color='r')
plt.plot(x[5:7], d17_18[5:7], linestyle='None', marker='o', color='b')
plt.plot(x[7:9], d17_18[7:9], linestyle='None', marker='o', color='g')
plt.plot(x[9:11], d17_18[9:11], linestyle='None', marker='o', color='m')
plt.plot(x[11:13], d17_18[11:13], linestyle='None', marker='o', color='orange')
plt.title('d17_18')
plt.axhline(y=cm1[1])
#plt.axhline(y=cm2[1], color='red')
#plt.axhline(y=cm3[1], color='green')
#plt.axhline(y=cm4[1], color='yellow')
#plt.axhline(y=cm5[1], color='purple')
plt.axhline(y=cm6[1], color='orange')
plt.axhline(y=cm7[1], color='pink')
plt.axhline(y=cm8[1], color='magenta')
#%% Meting na vullen
#d18O_fit = np.array([b3m1a[5], b3m2a[5], b4m1a[5], b5m1a[5], b6m1a[5], b7m1a[5]])

d18O_Pfit = np.array([b3m1a[5], b3m2a[5], b4m1a[5], b5m1a[5], b6m1a[5], b7m1a[5]])
e_d18O_Pfit = np.array([err_b3m1a[1], err_b3m2a[1], err_b4m1a[1], err_b5m1a[1], err_b6m1a[1], err_b7m1a[1]])

d13C_fit = np.array([b3m1a[4], b3m2a[4], b4m1a[4], b5m1a[4], b6m1a[4], b7m1a[4]])
e_d13C_fit = np.array([err_b3m1a[0], err_b3m2a[0], err_b4m1a[0], err_b5m1a[0], err_b6m1a[0], err_b7m1a[0]])

#CO2_corr = np.array([b3m1a[2], b3m2a[2], b4m1a[2], b5m1a[2], b6m1a[2], b7m1a[2]])

d17O_corr = np.array([b3m1a[0], b3m2a[0], b4m1a[0], b5m1a[0], b6m1a[0], b7m1a[0]])
e_d17O_corr = np.array([err_b3m1a[2], err_b3m2a[2], err_b4m1a[2], err_b5m1a[2], err_b6m1a[2], err_b7m1a[2]])

#D17O = np.array([b3m1a[0], b3m2a[0], b4m1a[0], b5m1a[0], b6m1a[0], b7m1a[0]])

a_cyl_d18O_Pfit = np.mean([cm1[5], cm6[5], cm7[5], cm8[5]])
a_cyl_d13C_fit = np.mean([cm1[4], cm6[4], cm7[4], cm8[4]])
a_cyl_d17O_corr = np.mean([cm1[0], cm6[0], cm7[0], cm8[0]])

std_cyl_d18O_Pfit = np.std([cm1[5], cm6[5], cm7[5], cm8[5]])
std_cyl_d13C_fit = np.std([cm1[4], cm6[4], cm7[4], cm8[4]])
std_cyl_d17O_corr = np.std([cm1[0], cm6[0], cm7[0], cm8[0]])

fig, ax = plt.subplots (3,1, sharex=True)

x = np.array([1, 2, 3, 4, 5, 6])

#plt.figure(7)
#plt.plot(x, d18O_fit, linestyle='None', marker='o')
#plt.axhline(y=12.56)
#xticks1=['bag 3', 'bag 3', 'bag 4', 'bag 5', 'bag 6', 'bag 7']
#plt.xticks(x,xticks1) 


ax[0].errorbar(x, d18O_Pfit, e_d18O_Pfit, linestyle='None', marker='o', markersize=12)
ax[0].axhline(y=a_cyl_d18O_Pfit, color='red')
ax[0].axhline(y=a_cyl_d18O_Pfit+std_cyl_d18O_Pfit, color='grey', linestyle='--')
ax[0].axhline(y=a_cyl_d18O_Pfit-std_cyl_d18O_Pfit, color='grey', linestyle='--')
ax[0].set_ylabel(u'\u2030', fontsize=16)
ax[0].set_title('$\delta^{18}O$', fontsize=16)

ax[1].errorbar(x, d13C_fit, e_d13C_fit, linestyle='None', marker='o', markersize=12)
ax[1].axhline(y=a_cyl_d13C_fit, color='red')
ax[1].axhline(y=a_cyl_d13C_fit+std_cyl_d13C_fit, color='grey', linestyle='--')
ax[1].axhline(y=a_cyl_d13C_fit-std_cyl_d13C_fit, color='grey', linestyle='--')
ax[1].set_ylabel(u'\u2030', fontsize=16)
ax[1].set_title('$\delta^{13}C$', fontsize=16)

#plt.figure(10)
#plt.plot(x, CO2_corr, linestyle='None', marker='o')

ax[2].errorbar(x, d17O_corr, e_d17O_corr, linestyle='None', marker='o', markersize=12)
ax[2].axhline(y=a_cyl_d17O_corr, color='red')
ax[2].axhline(y=a_cyl_d17O_corr+std_cyl_d17O_corr, color='grey', linestyle='--')
ax[2].axhline(y=a_cyl_d17O_corr-std_cyl_d17O_corr, color='grey', linestyle='--')
ax[2].set_ylabel(u'\u2030', fontsize=16)
ax[2].set_title('$\delta^{17}O$', fontsize=16)

#plt.figure(12)
#plt.plot(x, D17O, linestyle='None', marker='o')

plt.setp(ax, xticks=[1, 2, 3, 4, 5, 6], xticklabels=['Bag 3', 'Bag 3', 'Bag 4', 'Bag 5', 'Bag 6', 'Bag 7'])

ax[1].yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

for item in (ax[2].get_yticklabels()):
    item.set_fontsize(14)
    
for item in (ax[1].get_yticklabels()):
    item.set_fontsize(14)
    
for item in (ax[0].get_yticklabels()):
    item.set_fontsize(14)
    
for item in (ax[2].get_xticklabels()):
    item.set_fontsize(14)

fig.suptitle('Stable isotope ratios in sample bags immediately after filling', fontsize=18)
#%% Verschil tussen metingen

#diff_d18O_fit=np.array([diff_b3m1[5], diff_b3m2[5], diff_b4m1[5], diff_b5m1[5], diff_b6m1[5], diff_b7m1[5]])

#diff_d18O_Pfit=np.array([diff_b3m1[4], diff_b3m2[4], diff_b4m1[4], diff_b5m1[4], diff_b6m1[4], diff_b7m1[4]])

#diff_d13C_fit=np.array([diff_b3m1[3], diff_b3m2[3], diff_b4m1[3], diff_b5m1[3], diff_b6m1[3], diff_b7m1[3]])

#diff_CO2_corr=np.array([diff_b3m1[2], diff_b3m2[2], diff_b4m1[2], diff_b5m1[2], diff_b6m1[2], diff_b7m1[2]])

#diff_d17O_corr=np.array([diff_b3m1[1], diff_b3m2[1], diff_b4m1[1], diff_b5m1[1], diff_b6m1[1], diff_b7m1[1]])

#diff_D17O=np.array([diff_b3m1[0], diff_b3m2[0], diff_b4m1[0], diff_b5m1[0], diff_b6m1[0], diff_b7m1[0]])

#x=np.array([1, 2, 3, 4, 5, 6])

#plt.figure(13)
#plt.plot(x, diff_d18O_fit, linestyle='None', marker='o')
#plt.title('d18O_fit')

#plt.figure(14)
#plt.plot(x, diff_d18O_Pfit, linestyle='None', marker='o')
#plt.title('d18O_Pfit')

#plt.figure(15)
#plt.plot(x, diff_d13C_fit, linestyle='None', marker='o')
#plt.title('d13C_fit')

#plt.figure(16)
#plt.plot(x, diff_CO2_corr, linestyle='None', marker='o')
#plt.title('CO2_corr')

#plt.figure(17)
#plt.plot(x, diff_d17O_corr, linestyle='None', marker='o')
#plt.title('d17O_corr')

#plt.figure(18)
#plt.plot(x, diff_D17O, linestyle='None', marker='o')
#plt.title('D17O')

diff_d18O_Pfit=np.array([diff_b3m1[5], diff_b3m2[5], diff_b4m1[5], diff_b5m1[5], diff_b6m1[5], diff_b7m1[5]])
err_diff_d18O_Pfit=np.array([err_diff_b3m1[1], err_diff_b3m2[1], err_diff_b4m1[1], err_diff_b5m1[1], err_diff_b6m1[1], err_diff_b7m1[1]])

diff_d13C_fit=np.array([diff_b3m1[4], diff_b3m2[4], diff_b4m1[4], diff_b5m1[4], diff_b6m1[4], diff_b7m1[4]])
err_diff_d13C_fit=np.array([err_diff_b3m1[0], err_diff_b3m2[0], err_diff_b4m1[0], err_diff_b5m1[0], err_diff_b6m1[0], err_diff_b7m1[0]])

diff_d17O_corr=np.array([diff_b3m1[0], diff_b3m2[0], diff_b4m1[0], diff_b5m1[0], diff_b6m1[0], diff_b7m1[0]])
err_diff_d17O_corr=np.array([err_diff_b3m1[2], err_diff_b3m2[2], err_diff_b4m1[2], err_diff_b5m1[2], err_diff_b6m1[2], err_diff_b7m1[2]])

x=np.array([1, 2, 3, 4, 5, 6])

plt.figure(10)
plt.errorbar(x, diff_d18O_Pfit, err_diff_d18O_Pfit, linestyle='None', marker='o')
plt.title('d18O_Pfit')

plt.figure(11)
plt.errorbar(x, diff_d13C_fit, err_diff_d13C_fit, linestyle='None', marker='o')
plt.title('d13C_fit')

plt.figure(12)
plt.errorbar(x, diff_d17O_corr, err_diff_d17O_corr, linestyle='None', marker='o')
plt.title('d17O_corr')
#%% Verschil gecorrigeerd voor tijd

diff_b3m1_cor = diff_b3m1/119.35
err_diff_b3m1_cor = err_diff_b3m1/119.35

diff_b3m2_cor = diff_b3m2/263.37
err_diff_b3m2_cor = err_diff_b3m2/263.37

diff_b4_cor = diff_b4m1/166.87
err_diff_b4_cor = err_diff_b4m1/166.87

diff_b5_cor = diff_b5m1/165.25
err_diff_b5_cor = err_diff_b5m1/165.25

diff_b6_cor = diff_b6m1/168.05
err_diff_b6_cor = err_diff_b6m1/168.05

diff_b7_cor = diff_b7m1/68.75
err_diff_b7_cor = err_diff_b7m1/68.75

#diff_d18O_fit=np.array([diff_b3m1_cor[5], diff_b4_cor[5], diff_b5_cor[5], diff_b6_cor[5], diff_b7_cor[5]])

diff_d18O_Pfit=np.array([diff_b3m1_cor[5], diff_b3m2_cor[5], diff_b4_cor[5], diff_b5_cor[5], diff_b6_cor[5], diff_b7_cor[5]])
err_diff_d18O_Pfit=np.array([err_diff_b3m1_cor[1], err_diff_b3m2_cor[1], err_diff_b4_cor[1], err_diff_b5_cor[1], err_diff_b6_cor[1], err_diff_b7_cor[1]])

diff_d13C_fit=np.array([diff_b3m1_cor[4], diff_b3m2_cor[4], diff_b4_cor[4], diff_b5_cor[4], diff_b6_cor[4], diff_b7_cor[4]])
err_diff_d13C_fit=np.array([err_diff_b3m1_cor[0], err_diff_b3m2_cor[0], err_diff_b4_cor[0], err_diff_b5_cor[0], err_diff_b6_cor[0], err_diff_b7_cor[0]])

#diff_CO2_corr=np.array([diff_b3m1_cor[2], diff_b4_cor[2], diff_b5_cor[2], diff_b6_cor[2], diff_b7_cor[2]])

diff_d17O_corr=np.array([diff_b3m1_cor[0], diff_b3m2_cor[0], diff_b4_cor[0], diff_b5_cor[0], diff_b6_cor[0], diff_b7_cor[0]])
err_diff_d17O_corr=np.array([err_diff_b3m1_cor[2], err_diff_b3m2_cor[2], err_diff_b4_cor[2], err_diff_b5_cor[2], err_diff_b6_cor[2], err_diff_b7_cor[2]])

#diff_D17O=np.array([diff_b3m1_cor[0], diff_b4_cor[0], diff_b5_cor[0], diff_b6_cor[0], diff_b7_cor[0]])

x=np.array([1, 2, 3, 4, 5, 6])
fig, ax = plt.subplots (3,1, sharex=True)

#plt.figure(19)
#plt.plot(x, diff_d18O_fit,, linestyle='None', marker='o')
#plt.title('d18O_fit')

ax[0].errorbar(x, diff_d18O_Pfit, err_diff_d18O_Pfit, linestyle='None', marker='o')
ax[0].set_title('$\delta^{18}O$', fontsize=16)
ax[0].set_ylabel(u'\u2030', fontsize=15)
ax[0].axhline(y=0, color='red', linewidth=0.5)

ax[1].errorbar(x, diff_d13C_fit, err_diff_d13C_fit, linestyle='None', marker='o')
ax[1].set_title('$\delta^{13}C$', fontsize=16)
ax[1].set_ylabel(u'\u2030', fontsize=15)
ax[1].axhline(y=0, color='red', linewidth=0.5)

#plt.figure(22)
#plt.plot(x, diff_CO2_corr, linestyle='None', marker='o')
#plt.title('CO2_corr')

ax[2].errorbar(x, diff_d17O_corr, err_diff_d17O_corr, linestyle='None', marker='o')
ax[2].set_title('$\delta^{17}O$', fontsize=16)
ax[2].set_ylabel(u'\u2030', fontsize=15)
ax[2].axhline(y=0, color='red', linewidth=0.5)

plt.setp(ax, xticks=[1, 2, 3, 4, 5, 6], xticklabels=['Bag 3', 'Bag 3', 'Bag 4', 'Bag 5', 'Bag 6', 'Bag 7'])


for item in (ax[2].get_yticklabels()):
    item.set_fontsize(13)
    
for item in (ax[1].get_yticklabels()):
    item.set_fontsize(13)
    
for item in (ax[0].get_yticklabels()):
    item.set_fontsize(13)
    
for item in (ax[2].get_xticklabels()):
    item.set_fontsize(15)

fig.suptitle('Change in isotopic composition per hour', fontsize=18)

#plt.figure(24)
#plt.plot(x, diff_D17O, linestyle='None', marker='o')
#plt.title('D17O')
idx=np.linspace(1,6,6)
dt=np.array([119.35,
   263.37          ,
   166.87          ,
   165.25          ,
   168.05          ,
   68.75])

all_data=np.array([ diff_b3m1,
 diff_b3m2 ,
 diff_b4m1 ,
 diff_b5m1 ,
 diff_b6m1 ,
 diff_b7m1])
sel_data=np.array([idx,dt,all_data[:,4],all_data[:,0],all_data[:,5]])
texfile = open(config.TabDir+'lisa_co2_iso_stor.tex' , 'w')
prec = np.array([0,2,2,2,2])
for row in sel_data.T:
        scantools.npa_to_tex_table(row, prec,texfile)
texfile.close()
#%% Verschil gecorrigeerd voor tijd
diff_b3m1_cor = diff_b3m1/119.35
err_diff_b3m1_cor = err_diff_b3m1/119.35

diff_b3m2_cor = diff_b3m2/263.37
err_diff_b3m2_cor = err_diff_b3m2/263.37

diff_b4_cor = diff_b4m1/166.87
err_diff_b4_cor = err_diff_b4m1/166.87

diff_b5_cor = diff_b5m1/165.25
err_diff_b5_cor = err_diff_b5m1/165.25

diff_b6_cor = diff_b6m1/168.05
err_diff_b6_cor = err_diff_b6m1/168.05

diff_b7_cor = diff_b7m1/68.75
err_diff_b7_cor = err_diff_b7m1/68.75

#diff_d18O_fit=np.array([diff_b3m1_cor[5], diff_b4_cor[5], diff_b5_cor[5], diff_b6_cor[5], diff_b7_cor[5]])

diff_d18O_Pfit=np.array([diff_b3m1_cor[5], diff_b3m2_cor[5], diff_b4_cor[5], diff_b5_cor[5], diff_b6_cor[5], diff_b7_cor[5]])
diff_d18O_fit=np.array([diff_b3m1_cor[6], diff_b3m2_cor[6], diff_b4_cor[6], diff_b5_cor[6], diff_b6_cor[6], diff_b7_cor[6]])

err_diff_d18O_Pfit=np.array([err_diff_b3m1_cor[1], err_diff_b3m2_cor[1], err_diff_b4_cor[1], err_diff_b5_cor[1], err_diff_b6_cor[1], err_diff_b7_cor[1]])

diff_d13C_fit=np.array([diff_b3m1_cor[4], diff_b3m2_cor[4], diff_b4_cor[4], diff_b5_cor[4], diff_b6_cor[4], diff_b7_cor[4]])
print("%.4f" %np.mean(diff_d13C_fit))
print("%.4f" %np.std(diff_d13C_fit))
print("%.4f" %np.mean(diff_d17O_corr))
print("%.4f" %np.std(diff_d17O_corr))
print("%.4f" %np.mean(diff_d18O_Pfit))
print("%.4f" %np.std(diff_d18O_Pfit))
# print("%.4f" %np.mean(diff_d18O_fit))
# print("%.4f" %np.std(diff_d18O_fit))
err_diff_d13C_fit=np.array([err_diff_b3m1_cor[0], err_diff_b3m2_cor[0], err_diff_b4_cor[0], err_diff_b5_cor[0], err_diff_b6_cor[0], err_diff_b7_cor[0]])

#diff_CO2_corr=np.array([diff_b3m1_cor[2], diff_b4_cor[2], diff_b5_cor[2], diff_b6_cor[2], diff_b7_cor[2]])

diff_d17O_corr=np.array([diff_b3m1_cor[0], diff_b3m2_cor[0], diff_b4_cor[0], diff_b5_cor[0], diff_b6_cor[0], diff_b7_cor[0]])
err_diff_d17O_corr=np.array([err_diff_b3m1_cor[2], err_diff_b3m2_cor[2], err_diff_b4_cor[2], err_diff_b5_cor[2], err_diff_b6_cor[2], err_diff_b7_cor[2]])

#diff_D17O=np.array([diff_b3m1_cor[0], diff_b4_cor[0], diff_b5_cor[0], diff_b6_cor[0], diff_b7_cor[0]])

x=np.array([1, 2, 3, 4, 5, 6])
fig, ax = plt.subplots (3,1, sharex=True)

#plt.figure(19)
#plt.plot(x, diff_d18O_fit,, linestyle='None', marker='o')
#plt.title('d18O_fit')

ax[0].errorbar(x, diff_d18O_Pfit, err_diff_d18O_Pfit, linestyle='None', marker='o', markersize=12)
ax[0].set_title('$\delta^{18}O$', fontsize=15)
ax[0].set_ylabel(u'\u2030', fontsize=15)
ax[0].axhline(y=0, color='red', linewidth=0.5)

ax[1].errorbar(x, diff_d13C_fit, err_diff_d13C_fit, linestyle='None', marker='o', markersize=12)
ax[1].set_title('$\delta^{13}C$', fontsize=15)
ax[1].set_ylabel(u'\u2030', fontsize=15)
ax[1].axhline(y=0, color='red', linewidth=0.5)

#plt.figure(22)
#plt.plot(x, diff_CO2_corr, linestyle='None', marker='o')
#plt.title('CO2_corr')

ax[2].errorbar(x, diff_d17O_corr, err_diff_d17O_corr, linestyle='None', marker='o', markersize=12)
ax[2].set_title('$\delta^{17}O$', fontsize=15)
ax[2].set_ylabel(u'\u2030', fontsize=15)
ax[2].axhline(y=0, color='red', linewidth=0.5)

plt.setp(ax, xticks=[1, 2, 3, 4, 5, 6], xticklabels=['Bag 3', 'Bag 3', 'Bag 4', 'Bag 5', 'Bag 6', 'Bag 7'])


for item in (ax[2].get_yticklabels()):
    item.set_fontsize(14)
    
for item in (ax[1].get_yticklabels()):
    item.set_fontsize(14)
    
for item in (ax[0].get_yticklabels()):
    item.set_fontsize(14)
    
for item in (ax[2].get_xticklabels()):
    item.set_fontsize(14)

# fig.suptitle('Change in isotopic ratio per hour', fontsize=18)

#plt.figure(24)
#plt.plot(x, diff_D17O, linestyle='None', marker='o')
#plt.title('D17O')
