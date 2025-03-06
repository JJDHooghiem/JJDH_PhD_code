#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Don't remove the line below, it is checked by "one to run them all"
# --otrta-p--
# extension p means parallel, s is for single
# -*- coding: utf-8 -*-

"""
Created on Wed Oct 24 08:47:38 2018

@author: meisu 
eddited by JJDHooghiem

"""
#%%
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
# from matplotlib.patches import Ellipse
import config 
import scantools
#%% 
DataDir=config.DataDir+'/2018_Long_term_storage/'
import Picarro
dataf=Picarro.get_Picarro(DataDir+'CFKBDS2102-20181023-073305Z-DataLog_User.dat',configfile=DataDir+'pic_config.ini')
datag=Picarro.get_Picarro(DataDir+'CFKBDS2102-20181023-112242Z-DataLog_User.dat',configfile=DataDir+'pic_config.ini')
datah=Picarro.get_Picarro(DataDir+'CFKBDS2102-20181024-064225Z-DataLog_User.dat',configfile=DataDir+'pic_config.ini')
datai=Picarro.get_Picarro(DataDir+'CFKBDS2102-20181024-092403Z-DataLog_User.dat',configfile=DataDir+'pic_config.ini')
dataj=Picarro.get_Picarro(DataDir+'CFKBDS2102-20181026-070131Z-DataLog_User.dat',configfile=DataDir+'pic_config.ini')
datak=Picarro.get_Picarro(DataDir+'CFKBDS2102-20181029-094758Z-DataLog_User.dat',configfile=DataDir+'pic_config.ini')
datal=Picarro.get_Picarro(DataDir+'CFKBDS2102-20181029-130628Z-DataLog_User.dat',configfile=DataDir+'pic_config.ini')



# ex2_b11m_all = np.array(Picarro.intervalmean(5500,6000,dataf))
# ex2_b12m_all = np.array(Picarro.intervalmean(23300,23750,dataf))
# ex2_b31m_all = np.array(Picarro.intervalmean(6500,7300,datag))

ex2_b13m_all = np.array(Picarro.intervalmean(18800,19000,datag))
ex2_b14m_all = np.array(Picarro.intervalmean(13700,13900,datah))

# ex2_b15m_all = np.array(Picarro.intervalmean(2500,2970,dataj))
ex2_b15m_all = np.array(Picarro.intervalmean(2650,2850,dataj))
ex2_b16m_all = np.array(Picarro.intervalmean(2950,3150,datak))

# ex2_b32m_all = np.array(Picarro.intervalmean(14500,15500,datag))
ex2_b32m_all = np.array(Picarro.intervalmean(15000,15200,datag))
ex2_b33m_all = np.array(Picarro.intervalmean(10300,10500,datah))

ex2_b34m_all = np.array(Picarro.intervalmean(5900,6100,dataj))
ex2_b35m_all = np.array(Picarro.intervalmean(6400,6600,datak))

# ex2_b41m_all = np.array(Picarro.intervalmean(10400,10800,datag))
# ex2_b42m_all = np.array(Picarro.intervalmean(16000,16600,datah))

# ex2_b43m_all = np.array(Picarro.intervalmean(9350,9800,dataj))
ex2_b43m_all = np.array(Picarro.intervalmean(9500,9700,dataj))
ex2_b44m_all = np.array(Picarro.intervalmean(10300,10500,datak))

# ex2_b11m_t = np.nanmean(dataf["JULIAN_DAYS"][5500  : 6000  ] )
# ex2_b12m_t = np.nanmean(dataf["JULIAN_DAYS"][23300 : 23750 ] )
# ex2_b31m_t = np.nanmean(datag["JULIAN_DAYS"][6500  : 7300  ] )


# print(24*60*(datag["JULIAN_DAYS"][18800]-datag["JULIAN_DAYS"][19000 ]))
ex2_b13m_t = np.nanmean(datag["JULIAN_DAYS"][18800 : 19000 ] ) 
ex2_b14m_t = np.nanmean(datah["JULIAN_DAYS"][13700: 13900] )

ex2_b15m_t = np.nanmean(dataj["JULIAN_DAYS"][2650  : 2850  ] )
ex2_b16m_t = np.nanmean(datak["JULIAN_DAYS"][2950  : 3150  ] )

ex2_b32m_t = np.nanmean(datag["JULIAN_DAYS"][15000 : 15200 ] )
ex2_b33m_t = np.nanmean(datah["JULIAN_DAYS"][10300 : 10500 ] )

ex2_b34m_t = np.nanmean(dataj["JULIAN_DAYS"][5900  : 6100  ] )
ex2_b35m_t = np.nanmean(datak["JULIAN_DAYS"][6400  : 6600  ] )

# ex2_b41m_t = np.nanmean(datag["JULIAN_DAYS"][10400 : 10900 ] )
# ex2_b42m_t = np.nanmean(datah["JULIAN_DAYS"][16000 : 16700 ] )

ex2_b43m_t = np.nanmean(dataj["JULIAN_DAYS"][9500   : 9700 ] )
ex2_b44m_t = np.nanmean(datak["JULIAN_DAYS"][10300  : 10500] )

# all_data =np.array([ ex2_b13m_all,ex2_b14m_all,ex2_b15m_all,ex2_b16m_all,ex2_b32m_all,ex2_b33m_all,ex2_b34m_all,ex2_b35m_all,ex2_b41m_all,ex2_b42m_all,ex2_b43m_all,ex2_b44m_all ])
all_data =np.array([ ex2_b13m_all,ex2_b14m_all,ex2_b15m_all,ex2_b16m_all,ex2_b32m_all,ex2_b33m_all,ex2_b34m_all,ex2_b35m_all,ex2_b43m_all,ex2_b44m_all ])

# According to Meis her work the experiments were executed as follows, bag filled, then measured. After a storage period,
# measured agian. Then refilled for the long storage period. So each bag has its on zero reference point for each storage 
# period. Short term and long term periods are thus not comparable



# t=np.array([ex2_b13m_t,ex2_b14m_t,ex2_b15m_t,ex2_b16m_t,ex2_b32m_t,ex2_b33m_t,ex2_b34m_t,ex2_b35m_t,ex2_b41m_t,ex2_b42m_t,ex2_b43m_t,ex2_b44m_t])
t=np.array([ex2_b13m_t,ex2_b14m_t,ex2_b15m_t,ex2_b16m_t,ex2_b32m_t,ex2_b33m_t,ex2_b34m_t,ex2_b35m_t,ex2_b43m_t,ex2_b44m_t])
# in hours
dt=np.array([24*(t[i*2+1]-t[2*i]) for i in range(0,int(len(t)/2))])
# print(all_data)
ex2_c21m_all = np.array(Picarro.intervalmean(22400,22600,datag))
ex2_c22m_all = np.array(Picarro.intervalmean(7300,7500,datah))
ex2_c23m_all = np.array(Picarro.intervalmean(4600,4800,datal))

# ex2_c21m_all = datag[20000:24000].resample("30S").mean()
# print(len(ex2_c21m_all ))
# print(np.std(ex2_c21m_all['CO2_cor'] ))
# print(np.std(ex2_c21m_all['CH4_cor'] ))
# print(np.std(ex2_c21m_all['CO_cor'] ))
# ex2_c22m_all = np.array(Picarro.intervalmean(7300,7500,datah))
# ex2_c23m_all = np.array(Picarro.intervalmean(4600,4800,datal))

# f,t,m=Picarro.meanplot([4500],[5000],datal,filename='meisu',whole=True)
# f.savefig('meanplotje.pdf')
cyl_co2_m=np.array([ex2_c21m_all[0],ex2_c22m_all[0],ex2_c23m_all[0]])
cyl_co2_s=np.array([ex2_c21m_all[1],ex2_c22m_all[1],ex2_c23m_all[1]])
cyl_ch4_m=np.array([ex2_c21m_all[2],ex2_c22m_all[2],ex2_c23m_all[2]])
cyl_ch4_s=np.array([ex2_c21m_all[3],ex2_c22m_all[3],ex2_c23m_all[3]])
cyl_co_m =np.array([ex2_c21m_all[4],ex2_c22m_all[4],ex2_c23m_all[4]])
cyl_co_s =np.array([ex2_c21m_all[5],ex2_c22m_all[5],ex2_c23m_all[5]])
cyl_h2o_m=np.array([ex2_c21m_all[6],ex2_c22m_all[6],ex2_c23m_all[6]])
cyl_h2o_s=np.array([ex2_c21m_all[7],ex2_c22m_all[7],ex2_c23m_all[7]])

# print(cyl_co2_m)
# print(cyl_co2_s)
# print(cyl_ch4_m)
# print(cyl_ch4_s)
# print(cyl_co_m )
# print(cyl_co_s )
# print(cyl_h2o_m)
# print(cyl_h2o_s)

print(np.mean(cyl_co2_m))
print(np.std(cyl_co2_m))
print(np.mean(cyl_ch4_m))
print(np.std(cyl_ch4_m))
print(np.mean(cyl_co_m ))
print(np.std(cyl_co_m ))


# cyl_co2_s=np.array([ex2_c22m_all[1],ex2_c23m_all[1]])
# cyl_ch4_m=np.array([ex2_c22m_all[2],ex2_c23m_all[2]])
# cyl_ch4_s=np.array([ex2_c22m_all[3],ex2_c23m_all[3]])
# cyl_co_m =np.array([ex2_c22m_all[4],ex2_c23m_all[4]])
# cyl_co_s =np.array([ex2_c22m_all[5],ex2_c23m_all[5]])
# cyl_h2o_m=np.array([ex2_c22m_all[6],ex2_c23m_all[6]])
# cyl_h2o_s=np.array([ex2_c22m_all[7],ex2_c23m_all[7]])

ex2_c21m_t = np.nanmean(datag["JULIAN_DAYS"][22400 : 22600 ] )
ex2_c22m_t = np.nanmean(datah["JULIAN_DAYS"][7300  : 7500  ] )
ex2_c23m_t = np.nanmean(datal["JULIAN_DAYS"][4600  : 4800  ] )

cyl_t=np.array([ ex2_c21m_t,ex2_c22m_t,ex2_c23m_t])
# cyl_t=np.array([ ex2_c21m_t,ex2_c23m_t])

drift_co2=interp1d(cyl_t,cyl_co2_m-cyl_co2_m[0],fill_value='extrapolate')(t)
drift_ch4=interp1d(cyl_t,cyl_ch4_m-cyl_ch4_m[0],fill_value='extrapolate')(t)
drift_co =interp1d(cyl_t,cyl_co_m -cyl_co_m[0] ,fill_value='extrapolate')(t)

all_data[:,0]=all_data[:,0]-drift_co2
all_data[:,2]=all_data[:,2]-drift_ch4
all_data[:,4]=all_data[:,4]-drift_co
# visually check the drifts 

# print(all_data[:,1])
# print(all_data[:,3])
# print(all_data[:,5])
# print(all_data[:,7])

xlims=[(295,305)]*3
ylims=[(-0.1,0.1),(-0.1,0.1),(-2.5,2.5)]

xlabs = [config.axl['tho']]*3

ylabs = [config.axl['dco2'],config.axl['dch4'],config.axl['dco']]

fig,axes=scantools.plot_init(1,3,xlabs=xlabs,ylabs=ylabs,xlims=xlims,ylims=ylims)
print(len(axes))
scantools.plot_add(axes[0] ,cyl_t , cyl_co2_m-cyl_co2_m[0] ,  color=config.GruvBoxColors[0]  , label='Tank difference')
scantools.plot_add(axes[1] ,cyl_t , cyl_ch4_m-cyl_ch4_m[0] ,  color=config.GruvBoxColors[0])
scantools.plot_add(axes[2] ,cyl_t , cyl_co_m-cyl_co_m[0]   ,  color=config.GruvBoxColors[0])
scantools.plot_add(axes[0] ,t , drift_co2              ,  color=config.GruvBoxColors[1]  , label='correction')
scantools.plot_add(axes[1] ,t , drift_ch4              ,  color=config.GruvBoxColors[1])
scantools.plot_add(axes[2] ,t , drift_co               ,  color=config.GruvBoxColors[1])
axes[0].legend()
fig.tight_layout()
fig.savefig(config.FigDir+'lisasd_lts_instr_drift.pdf')

print("%.2f" % (np.mean(all_data[:,4] ))  )
print("%.2f" % (np.std(all_data[:,4] ))  )
a=np.array([all_data[2*i+1] for i in range(0,int(len(t)/2))])
b=np.array([all_data[2*i] for i in range(0,int(len(t)/2))])

from scipy.stats import mannwhitneyu
from scipy.stats import ttest_ind
stat, p = ttest_ind(a[:,4], b[:,4])
print('stat=%.3f, p=%.3f' % (stat, p))
if p > 0.05:
	print('Probably the same distribution')
else:
	print('Probably different distributions')
print("%.2f" % (np.mean(a[:,4] ))  )
print("%.2f" % (np.std(a[:,4] ))  )
print("%.2f" % (np.mean(b[:,4] ))  )
print("%.2f" % (np.std(b[:,4] ))  )

all_data_dif=np.array([all_data[2*i+1]-all_data[2*i] for i in range(0,int(len(t)/2))])
# all_data_rat=all_data[2*i+1]-all_data[2*i]

print("%.2f" % (np.mean(all_data_dif[:,0])))
print("%.2f" % (np.std(all_data_dif[:,0])))
print("%.2f" % (np.mean(all_data_dif[:,2])))
print("%.2f" % (np.std(all_data_dif[:,2])))
print("%.2f" % (np.mean(all_data_dif[:,4])))
print("%.2f" % (np.std(all_data_dif[:,4])))
print("%.2f" % (np.mean(all_data_dif[:,6])))
print("%.2f" % (np.std(all_data_dif[:,6])))

print("%.2f" % (np.mean(all_data_dif[:,0]/dt )*1000)  )
print("%.2f" % (np.std(all_data_dif[:,0]/dt  )*1000)  )
print("%.2f" % (np.mean(all_data_dif[:,2]/dt )*1000)  )
print("%.2f" % (np.std(all_data_dif[:,2]/dt  )*1000)  )
print("%.2f" % (np.mean(all_data_dif[:,4]/dt )*1000)  )
print("%.2f" % (np.std(all_data_dif[:,4]/dt  )*1000)  )
print("%.2f" % (np.mean(all_data_dif[:,6]/dt )*10000)  )
print("%.2f" % (np.std(all_data_dif[:,6]/dt  )*10000)  )

all_data_dev=np.array([all_data[2*i+1]-all_data[2*i] for i in range(0,int(len(t)/2))])

xlabs = [config.axl['tho']]
ylabs = [config.axl['mfr']]
print(dt)
xlims=[(0,80)]
ylims=[(0,0.7)]
fig,axes=scantools.plot_init(1,1,xlabs=xlabs,ylabs=ylabs,xlims=xlims,ylims=ylims)

scantools.plot_add(axes,dt,all_data_dev[:,0],color=config.GruvBoxColors[0],label=r'$\textrm{X}=\textrm{CO}_{2}$ ({\textmugreek}mol~mol$^{-1}$)',marker=config.Markers[0],linestyle='')
scantools.plot_add(axes,dt,all_data_dev[:,2],color=config.GruvBoxColors[1],label=r'$\textrm{X}=\textrm{CH}_{4}$ (nmol~mol$^{-1}$)',marker=config.Markers[1],linestyle='')
# scantools.plot_add(axes,dt,all_data_dev[:,4],color=config.GruvBoxColors[2],label=r'$\textrm{X}=\textrm{CO}$',marker=config.Markers[2],linestyle='')
scantools.plot_add(axes,dt,all_data_dev[:,6],color=config.GruvBoxColors[3],label=r'$\textrm{X}=\textrm{H}_{2}\textrm{O}$ (cmol~mol$^{-1}$)',marker=config.Markers[3],linestyle='')
t=np.array([1,79])
co2_stats=scantools.regression(dt,all_data_dev[:,0],intercept=False)
ch4_stats=scantools.regression(dt,all_data_dev[:,2],intercept=False)
# co_stats=scantools.regression(dt,all_data_dev[:,4]-1,intercept=False)
h2o_stats=scantools.regression(dt,all_data_dev[:,6],intercept=False)
print(all_data_dev[:,6])
scantools.plot_add(axes,t,t*co2_stats[0],color=config.GruvBoxColors[0],label='fit $p=%.3f$' % co2_stats[-1],linestyle='-')
scantools.plot_add(axes,t,t*ch4_stats[0],color=config.GruvBoxColors[1],label='fit $p=%.3f$' % ch4_stats[-1],linestyle='-')
# scantools.plot_add(axes,t,t*co_stats[0]+1,color=config.GruvBoxColors[2],label='fit $p=%.3f$' % co_stats[-1] ,linestyle='-')
scantools.plot_add(axes,t,t*h2o_stats[0],color=config.GruvBoxColors[3],label='fit $p=%.3f$' % h2o_stats[-1] ,linestyle='-')


# scantools.statplot(axes,dt,all_data_dev[:,0])
# scantools.statplot(axes,dt,all_data_dev[:,2])
# scantools.statplot(axes,dt,all_data_dev[:,4])
axes.legend()
fig.tight_layout()
fig.savefig(config.FigDir+'lisasd_lts_rel_drift.pdf')
exit()



#%% CO2
# Results first day (23-10-2018)
# ex2 means experiment2  bx is bag x x=[1,2,3,4 ..]
ex2_b11m1 = np.nanmean(dataf['CO2_cor'][5500:6000])
ex2_b11s1 = np.nanstd(dataf['CO2_cor'][5500:6000])

ex2_b12m1 = np.nanmean(dataf['CO2_cor'][23300:23750])
ex2_b12s1 = np.nanstd(dataf['CO2_cor'][23300:23750])

ex2_b31m1 = np.nanmean(datag['CO2_cor'][6500:7300])
ex2_b31s1 = np.nanstd(datag['CO2_cor'][6500:7300])

ex2_b41m1 = np.nanmean(datag['CO2_cor'][10400:10900])
ex2_b41s1 = np.nanstd(datag['CO2_cor'][10400:10900])

ex2_b32m1 = np.nanmean(datag['CO2_cor'][14500:15500])
ex2_b32s1 = np.nanstd(datag['CO2_cor'][14500:15500])

ex2_b13m1 = np.nanmean(datag['CO2_cor'][18300:19000])
ex2_b13s1 = np.nanstd(datag['CO2_cor'][18300:19000])

ex2_c21m1 = np.nanmean(datag['CO2_cor'][21500:22600])
ex2_c21s1 = np.nanstd(datag['CO2_cor'][21500:22600])

# Results second day(24-10-2018)

ex2_c22m1 = np.nanmean(datah['CO2_cor'][6500:7500])
ex2_c22s1 = np.nanstd(datah['CO2_cor'][6500:7500])

ex2_b33m1 = np.nanmean(datah['CO2_cor'][10000:10500])
ex2_b33s1 = np.nanstd(datah['CO2_cor'][10000:10500])

ex2_b14m1 = np.nanmean(datah['CO2_cor'][13300:14000])
ex2_b14s1 = np.nanstd(datah['CO2_cor'][13300:14000])

ex2_b42m1 = np.nanmean(datah['CO2_cor'][16000:16700])
ex2_b42s1 = np.nanstd(datah['CO2_cor'][16000:16700])

# Results third day(26-10-2018)

ex2_b15m1 = np.nanmean(dataj['CO2_cor'][2500:2970])
ex2_b15s1 = np.nanstd(dataj['CO2_cor'][2500:2970])

ex2_b34m1 = np.nanmean(dataj['CO2_cor'][5700:6200])
ex2_b34s1 = np.nanstd(dataj['CO2_cor'][5700:6200])

ex2_b43m1 = np.nanmean(dataj['CO2_cor'][9350:9800])
ex2_b43s1 = np.nanstd(dataj['CO2_cor'][9350:9800])

# Results fourth day (29-10-2018)

ex2_b16m1 = np.nanmean(datak['CO2_cor'][2500:3200])
ex2_b16s1 = np.nanstd(datak['CO2_cor'][2500:3200])

ex2_b35m1 = np.nanmean(datak['CO2_cor'][6000:6600])
ex2_b35s1 = np.nanstd(datak['CO2_cor'][6000:6600])

ex2_b44m1 = np.nanmean(datak['CO2_cor'][9800:10500])
ex2_b44s1 = np.nanstd(datak['CO2_cor'][9800:10500])

ex2_c23m1 = np.nanmean(datal['CO2_cor'][4500:5400])
ex2_c23s1 = np.nanstd(datal['CO2_cor'][4500:5400])

# import matplotlib
# matplotlib.use('Qt5Agg')
# matplotlib.rc('text', usetex=False)
# x=np.array([ex2_c21m_t, ex2_c22m_t, ex2_c23m_t])-ex2_c21m_t
# y=np.array([ex2_c21m1, ex2_c22m1, ex2_c23m1])-ex2_c21m1
# plt.plot(x,y)
# plt.show()

#%% CH4

ex2_b11m2 = np.nanmean(dataf['CH4_cor'][5600:6000])
ex2_b11s2 = np.nanstd(dataf['CH4_cor'][5600:6000])

ex2_b12m2 = np.nanmean(dataf['CH4_cor'][23300:23750])
ex2_b12s2 = np.nanstd(dataf['CH4_cor'][23300:23750])

ex2_b31m2 = np.nanmean(datag['CH4_cor'][6500:7300])
ex2_b31s2 = np.nanstd(datag['CH4_cor'][6500:7300])

ex2_b41m2 = np.nanmean(datag['CH4_cor'][10400:10775])
ex2_b41s2 = np.nanstd(datag['CH4_cor'][10400:10775])

ex2_b32m2 = np.nanmean(datag['CH4_cor'][14500:15200])
ex2_b32s2 = np.nanstd(datag['CH4_cor'][14500:15200])

ex2_b13m2 = np.nanmean(datag['CH4_cor'][18300:19000])
ex2_b13s2 = np.nanstd(datag['CH4_cor'][18300:19000])

ex2_c21m2 = np.nanmean(datag['CH4_cor'][21500:22600])
ex2_c21s2 = np.nanstd(datag['CH4_cor'][21500:22600])

# Results second day(24-10-2018)

ex2_c22m2 = np.nanmean(datah['CH4_cor'][6500:7500])
ex2_c22s2 = np.nanstd(datah['CH4_cor'][6500:7500])

ex2_b33m2 = np.nanmean(datah['CH4_cor'][10000:10500])
ex2_b33s2 = np.nanstd(datah['CH4_cor'][10000:10500])

ex2_b14m2 = np.nanmean(datah['CH4_cor'][13300:14000])
ex2_b14s2 = np.nanstd(datah['CH4_cor'][13300:14000])

ex2_b42m2 = np.nanmean(datah['CH4_cor'][16000:16700])
ex2_b42s2 = np.nanstd(datah['CH4_cor'][16000:16700])

# Results third day(26-10-2018)

ex2_b15m2 = np.nanmean(dataj['CH4_cor'][2300:2900])
ex2_b15s2 = np.nanstd(dataj['CH4_cor'][2300:2900])

ex2_b34m2 = np.nanmean(dataj['CH4_cor'][5600:6150])
ex2_b34s2 = np.nanstd(dataj['CH4_cor'][5600:6150])

ex2_b43m2 = np.nanmean(dataj['CH4_cor'][9200:9780])
ex2_b43s2 = np.nanstd(dataj['CH4_cor'][9200:9780])

# Results fourth day (29-10-2018)

ex2_b16m2 = np.nanmean(datak['CH4_cor'][2500:3200])
ex2_b16s2 = np.nanstd(datak['CH4_cor'][2500:3200])

ex2_b35m2 = np.nanmean(datak['CH4_cor'][6000:6600])
ex2_b35s2 = np.nanstd(datak['CH4_cor'][6000:6600])

ex2_b44m2 = np.nanmean(datak['CH4_cor'][9800:10500])
ex2_b44s2 = np.nanstd(datak['CH4_cor'][9800:10500])

ex2_c23m2 = np.nanmean(datal['CH4_cor'][4500:5400])
ex2_c23s2 = np.nanstd(datal['CH4_cor'][4500:5400])
#%% CO

ex2_b11m3 = np.nanmean(dataf['CO_cor'][5500:6000])
ex2_b11s3 = np.nanstd(dataf['CO_cor'][5500:6000])

ex2_b12m3 = np.nanmean(dataf['CO_cor'][23300:23750])
ex2_b12s3 = np.nanstd(dataf['CO_cor'][23300:23750])

ex2_b31m3 = np.nanmean(datag['CO_cor'][6500:7300])
ex2_b31s3 = np.nanstd(datag['CO_cor'][6500:7300])

ex2_b41m3 = np.nanmean(datag['CO_cor'][10400:10900])
ex2_b41s3 = np.nanstd(datag['CO_cor'][10400:10900])

ex2_b32m3 = np.nanmean(datag['CO_cor'][14500:15500])
ex2_b32s3 = np.nanstd(datag['CO_cor'][14500:15500])

ex2_b13m3 = np.nanmean(datag['CO_cor'][18300:19000])
ex2_b13s3 = np.nanstd(datag['CO_cor'][18300:19000])

ex2_c21m3 = np.nanmean(datag['CO_cor'][21500:22600])
ex2_c21s3 = np.nanstd(datag['CO_cor'][21500:22600])

# Results second day(24-10-2018)

ex2_c22m3 = np.nanmean(datah['CO_cor'][6500:7500])
ex2_c22s3 = np.nanstd(datah['CO_cor'][6500:7500])

ex2_b33m3 = np.nanmean(datah['CO_cor'][10000:10500])
ex2_b33s3 = np.nanstd(datah['CO_cor'][10000:10500])

ex2_b14m3 = np.nanmean(datah['CO_cor'][13300:14000])
ex2_b14s3 = np.nanstd(datah['CO_cor'][13300:14000])

ex2_b42m3 = np.nanmean(datah['CO_cor'][16000:16700])
ex2_b42s3 = np.nanstd(datah['CO_cor'][16000:16700])

# Results third day(26-10-2018)

ex2_b15m3 = np.nanmean(dataj['CO_cor'][2300:2900])
ex2_b15s3 = np.nanstd(dataj['CO_cor'][2300:2900])

ex2_b34m3 = np.nanmean(dataj['CO_cor'][5600:6150])
ex2_b34s3 = np.nanstd(dataj['CO_cor'][5600:6150])

ex2_b43m3 = np.nanmean(dataj['CO_cor'][9200:9780])
ex2_b43s3 = np.nanstd(dataj['CO_cor'][9200:9780])

# Results fourth day (29-10-2018)

ex2_b16m3 = np.nanmean(datak['CO_cor'][2500:3200])
ex2_b16s3 = np.nanstd(datak['CO_cor'][2500:3200])

ex2_b35m3 = np.nanmean(datak['CO_cor'][6000:6600])
ex2_b35s3 = np.nanstd(datak['CO_cor'][6000:6600])

ex2_b44m3 = np.nanmean(datak['CO_cor'][9800:10500])
ex2_b44s3 = np.nanstd(datak['CO_cor'][9800:10500])

ex2_c23m3 = np.nanmean(datal['CO_cor'][4500:5400])
ex2_c23s3 = np.nanstd(datal['CO_cor'][4500:5400])

#%% H2O

ex2_b11m4 = np.nanmean(dataf['H2O'][5500:6000])
ex2_b11s4 = np.nanstd(dataf['H2O'][5500:6000])

ex2_b12m4 = np.nanmean(dataf['H2O'][23300:23750])
ex2_b12s4 = np.nanstd(dataf['H2O'][23300:23750])

ex2_b31m4 = np.nanmean(datag['H2O'][6500:7300])
ex2_b31s4 = np.nanstd(datag['H2O'][6500:7300])

ex2_b41m4 = np.nanmean(datag['H2O'][10400:10900])
ex2_b41s4 = np.nanstd(datag['H2O'][10400:10900])

ex2_b32m4 = np.nanmean(datag['H2O'][14500:15500])
ex2_b32s4 = np.nanstd(datag['H2O'][14500:15500])

ex2_b13m4 = np.nanmean(datag['H2O'][18300:19000])
ex2_b13s4 = np.nanstd(datag['H2O'][18300:19000])

ex2_c21m4 = np.nanmean(datag['H2O'][21500:22600])
ex2_c21s4 = np.nanstd(datag['H2O'][21500:22600])

# Results second day(24-10-2018)

ex2_c22m4 = np.nanmean(datah['H2O'][6500:7500])
ex2_c22s4 = np.nanstd(datah['H2O'][6500:7500])

ex2_b33m4 = np.nanmean(datah['H2O'][10000:10500])
ex2_b33s4 = np.nanstd(datah['H2O'][10000:10500])

ex2_b14m4 = np.nanmean(datah['H2O'][13300:14000])
ex2_b14s4 = np.nanstd(datah['H2O'][13300:14000])

ex2_b42m4 = np.nanmean(datah['H2O'][16000:16700])
ex2_b42s4 = np.nanstd(datah['H2O'][16000:16700])

# Results third day(26-10-2018)

ex2_b15m4 = np.nanmean(dataj['H2O'][2300:2900])
ex2_b15s4 = np.nanstd(dataj['H2O'][2300:2900])

ex2_b34m4 = np.nanmean(dataj['H2O'][5600:6150])
ex2_b34s4 = np.nanstd(dataj['H2O'][5600:6150])

ex2_b43m4 = np.nanmean(dataj['H2O'][9200:9700])
ex2_b43s4 = np.nanstd(dataj['H2O'][9200:9700])

# Results fourth day (29-10-2018)

ex2_b16m4 = np.nanmean(datak['H2O'][2500:3150])
ex2_b16s4 = np.nanstd(datak['H2O'][2500:3150])

ex2_b35m4 = np.nanmean(datak['H2O'][6000:6600])
ex2_b35s4 = np.nanstd(datak['H2O'][6000:6600])

ex2_b44m4 = np.nanmean(datak['H2O'][9800:10500])
ex2_b44s4 = np.nanstd(datak['H2O'][9800:10500])

ex2_c23m4 = np.nanmean(datal['H2O'][4500:5400])
ex2_c23s4 = np.nanstd(datal['H2O'][4500:5400])
#%% Plot CO2
x = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])

y1_1 = np.array([ex2_b11m1, ex2_b12m1, ex2_b13m1, ex2_b14m1, ex2_b15m1, ex2_b16m1])
#y2_1 = np.array([ex2_b21m1])
y3_1 = np.array([ex2_b31m1, ex2_b32m1, ex2_b33m1, ex2_b34m1, ex2_b35m1])
y4_1 = np.array([ex2_b41m1, ex2_b42m1, ex2_b43m1, ex2_b44m1])

e1_1 = np.array([ex2_b11s1, ex2_b12s1, ex2_b13s1, ex2_b14s1, ex2_b15s1, ex2_b16s1])
#e2_1 = np.array([ex2_b21s1])
e3_1 = np.array([ex2_b31s1, ex2_b32s1, ex2_b33s1, ex2_b34s1, ex2_b35s1])
e4_1 = np.array([ex2_b41s1, ex2_b42s1, ex2_b43s1, ex2_b44s1])

fig, ax = plt.subplots(1,1)
ax.errorbar(x[0:6], y1_1, e1_1, linestyle='None', marker='o', label='Bag 1')
#plt.errorbar(x[3], y2_1, e2_1, linestyle='None', marker='o')
ax.errorbar(x[6:11], y3_1, e3_1, linestyle='None', marker='o', label='Bag 3')
ax.errorbar(x[11:15], y4_1, e4_1, linestyle='None', marker='o', label='Bag 4')
plt.axhline(y=ex2_c21m1, color='black', label='Cylinder')
plt.axhline(y=ex2_c22m1, color='purple', label='Cylinder')
plt.axhline(y=ex2_c23m1, color='red', label='Cylinder')
plt.legend()
plt.title('Measured values of CO2')
plt.ylabel('ppm')
plt.xticks([])

el1 = Ellipse((x[2],y1_1[2]), 1, 0.07, color='red', alpha=1, fill=None)
el2 = Ellipse((x[3],y1_1[3]), 1, 0.07, color='red', alpha=1, fill=None)
el3 = Ellipse((x[7],y3_1[1]), 1, 0.07, color='red', alpha=1, fill=None)
el4 = Ellipse((x[8],y3_1[2]), 1, 0.07, color='red', alpha=1, fill=None)
el5 = Ellipse((x[11],y4_1[0]), 1, 0.07, color='red', alpha=1, fill=None)
el6 = Ellipse((x[12],y4_1[1]), 1, 0.07, color='red', alpha=1, fill=None)

el7 = Ellipse((x[4],y1_1[4]), 1, 0.07, color='black', alpha=1, fill=None)
el8 = Ellipse((x[5],y1_1[5]), 1, 0.07, color='black', alpha=1, fill=None)
el9 = Ellipse((x[9],y3_1[3]), 1, 0.07, color='black', alpha=1, fill=None)
el10 = Ellipse((x[10],y3_1[4]), 1, 0.07, color='black', alpha=1, fill=None)
el11 = Ellipse((x[13],y4_1[2]), 1, 0.07, color='black', alpha=1, fill=None)
el12 = Ellipse((x[14],y4_1[3]), 1, 0.07, color='black', alpha=1, fill=None)

ax.add_artist(el1)
ax.add_artist(el2)
ax.add_artist(el3)
ax.add_artist(el4)
ax.add_artist(el5)
ax.add_artist(el6)
ax.add_artist(el7)
ax.add_artist(el8)
ax.add_artist(el9)
ax.add_artist(el10)
ax.add_artist(el11)
ax.add_artist(el12)
#%% Plot CH4

x = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10 ,11, 12, 13, 14, 15])

y1_2 = np.array([ex2_b11m2, ex2_b12m2, ex2_b13m2, ex2_b14m2, ex2_b15m2, ex2_b16m2])
#y2_2 = np.array([ex2_b21m2])
y3_2 = np.array([ex2_b31m2, ex2_b32m2, ex2_b33m2, ex2_b34m2, ex2_b35m2])
y4_2 = np.array([ex2_b41m2, ex2_b42m2, ex2_b43m2, ex2_b44m2])

e1_2 = np.array([ex2_b11s2, ex2_b12s2, ex2_b13s2, ex2_b14s2, ex2_b15s2, ex2_b16s2])
#e2_2 = np.array([ex2_b21s2])
e3_2 = np.array([ex2_b31s2, ex2_b32s2, ex2_b33s2, ex2_b34s2, ex2_b35s2])
e4_2 = np.array([ex2_b41s2, ex2_b42s2, ex2_b43s2, ex2_b44s2])

fig, ax = plt.subplots(1,1)
plt.errorbar(x[0:6], y1_2, e1_2, linestyle='None', marker='o', label='Bag 1')
#plt.errorbar(x[3], y2_2, e2_2, linestyle='None', marker='o')
plt.errorbar(x[6:11], y3_2, e3_2, linestyle='None', marker='o', label='Bag 2')
plt.errorbar(x[11:15], y4_2, e4_2, linestyle='None', marker='o', label='Bag 3')
plt.axhline(y=ex2_c21m2, color='black')
plt.axhline(y=ex2_c22m2, color='purple')
plt.axhline(y=ex2_c23m2, color='red')
plt.legend()
plt.title('Measured values of CH4')
plt.ylabel('ppb')
plt.xticks([])

el1 = Ellipse((x[2],y1_2[2]), 1, 0.3, color='red', alpha=1, fill=None)
el2 = Ellipse((x[3],y1_2[3]), 1, 0.3, color='red', alpha=1, fill=None)
el3 = Ellipse((x[7],y3_2[1]), 1, 0.3, color='red', alpha=1, fill=None)
el4 = Ellipse((x[8],y3_2[2]), 1, 0.3, color='red', alpha=1, fill=None)
el5 = Ellipse((x[11],y4_2[0]), 1, 0.3, color='red', alpha=1, fill=None)
el6 = Ellipse((x[12],y4_2[1]), 1, 0.3, color='red', alpha=1, fill=None)

el7 = Ellipse((x[4],y1_2[4]), 1, 0.3, color='black', alpha=1, fill=None)
el8 = Ellipse((x[5],y1_2[5]), 1, 0.3, color='black', alpha=1, fill=None)
el9 = Ellipse((x[9],y3_2[3]), 1, 0.3, color='black', alpha=1, fill=None)
el10 = Ellipse((x[10],y3_2[4]), 1, 0.3, color='black', alpha=1, fill=None)
el11 = Ellipse((x[13],y4_2[2]), 1, 0.3, color='black', alpha=1, fill=None)
el12 = Ellipse((x[14],y4_2[3]), 1, 0.3, color='black', alpha=1, fill=None)

ax.add_artist(el1)
ax.add_artist(el2)
ax.add_artist(el3)
ax.add_artist(el4)
ax.add_artist(el5)
ax.add_artist(el6)
ax.add_artist(el7)
ax.add_artist(el8)
ax.add_artist(el9)
ax.add_artist(el10)
ax.add_artist(el11)
ax.add_artist(el12)
#%% Plot CO

x = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9 ,10, 11, 12, 13, 14, 15])

y1_3 = np.array([ex2_b11m3, ex2_b12m3, ex2_b13m3, ex2_b14m3, ex2_b15m3, ex2_b16m3])
#y2_2 = np.array([ex2_b21m2])
y3_3 = np.array([ex2_b31m3, ex2_b32m3, ex2_b33m3, ex2_b34m3, ex2_b35m3])
y4_3 = np.array([ex2_b41m3, ex2_b42m3, ex2_b43m3, ex2_b44m3])

e1_3 = np.array([ex2_b11s3, ex2_b12s3, ex2_b13s3, ex2_b14s3, ex2_b15s3, ex2_b16s3])
#e2_2 = np.array([ex2_b21s2])
e3_3 = np.array([ex2_b31s3, ex2_b32s3, ex2_b33s3, ex2_b34s3, ex2_b35s3])
e4_3 = np.array([ex2_b41s3, ex2_b42s3, ex2_b43s3, ex2_b44s3])

fig, ax = plt.subplots(1,1)
plt.errorbar(x[0:6], y1_3, e1_3, linestyle='None', marker='o', label='Bag 1')
#plt.errorbar(x[3], y2_2, e2_2, linestyle='None', marker='o')
plt.errorbar(x[6:11], y3_3, e3_3, linestyle='None', marker='o', label='Bag 2')
plt.errorbar(x[11:15], y4_3, e4_3, linestyle='None', marker='o', label='Bag 3')
plt.axhline(y=ex2_c21m3, color='black')
plt.axhline(y=ex2_c22m3, color='purple')
plt.axhline(y=ex2_c23m3, color='red')
plt.legend()
plt.title('Measured values of CO')
plt.ylabel('ppb')
plt.xticks([])

el1 = Ellipse((x[2],y1_3[2]), 1, 1, color='red', alpha=1, fill=None)
el2 = Ellipse((x[3],y1_3[3]), 1, 1, color='red', alpha=1, fill=None)
el3 = Ellipse((x[7],y3_3[1]), 1, 1, color='red', alpha=1, fill=None)
el4 = Ellipse((x[8],y3_3[2]), 1, 1, color='red', alpha=1, fill=None)
el5 = Ellipse((x[11],y4_3[0]), 1, 1, color='red', alpha=1, fill=None)
el6 = Ellipse((x[12],y4_3[1]), 1, 1, color='red', alpha=1, fill=None)

el7 = Ellipse((x[4],y1_3[4]), 1, 1, color='black', alpha=1, fill=None)
el8 = Ellipse((x[5],y1_3[5]), 1, 1, color='black', alpha=1, fill=None)
el9 = Ellipse((x[9],y3_3[3]), 1, 1, color='black', alpha=1, fill=None)
el10 = Ellipse((x[10],y3_3[4]), 1, 1, color='black', alpha=1, fill=None)
el11 = Ellipse((x[13],y4_3[2]), 1, 1, color='black', alpha=1, fill=None)
el12 = Ellipse((x[14],y4_3[3]), 1, 1, color='black', alpha=1, fill=None)

ax.add_artist(el1)
ax.add_artist(el2)
ax.add_artist(el3)
ax.add_artist(el4)
ax.add_artist(el5)
ax.add_artist(el6)
ax.add_artist(el7)
ax.add_artist(el8)
ax.add_artist(el9)
ax.add_artist(el10)
ax.add_artist(el11)
ax.add_artist(el12)
#%% Plot H2O

x = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9 ,10, 11, 12, 13, 14, 15])

y1_4 = np.array([ex2_b11m4, ex2_b12m4, ex2_b13m4, ex2_b14m4, ex2_b15m4, ex2_b15m4])
#y2_2 = np.array([ex2_b21m2])
y3_4 = np.array([ex2_b31m4, ex2_b32m4, ex2_b33m4, ex2_b34m4, ex2_b35m4])
y4_4 = np.array([ex2_b41m4, ex2_b42m4, ex2_b43m4, ex2_b44m4])

e1_4 = np.array([ex2_b11s4, ex2_b12s4, ex2_b13s4, ex2_b14s4, ex2_b15s4, ex2_b16s4])
#e2_2 = np.array([ex2_b21s2])
e3_4 = np.array([ex2_b31s4, ex2_b32s4, ex2_b33s4, ex2_b34s4, ex2_b35s4])
e4_4 = np.array([ex2_b41s4, ex2_b42s4, ex2_b43s4, ex2_b44s4])

fig, ax = plt.subplots(1,1)
plt.errorbar(x[0:6], y1_4, e1_4, linestyle='None', marker='o', label='Bag 1')
#plt.errorbar(x[3], y2_2, e2_2, linestyle='None', marker='o')
plt.errorbar(x[6:11], y3_4, e3_4, linestyle='None', marker='o', label='Bag 2')
plt.errorbar(x[11:15], y4_4, e4_4, linestyle='None', marker='o', label='Bag 3')
plt.axhline(y=ex2_c21m4, color='black')
plt.axhline(y=ex2_c22m4, color='purple')
plt.axhline(y=ex2_c23m4, color='red')

#%% Plot zakje 2
fig, axs = plt.subplots(4, 1, sharex=True)
axs[0].plot(datai['CO2_cor'][10750:16600][np.isfinite(datai['CO2_cor'])])
axs[0].set_ylabel('ppm')
axs[0].set_title('CO2')
axs[1].plot(datai['CH4_cor'][10750:16600][np.isfinite(datai['CH4_cor'])])
axs[1].set_ylabel('ppb')
axs[1].set_title('CH4')
axs[2].plot(datai['CO_cor'][10750:16600][np.isfinite(datai['CO_cor'])])
axs[2].set_ylabel('ppb')
axs[2].set_title('CO')
axs[3].plot(datai['H2O'][11000:16600][np.isfinite(datai['H2O'])])
axs[3].set_ylabel('%')
axs[3].set_title('H2O')
axs[3].set_xlabel('day, time')
fig.suptitle('Bag 2, zero-air')

#%% Graphs report

#Difference of CO2 over time

fig, ax = plt.subplots (4,1, sharex=True)
diff_b1_sp = (ex2_b14m1-ex2_b13m1)/18.5*1000
diff_b1_lp = (ex2_b16m1-ex2_b15m1)/74.83*1000

diff_b3_sp = (ex2_b33m1-ex2_b32m1)/18.58*1000
diff_b3_lp = (ex2_b35m1-ex2_b34m1)/74.83*1000

diff_b4_spa = (ex2_b42m1-ex2_b41m1)/20.25*1000
diff_b4_lp = (ex2_b44m1-ex2_b43m1)/74.92*1000

e_d_b1_sp = (np.sqrt(ex2_b14s1**2+ex2_b13s1**2))/18.5*1000
e_d_b1_lp = (np.sqrt(ex2_b15s1**2+ex2_b16s1**2))/74.83*1000

e_d_b3_sp = (np.sqrt(ex2_b33s1**2+ex2_b32s1**2))/18.58*1000
e_d_b3_lp = (np.sqrt(ex2_b35s1**2+ex2_b34s1**2))/74.83*1000

e_d_b4_spa = (np.sqrt(ex2_b41s1**2+ex2_b42s1**2))/20.25*1000
e_d_b4_lp = (np.sqrt(ex2_b44s1**2+ex2_b43s1**2))/74.92*1000

x = np.array([1, 2, 3, 4, 5, 6])
y = np.array([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_spa, diff_b4_lp])
e = np.array([e_d_b1_sp, e_d_b1_lp, e_d_b3_sp, e_d_b3_lp, e_d_b4_spa, e_d_b4_lp])

ax[0].errorbar(x[0:2], y[0:2], e[0:2], linestyle='None', marker='o', color='black', markersize='10')
ax[0].errorbar(x[2:4], y[2:4], e[2:4], linestyle='None', marker='o', color='g', markersize='10')
ax[0].errorbar(x[4:6], y[4:6], e[4:6], linestyle='None', marker='o', color='b', markersize='10')
ax[0].set_ylabel('ppb', fontsize=15)
ax[0].set_title('$CO_2$', fontsize=16)
ax[0].axhline(y=0, color='red', linewidth=0.5)

mean_diff_co2 = np.mean([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_spa, diff_b4_lp])
std_diff_co2 = np.std([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_spa, diff_b4_lp])
print( mean_diff_co2, std_diff_co2)

mean_diff_co2_b = np.mean([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_lp])
std_diff_co2_b = np.std([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_lp])
print( mean_diff_co2_b, std_diff_co2_b)
# Difference of CH4 over time

diff_b1_sp = (ex2_b14m2-ex2_b13m2)/18.5*1000
diff_b1_lp = (ex2_b16m2-ex2_b15m2)/74.83*1000

diff_b3_sp = (ex2_b33m2-ex2_b32m2)/18.58*1000
diff_b3_lp = (ex2_b35m2-ex2_b34m2)/74.83*1000

diff_b4_spb = (ex2_b42m2-ex2_b41m2)/20.25*1000
diff_b4_lp = (ex2_b44m2-ex2_b43m2)/74.92*1000

e_d_b1_sp = (np.sqrt(ex2_b14s2**2+ex2_b13s2**2))/18.5*1000
e_d_b1_lp = (np.sqrt(ex2_b15s2**2+ex2_b16s2**2))/74.83*1000

e_d_b3_sp = (np.sqrt(ex2_b33s2**2+ex2_b32s2**2))/18.58*1000
e_d_b3_lp = (np.sqrt(ex2_b35s2**2+ex2_b34s2**2))/74.83*1000

e_d_b4_spb = (np.sqrt(ex2_b41s2**2+ex2_b42s2**2))/20.25*1000
e_d_b4_lp = (np.sqrt(ex2_b44s2**2+ex2_b43s2**2))/74.92*1000

x = np.array([1, 2, 3, 4, 5, 6])
y = np.array([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_spb, diff_b4_lp])
e = np.array([e_d_b1_sp, e_d_b1_lp, e_d_b3_sp, e_d_b3_lp, e_d_b4_spb, e_d_b4_lp])

ax[1].errorbar(x[0:2], y[0:2], e[0:2], linestyle='None', marker='o', color='black', markersize='10')
ax[1].errorbar(x[2:4], y[2:4], e[2:4], linestyle='None', marker='o', color='g', markersize='10')
ax[1].errorbar(x[4:6], y[4:6], e[4:6], linestyle='None', marker='o', color='b', markersize='10')
ax[1].set_ylabel('ppt', fontsize=15)
ax[1].set_title('$CH_4$', fontsize=16)
ax[1].axhline(y=0, color='red', linewidth=0.5)

mean_diff_ch4 = np.mean([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_spb, diff_b4_lp])
std_diff_ch4 = np.std([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_spb, diff_b4_lp])
print( mean_diff_ch4, std_diff_ch4)

mean_diff_ch4_b = np.mean([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_lp])
std_diff_ch4_b = np.std([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_lp])
print( mean_diff_ch4_b, std_diff_ch4_b)
# Difference of CO over time

diff_b1_sp = (ex2_b14m3-ex2_b13m3)/18.5*1000
diff_b1_lp = (ex2_b16m3-ex2_b15m3)/74.83*1000

diff_b3_sp = (ex2_b33m3-ex2_b32m3)/18.58*1000
diff_b3_lp = (ex2_b35m3-ex2_b34m3)/74.83*1000

diff_b4_spc = (ex2_b42m3-ex2_b41m3)/20.25*1000
diff_b4_lp = (ex2_b44m3-ex2_b43m3)/74.92*1000

e_d_b1_sp = (np.sqrt(ex2_b14s3**2+ex2_b13s3**2))/18.5*1000
e_d_b1_lp = (np.sqrt(ex2_b15s3**2+ex2_b16s3**2))/74.83*1000

e_d_b3_sp = (np.sqrt(ex2_b33s3**2+ex2_b32s3**2))/18.58*1000
e_d_b3_lp = (np.sqrt(ex2_b35s3**2+ex2_b34s3**2))/74.83*1000

e_d_b4_spc = (np.sqrt(ex2_b41s3**2+ex2_b42s3**2))/20.25*1000
e_d_b4_lp = (np.sqrt(ex2_b44s3**2+ex2_b43s3**2))/74.92*1000

x = np.array([1, 2, 3, 4, 5, 6])
y = np.array([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_spc, diff_b4_lp])
e = np.array([e_d_b1_sp, e_d_b1_lp, e_d_b3_sp, e_d_b3_lp, e_d_b4_spc, e_d_b4_lp])

ax[2].errorbar(x[0:2], y[0:2], linestyle='None', marker='o', color='black', markersize='10')
ax[2].errorbar(x[2:4], y[2:4], linestyle='None', marker='o', color='g', markersize='10')
ax[2].errorbar(x[4:6], y[4:6], linestyle='None', marker='o', color='b', markersize='10')
ax[2].set_ylabel('ppt', fontsize=15)
ax[2].set_title('CO', fontsize=16)
ax[2].axhline(y=0, color='red', linewidth=0.5)

mean_diff_co = np.mean([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_spc, diff_b4_lp])
std_diff_co = np.std([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_spc, diff_b4_lp])
print( mean_diff_co, std_diff_co)

mean_diff_co_b = np.mean([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_lp])
std_diff_co_b = np.std([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_lp])
print( mean_diff_co_b, std_diff_co_b)
# Difference of H2O over time

diff_b1_sp = (ex2_b14m4-ex2_b13m4)/18.5*10
diff_b1_lp = (ex2_b16m4-ex2_b15m4)/74.83*10

diff_b3_sp = (ex2_b33m4-ex2_b32m4)/18.58*10
diff_b3_lp = (ex2_b35m4-ex2_b34m4)/74.83*10

diff_b4_spd = (ex2_b42m4-ex2_b41m4)/20.25*10
diff_b4_lp = (ex2_b44m4-ex2_b43m4)/74.92*10

e_d_b1_sp = (np.sqrt(ex2_b14s4**2+ex2_b13s4**2))/18.5*10
e_d_b1_lp = (np.sqrt(ex2_b15s4**2+ex2_b16s4**2))/74.83*10

e_d_b3_sp = (np.sqrt(ex2_b33s4**2+ex2_b32s4**2))/18.58*10
e_d_b3_lp = (np.sqrt(ex2_b35s4**2+ex2_b34s4**2))/74.83*10

e_d_b4_spd = (np.sqrt(ex2_b41s4**2+ex2_b42s4**2))/20.25*10
e_d_b4_lp = (np.sqrt(ex2_b44s4**2+ex2_b43s4**2))/74.92*10

x = np.array([1, 2, 3, 4, 5, 6])
y = np.array([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_spd, diff_b4_lp])
e = np.array([e_d_b1_sp, e_d_b1_lp, e_d_b3_sp, e_d_b3_lp, e_d_b4_spd, e_d_b4_lp])

ax[3].errorbar(x[0:2], y[0:2], e[0:2], linestyle='None', marker='o', color='black', label='Bag 1', markersize='10')
ax[3].errorbar(x[2:4], y[2:4], e[2:4], linestyle='None', marker='o', color='g', label='Bag 3', markersize='10')
ax[3].errorbar(x[4:6], y[4:6], e[4:6], linestyle='None', marker='o', color='b', label='Bag 4', markersize='10')
ax[3].set_ylabel(u'\u2030', fontsize=15)
ax[3].set_title('$H_2O$', fontsize=16)
ax[3].axhline(y=0, color='red', linewidth=0.5)

mean_diff_h2o = np.mean([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_spd, diff_b4_lp])
std_diff_h2o = np.std([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_spd, diff_b4_lp])
print( mean_diff_h2o, std_diff_h2o)

mean_diff_h2o_b = np.mean([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_lp])
std_diff_h2o_b = np.std([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_lp])
print( mean_diff_h2o_b, std_diff_h2o_b)

xticks_labels=['Bag 1 - short', 'Bag 1 - long', 'Bag 3 - short', 'Bag 3 - long', 'Bag 4 - short', 'Bag 4 - long']
plt.setp(ax, xticks=[1, 2, 3, 4, 5, 6], xticklabels=['Bag 1 - short', 'Bag 1 - long', 'Bag 3 - short', 'Bag 3 - long', 'Bag 4 - short', 'Bag 4 - long'])


for item in (ax[3].get_xticklabels()):
    item.set_fontsize(15)
    
for item in (ax[3].get_yticklabels()):
    item.set_fontsize(13)
    
for item in (ax[2].get_yticklabels()):
    item.set_fontsize(13)
    
for item in (ax[1].get_yticklabels()):
    item.set_fontsize(13)
    
for item in (ax[0].get_yticklabels()):
    item.set_fontsize(13)

fig.suptitle('Change in trace gas mole fraction per hour', fontsize=18)



#%% Graphs for presentation

#Difference of CO2 over time

fig, ax = plt.subplots (4,1, sharex=True)
diff_b1_spa = (ex2_b14m1-ex2_b13m1)/18.5*1000
diff_b1_lpa = (ex2_b16m1-ex2_b15m1)/74.83*1000

diff_b3_spa = (ex2_b33m1-ex2_b32m1)/18.58*1000
diff_b3_lpa = (ex2_b35m1-ex2_b34m1)/74.83*1000

diff_b4_spa = (ex2_b42m1-ex2_b41m1)/20.25*1000
diff_b4_lpa = (ex2_b44m1-ex2_b43m1)/74.92*1000

e_d_b1_sp = (np.sqrt(ex2_b14s1**2+ex2_b13s1**2))/18.5*1000
e_d_b1_lp = (np.sqrt(ex2_b15s1**2+ex2_b16s1**2))/74.83*1000

e_d_b3_sp = (np.sqrt(ex2_b33s1**2+ex2_b32s1**2))/18.58*1000
e_d_b3_lp = (np.sqrt(ex2_b35s1**2+ex2_b34s1**2))/74.83*1000

e_d_b4_spa = (np.sqrt(ex2_b41s1**2+ex2_b42s1**2))/20.25*1000
e_d_b4_lpa = (np.sqrt(ex2_b44s1**2+ex2_b43s1**2))/74.92*1000

x = np.array([1, 2, 3, 4, 5, 6])
y = np.array([diff_b1_spa, diff_b1_lpa, diff_b3_spa, diff_b3_lpa, diff_b4_spa, diff_b4_lpa])
e = np.array([e_d_b1_sp, e_d_b1_lp, e_d_b3_sp, e_d_b3_lp, e_d_b4_spa, e_d_b4_lp])

ax[0].errorbar(x[0:2], y[0:2], e[0:2], linestyle='None', marker='o', color='black', markersize='12')
ax[0].errorbar(x[2:4], y[2:4], e[2:4], linestyle='None', marker='o', color='g', markersize='12')
ax[0].errorbar(x[4:6], y[4:6], e[4:6], linestyle='None', marker='o', color='b', markersize='12')
ax[0].set_ylabel('x$10^{-3}$ ppm', fontsize=20)
ax[0].set_title('$CO_2$', fontsize=25)
ax[0].axhline(y=0, color='grey', linewidth=1)

mean_diff_co2 = np.mean([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_spa, diff_b4_lp])
std_diff_co2 = np.std([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_spa, diff_b4_lp])
print( mean_diff_co2, std_diff_co2)

mean_diff_co2_b = np.mean([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_lp])
std_diff_co2_b = np.std([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_lp])
print( mean_diff_co2_b, std_diff_co2_b)
# Difference of CH4 over time

diff_b1_spb = (ex2_b14m2-ex2_b13m2)/18.5*1000
diff_b1_lpb = (ex2_b16m2-ex2_b15m2)/74.83*1000

diff_b3_spb = (ex2_b33m2-ex2_b32m2)/18.58*1000
diff_b3_lpb = (ex2_b35m2-ex2_b34m2)/74.83*1000

diff_b4_spb = (ex2_b42m2-ex2_b41m2)/20.25*1000
diff_b4_lpb = (ex2_b44m2-ex2_b43m2)/74.92*1000

e_d_b1_sp = (np.sqrt(ex2_b14s2**2+ex2_b13s2**2))/18.5*1000
e_d_b1_lp = (np.sqrt(ex2_b15s2**2+ex2_b16s2**2))/74.83*1000

e_d_b3_sp = (np.sqrt(ex2_b33s2**2+ex2_b32s2**2))/18.58*1000
e_d_b3_lp = (np.sqrt(ex2_b35s2**2+ex2_b34s2**2))/74.83*1000

e_d_b4_spb = (np.sqrt(ex2_b41s2**2+ex2_b42s2**2))/20.25*1000
e_d_b4_lpb = (np.sqrt(ex2_b44s2**2+ex2_b43s2**2))/74.92*1000

x = np.array([1, 2, 3, 4, 5, 6])
y = np.array([diff_b1_spb, diff_b1_lpb, diff_b3_spb, diff_b3_lpb, diff_b4_spb, diff_b4_lpb])
e = np.array([e_d_b1_sp, e_d_b1_lp, e_d_b3_sp, e_d_b3_lp, e_d_b4_spb, e_d_b4_lp])

ax[1].errorbar(x[0:2], y[0:2], e[0:2], linestyle='None', marker='o', color='black', markersize='12')
ax[1].errorbar(x[2:4], y[2:4], e[2:4], linestyle='None', marker='o', color='g', markersize='12')
ax[1].errorbar(x[4:6], y[4:6], e[4:6], linestyle='None', marker='o', color='b', markersize='12')
ax[1].set_ylabel('x$10^{-3}$ ppb', fontsize=20)
ax[1].set_title('$CH_4$', fontsize=25)
ax[1].axhline(y=0, color='grey', linewidth=1)

mean_diff_ch4 = np.mean([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_spb, diff_b4_lp])
std_diff_ch4 = np.std([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_spb, diff_b4_lp])
print( mean_diff_ch4, std_diff_ch4)

mean_diff_ch4_b = np.mean([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_lp])
std_diff_ch4_b = np.std([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_lp])
print( mean_diff_ch4_b, std_diff_ch4_b)
# Difference of CO over time

diff_b1_spc = (ex2_b14m3-ex2_b13m3)/18.5*1000
diff_b1_lpc = (ex2_b16m3-ex2_b15m3)/74.83*1000

diff_b3_spc = (ex2_b33m3-ex2_b32m3)/18.58*1000
diff_b3_lpc = (ex2_b35m3-ex2_b34m3)/74.83*1000

diff_b4_spc = (ex2_b42m3-ex2_b41m3)/20.25*1000
diff_b4_lpc = (ex2_b44m3-ex2_b43m3)/74.92*1000

e_d_b1_spc = (np.sqrt(ex2_b14s3**2+ex2_b13s3**2))/18.5*1000
e_d_b1_lpc = (np.sqrt(ex2_b15s3**2+ex2_b16s3**2))/74.83*1000

e_d_b3_spc = (np.sqrt(ex2_b33s3**2+ex2_b32s3**2))/18.58*1000
e_d_b3_lpc = (np.sqrt(ex2_b35s3**2+ex2_b34s3**2))/74.83*1000

e_d_b4_spc = (np.sqrt(ex2_b41s3**2+ex2_b42s3**2))/20.25*1000
e_d_b4_lpc = (np.sqrt(ex2_b44s3**2+ex2_b43s3**2))/74.92*1000

x = np.array([1, 2, 3, 4, 5, 6])
y = np.array([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_spc, diff_b4_lp])
e = np.array([e_d_b1_sp, e_d_b1_lp, e_d_b3_sp, e_d_b3_lp, e_d_b4_spc, e_d_b4_lp])

ax[2].errorbar(x[0:2], y[0:2], e[0:2], linestyle='None', marker='o', color='black', markersize='12')
ax[2].errorbar(x[2:4], y[2:4], e[2:4], linestyle='None', marker='o', color='g', markersize='12')
ax[2].errorbar(x[4:6], y[4:6], e[4:6], linestyle='None', marker='o', color='b', markersize='12')
ax[2].set_ylabel('x$10^{-3}$ ppb', fontsize=20)
ax[2].set_title('CO', fontsize=25)
ax[2].axhline(y=0, color='grey', linewidth=1)

mean_diff_co = np.mean([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_spc, diff_b4_lp])
std_diff_co = np.std([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_spc, diff_b4_lp])
print( mean_diff_co, std_diff_co)

mean_diff_co_b = np.mean([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_lp])
std_diff_co_b = np.std([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_lp])
print( mean_diff_co_b, std_diff_co_b)
# Difference of H2O over time

diff_b1_spd = (ex2_b14m4-ex2_b13m4)/18.5*10
diff_b1_lpd = (ex2_b16m4-ex2_b15m4)/74.83*10

diff_b3_spd = (ex2_b33m4-ex2_b32m4)/18.58*10
diff_b3_lpd = (ex2_b35m4-ex2_b34m4)/74.83*10

diff_b4_spd = (ex2_b42m4-ex2_b41m4)/20.25*10
diff_b4_lpd = (ex2_b44m4-ex2_b43m4)/74.92*10

e_d_b1_sp = (np.sqrt(ex2_b14s4**2+ex2_b13s4**2))/18.5*10
e_d_b1_lp = (np.sqrt(ex2_b15s4**2+ex2_b16s4**2))/74.83*10

e_d_b3_sp = (np.sqrt(ex2_b33s4**2+ex2_b32s4**2))/18.58*10
e_d_b3_lp = (np.sqrt(ex2_b35s4**2+ex2_b34s4**2))/74.83*10

e_d_b4_spd = (np.sqrt(ex2_b41s4**2+ex2_b42s4**2))/20.25*10
e_d_b4_lpd = (np.sqrt(ex2_b44s4**2+ex2_b43s4**2))/74.92*10

x = np.array([1, 2, 3, 4, 5, 6])
y = np.array([diff_b1_spd, diff_b1_lpd, diff_b3_spd, diff_b3_lpd, diff_b4_spd, diff_b4_lpd])
e = np.array([e_d_b1_sp, e_d_b1_lp, e_d_b3_sp, e_d_b3_lp, e_d_b4_spd, e_d_b4_lp])

ax[3].errorbar(x[0:2], y[0:2], e[0:2], linestyle='None', marker='o', color='black', label='Bag 1', markersize='12')
ax[3].errorbar(x[2:4], y[2:4], e[2:4], linestyle='None', marker='o', color='g', label='Bag 3', markersize='12')
ax[3].errorbar(x[4:6], y[4:6], e[4:6], linestyle='None', marker='o', color='b', label='Bag 4', markersize='12')
ax[3].set_ylabel(u'\u2030', fontsize=25)
ax[3].set_title('$H_2O$', fontsize=25)
ax[3].axhline(y=0, color='grey', linewidth=1)

mean_diff_h2o = np.mean([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_spd, diff_b4_lp])
std_diff_h2o = np.std([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_spd, diff_b4_lp])
print( mean_diff_h2o, std_diff_h2o)

mean_diff_h2o_b = np.mean([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_lp])
std_diff_h2o_b = np.std([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_lp])
print( mean_diff_h2o_b, std_diff_h2o_b)

xticks_labels=['Bag 1 - short', 'Bag 1 - long', 'Bag 3 - short', 'Bag 3 - long', 'Bag 4 - short', 'Bag 4 - long']
plt.setp(ax, xticks=[1, 2, 3, 4, 5, 6], xticklabels=['Bag 1 - short', 'Bag 1 - long', 'Bag 3 - short', 'Bag 3 - long', 'Bag 4 - short', 'Bag 4 - long'])


for item in (ax[3].get_xticklabels()):
    item.set_fontsize(23)
    
for item in (ax[3].get_yticklabels()):
    item.set_fontsize(20)
    
for item in (ax[2].get_yticklabels()):
    item.set_fontsize(20)
    
for item in (ax[1].get_yticklabels()):
    item.set_fontsize(20)
    
for item in (ax[0].get_yticklabels()):
    item.set_fontsize(20)

fig.suptitle('Change in trace gas mole fraction per hour', fontsize=25)

#%% Plot flux to concentration difference

flux_co2a = np.array([diff_b1_spa, diff_b3_spa, diff_b4_spa])
flux_co2b = np.array([diff_b1_lpa, diff_b3_lpa, diff_b4_lpa])

gradient_co2a = np.array([450-(ex2_b14m1+ex2_b13m1)/2, 450-(ex2_b33m1+ex2_b32m1)/2, 450-(ex2_b42m1+ex2_b41m1)/2])
gradient_co2b = np.array([450-(ex2_b16m1+ex2_b15m1)/2, 450-(ex2_b35m1+ex2_b34m1)/2, 450-(ex2_b44m1+ex2_b43m1)/2])

plt.figure(1)
plt.plot(gradient_co2a, flux_co2a, linestyle='None', marker='o',color='blue')
plt.plot(gradient_co2b, flux_co2b, linestyle='None', marker='o', color='red')
plt.title('CO2')

flux_ch4a = np.array([diff_b1_spb, diff_b3_spb, diff_b4_spb])
flux_ch4b = np.array([diff_b1_lpb, diff_b3_lpb, diff_b4_lpb])

gradient_ch4a = np.array([2150-(ex2_b14m2+ex2_b13m2)/2, 2150-(ex2_b33m2+ex2_b32m2)/2, 2150-(ex2_b42m2+ex2_b41m2)/2])
gradient_ch4b = np.array([2150-(ex2_b16m2+ex2_b15m2)/2, 2150-(ex2_b35m2+ex2_b34m2)/2, 2150-(ex2_b44m2+ex2_b43m2)/2])

plt.figure(2)
plt.plot(gradient_ch4a, flux_ch4a, linestyle='None', marker='o',color='blue')
plt.plot(gradient_ch4b, flux_ch4b, linestyle='None', marker='o', color='red')
plt.title('CH4')

flux_coa = np.array([diff_b1_spc, diff_b3_spc, diff_b4_spc])
flux_cob = np.array([diff_b1_lpc, diff_b3_lpc, diff_b4_lpc])

gradient_coa = np.array([(ex2_b14m3+ex2_b13m3)/2-160,(ex2_b33m3+ex2_b32m3)/2-160,(ex2_b42m3+ex2_b41m3)/2-160])
gradient_cob = np.array([(ex2_b16m3+ex2_b15m3)/2-160,(ex2_b35m3+ex2_b34m3)/2-160,(ex2_b44m3+ex2_b43m3)/2-160])

plt.figure(3)
plt.plot(gradient_coa, flux_coa, linestyle='None', marker='o',color='blue')
plt.plot(gradient_cob, flux_cob, linestyle='None', marker='o', color='red')
plt.title('CO')

flux_h2oa = np.array([diff_b1_spd, diff_b3_spd, diff_b4_spd])
flux_h2ob = np.array([diff_b1_lpd, diff_b3_lpd, diff_b4_lpd])

gradient_h2oa = np.array([1.25-(ex2_b14m4+ex2_b13m4)/2, 1.25-(ex2_b33m4+ex2_b32m4)/2, 1.25-(ex2_b42m4+ex2_b41m4)/2])
gradient_h2ob = np.array([1.25-(ex2_b16m4+ex2_b15m4)/2, 1.25-(ex2_b35m4+ex2_b34m4)/2, 1.25-(ex2_b44m4+ex2_b43m4)/2])

plt.figure(4)
plt.plot(gradient_h2oa, flux_h2oa, linestyle='None', marker='o',color='blue')
plt.plot(gradient_h2ob, flux_h2ob, linestyle='None', marker='o', color='red')
plt.title('H2O')

#%% Graphs for presentation (total flux)

#Difference of CO2 over time

fig, ax = plt.subplots (4,1, sharex=True)
diff_b1_spa = (ex2_b14m1-ex2_b13m1)
diff_b1_lpa = (ex2_b16m1-ex2_b15m1)

diff_b3_spa = (ex2_b33m1-ex2_b32m1)
diff_b3_lpa = (ex2_b35m1-ex2_b34m1)

diff_b4_spa = (ex2_b42m1-ex2_b41m1)
diff_b4_lpa = (ex2_b44m1-ex2_b43m1)

e_d_b1_sp = (np.sqrt(ex2_b14s1**2+ex2_b13s1**2))
e_d_b1_lp = (np.sqrt(ex2_b15s1**2+ex2_b16s1**2))

e_d_b3_sp = (np.sqrt(ex2_b33s1**2+ex2_b32s1**2))
e_d_b3_lp = (np.sqrt(ex2_b35s1**2+ex2_b34s1**2))

e_d_b4_spa = (np.sqrt(ex2_b41s1**2+ex2_b42s1**2))
e_d_b4_lp = (np.sqrt(ex2_b44s1**2+ex2_b43s1**2))

x = np.array([1, 2, 3, 4, 5, 6])
y = np.array([diff_b1_spa, diff_b1_lpa, diff_b3_spa, diff_b3_lpa, diff_b4_spa, diff_b4_lpa])
e = np.array([e_d_b1_sp, e_d_b1_lp, e_d_b3_sp, e_d_b3_lp, e_d_b4_spa, e_d_b4_lp])

ax[0].errorbar(x[0:2], y[0:2], e[0:2], linestyle='None', marker='o', color='black', markersize='12')
ax[0].errorbar(x[2:4], y[2:4], e[2:4], linestyle='None', marker='o', color='g', markersize='12')
ax[0].errorbar(x[4:6], y[4:6], e[4:6], linestyle='None', marker='o', color='b', markersize='12')
ax[0].set_ylabel('ppm', fontsize=15)
ax[0].set_title('$CO_2$', fontsize=16)
ax[0].axhline(y=0, color='red', linewidth=0.5)

mean_diff_co2 = np.mean([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_spa, diff_b4_lp])
std_diff_co2 = np.std([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_spa, diff_b4_lp])
print( mean_diff_co2, std_diff_co2)

mean_diff_co2_b = np.mean([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_lp])
std_diff_co2_b = np.std([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_lp])
print( mean_diff_co2_b, std_diff_co2_b)
# Difference of CH4 over time

diff_b1_spb = (ex2_b14m2-ex2_b13m2)
diff_b1_lpb = (ex2_b16m2-ex2_b15m2)

diff_b3_spb = (ex2_b33m2-ex2_b32m2)
diff_b3_lpb = (ex2_b35m2-ex2_b34m2)

diff_b4_spb = (ex2_b42m2-ex2_b41m2)
diff_b4_lpb = (ex2_b44m2-ex2_b43m2)

e_d_b1_sp = (np.sqrt(ex2_b14s2**2+ex2_b13s2**2))
e_d_b1_lp = (np.sqrt(ex2_b15s2**2+ex2_b16s2**2))

e_d_b3_sp = (np.sqrt(ex2_b33s2**2+ex2_b32s2**2))
e_d_b3_lp = (np.sqrt(ex2_b35s2**2+ex2_b34s2**2))

e_d_b4_spb = (np.sqrt(ex2_b41s2**2+ex2_b42s2**2))
e_d_b4_lp = (np.sqrt(ex2_b44s2**2+ex2_b43s2**2))

x = np.array([1, 2, 3, 4, 5, 6])
y = np.array([diff_b1_spb, diff_b1_lpb, diff_b3_spb, diff_b3_lpb, diff_b4_spb, diff_b4_lpb])
e = np.array([e_d_b1_sp, e_d_b1_lp, e_d_b3_sp, e_d_b3_lp, e_d_b4_spb, e_d_b4_lp])

ax[1].errorbar(x[0:2], y[0:2], e[0:2], linestyle='None', marker='o', color='black', markersize='12')
ax[1].errorbar(x[2:4], y[2:4], e[2:4], linestyle='None', marker='o', color='g', markersize='12')
ax[1].errorbar(x[4:6], y[4:6], e[4:6], linestyle='None', marker='o', color='b', markersize='12')
ax[1].set_ylabel('ppb', fontsize=15)
ax[1].set_title('$CH_4$', fontsize=16)
ax[1].axhline(y=0, color='red', linewidth=0.5)

mean_diff_ch4 = np.mean([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_spb, diff_b4_lp])
std_diff_ch4 = np.std([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_spb, diff_b4_lp])
print( mean_diff_ch4, std_diff_ch4)

mean_diff_ch4_b = np.mean([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_lp])
std_diff_ch4_b = np.std([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_lp])
print( mean_diff_ch4_b, std_diff_ch4_b)
# Difference of CO over time

diff_b1_spc = (ex2_b14m3-ex2_b13m3)
diff_b1_lpc = (ex2_b16m3-ex2_b15m3)

diff_b3_spc = (ex2_b33m3-ex2_b32m3)
diff_b3_lpc = (ex2_b35m3-ex2_b34m3)

diff_b4_spc = (ex2_b42m3-ex2_b41m3)
diff_b4_lpc = (ex2_b44m3-ex2_b43m3)

e_d_b1_spc = (np.sqrt(ex2_b14s3**2+ex2_b13s3**2))
e_d_b1_lpc = (np.sqrt(ex2_b15s3**2+ex2_b16s3**2))

e_d_b3_spc = (np.sqrt(ex2_b33s3**2+ex2_b32s3**2))
e_d_b3_lpc = (np.sqrt(ex2_b35s3**2+ex2_b34s3**2))

e_d_b4_spc = (np.sqrt(ex2_b41s3**2+ex2_b42s3**2))
e_d_b4_lpc = (np.sqrt(ex2_b44s3**2+ex2_b43s3**2))

x = np.array([1, 2, 3, 4, 5, 6])
y = np.array([diff_b1_spc, diff_b1_lpc, diff_b3_spc, diff_b3_lpc, diff_b4_spc, diff_b4_lpc])
e = np.array([e_d_b1_sp, e_d_b1_lp, e_d_b3_sp, e_d_b3_lp, e_d_b4_spc, e_d_b4_lp])

ax[2].errorbar(x[0:2], y[0:2], linestyle='None', marker='o', color='black', markersize='12')
ax[2].errorbar(x[2:4], y[2:4], linestyle='None', marker='o', color='g', markersize='12')
ax[2].errorbar(x[4:6], y[4:6], linestyle='None', marker='o', color='b', markersize='12')
ax[2].set_ylabel('ppb', fontsize=15)
ax[2].set_title('CO', fontsize=16)
ax[2].axhline(y=0, color='red', linewidth=0.5)

mean_diff_co = np.mean([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_spc, diff_b4_lp])
std_diff_co = np.std([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_spc, diff_b4_lp])
print( mean_diff_co, std_diff_co)

mean_diff_co_b = np.mean([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_lp])
std_diff_co_b = np.std([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_lp])
print( mean_diff_co_b, std_diff_co_b)
# Difference of H2O over time

diff_b1_spd = (ex2_b14m4-ex2_b13m4)*10
diff_b1_lpd = (ex2_b16m4-ex2_b15m4)*10

diff_b3_spd = (ex2_b33m4-ex2_b32m4)*10
diff_b3_lpd = (ex2_b35m4-ex2_b34m4)*10

diff_b4_spd = (ex2_b42m4-ex2_b41m4)*10
diff_b4_lpd = (ex2_b44m4-ex2_b43m4)*10

e_d_b1_sp = (np.sqrt(ex2_b14s4**2+ex2_b13s4**2))*10
e_d_b1_lp = (np.sqrt(ex2_b15s4**2+ex2_b16s4**2))*10

e_d_b3_sp = (np.sqrt(ex2_b33s4**2+ex2_b32s4**2))*10
e_d_b3_lp = (np.sqrt(ex2_b35s4**2+ex2_b34s4**2))*10

e_d_b4_spd = (np.sqrt(ex2_b41s4**2+ex2_b42s4**2))*10
e_d_b4_lp = (np.sqrt(ex2_b44s4**2+ex2_b43s4**2))*10

x = np.array([1, 2, 3, 4, 5, 6])
y = np.array([diff_b1_spd, diff_b1_lpd, diff_b3_spd, diff_b3_lpd, diff_b4_spd, diff_b4_lpd])
e = np.array([e_d_b1_sp, e_d_b1_lp, e_d_b3_sp, e_d_b3_lp, e_d_b4_spd, e_d_b4_lp])

ax[3].errorbar(x[0:2], y[0:2], e[0:2], linestyle='None', marker='o', color='black', label='Bag 1', markersize='12')
ax[3].errorbar(x[2:4], y[2:4], e[2:4], linestyle='None', marker='o', color='g', label='Bag 3', markersize='12')
ax[3].errorbar(x[4:6], y[4:6], e[4:6], linestyle='None', marker='o', color='b', label='Bag 4', markersize='12')
ax[3].set_ylabel(u'\u2030', fontsize=15)
ax[3].set_title('$H_2O$', fontsize=16)
ax[3].axhline(y=0, color='red', linewidth=0.5)

mean_diff_h2o = np.mean([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_spd, diff_b4_lp])
std_diff_h2o = np.std([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_spd, diff_b4_lp])
print( mean_diff_h2o, std_diff_h2o)

mean_diff_h2o_b = np.mean([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_lp])
std_diff_h2o_b = np.std([diff_b1_sp, diff_b1_lp, diff_b3_sp, diff_b3_lp, diff_b4_lp])
print( mean_diff_h2o_b, std_diff_h2o_b)

xticks_labels=['Bag 1 - short', 'Bag 1 - long', 'Bag 3 - short', 'Bag 3 - long', 'Bag 4 - short', 'Bag 4 - long']
plt.setp(ax, xticks=[1, 2, 3, 4, 5, 6], xticklabels=['Bag 1 - short', 'Bag 1 - long', 'Bag 3 - short', 'Bag 3 - long', 'Bag 4 - short', 'Bag 4 - long'])


for item in (ax[3].get_xticklabels()):
    item.set_fontsize(15)
    
for item in (ax[3].get_yticklabels()):
    item.set_fontsize(13)
    
for item in (ax[2].get_yticklabels()):
    item.set_fontsize(13)
    
for item in (ax[1].get_yticklabels()):
    item.set_fontsize(13)
    
for item in (ax[0].get_yticklabels()):
    item.set_fontsize(13)

fig.suptitle('Total change in trace gas mole fraction', fontsize=18)
