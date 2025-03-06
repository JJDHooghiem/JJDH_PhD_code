#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Don't remove the line below, it is checked by "one to run them all"
# --otrta-p--
# extension p means parallel, s is for single
"""
Created on Wed Jul  5 09:12:38 2017
@author: Joram
"""
#==============================================================================
# Pressure regulated chamber experiments
# To test the performance of the sampling system
#  
#==============================================================================
#==============================================================================
# Import required modules 
#==============================================================================

import os

import matplotlib
# matplotlib.use("Qt5Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import config
import scantools
from scipy.interpolate import interp1d
from scipy.optimize import curve_fit
#==============================================================================
# Define constants 
#==============================================================================

R=8.3144598     # Universal gas constant in unit kg/m2/s^2 /k/mol
V_b=0.00258     # Volume of sampling bag
Pstp= 100000.   # Standard atmospheric pressure in pascal
Tstp=273.15     # Standard atmospheric temperature STP in calvin 

def linfit(x,a,b):      # Linear
    return a*x+b

def lin(x,a):           # Linear force through zero 
    return a*x
    
def quadratic(x,a,b,c):
    return a*x**2+b*x+c
    
def quadratic2(x,a,b):
    return a*x**2+x*b   
        
def r_value(x, y):
    yhat=np.mean(y)
    
    sstot=np.sum([(y[i]-yhat)**2 for i in range(0,len(y))])
   
    ssres=np.sum([(y[i]-x[i])**2 for i in range(0,len(y))])

    r_value=1-(ssres/sstot)
    return r_value
    
def expsumfit(time,X,a,tau):
    return X-a*np.exp(-time/tau)
    
def hyper(x,a,b):
    return a/(x**b)
    
def sqrt(x,a,b):
    return np.sqrt(a*x**b)

#R=287.04
#g=9.80665
#
#def Theight(h):
#    return 15-(6.5/1000)*h
#
#T0=288.15
#p0=1013.25
#Gamma=0.0065
#def pheight(h):
#    return p0*(1.-(Gamma/T0)*h)**(g/(Gamma*R))   
#
#h=np.arange(0,11000,0.01)
#
#p=map(pheight,h)
#
#p11=226.32
#h11=11000
#T11=216.65
#def pheighta(h):
#    return p11*np.exp(-(g/(R*T11))*(h-h11))
#h2=np.arange(11000,20000,0.01)
#p2=map(pheighta,h2)
##plt.plot(h,p,h2,p2)
#p=np.concatenate((p,p2),axis=0)
#h=np.concatenate((h,h2),axis=0)
#
#T0=216.65
#p0=p[-1]
#Gamma=-0.001
#def pheight(h):
#    return p0*(1.-(Gamma/T0)*(h-20000))**(g/(Gamma*R))   
#h3=np.arange(20000,32000,0.01)
#p3=map(pheighta,h3)
#p=np.concatenate((p,p3),axis=0)
#h=np.concatenate((h,h3),axis=0)
#
#T0=228.65
#p0=p[-1]
#Gamma=-0.0028
#def pheight(h):
#    return p0*(1.-(Gamma/T0)*(h-32000))**(g/(Gamma*R))   
#h4=np.arange(32000,47000,0.01)
#p4=map(pheight,h4)
#p=np.concatenate((p,p4),axis=0)
#h=np.concatenate((h,h4),axis=0)
#
#pheight=interp1d(h,p) 

import atmos

h=np.linspace(0,50000,50000)
# From Pascal to hecto Pascal:
p=np.array([atmos.Standard_atmos(i)[0] for i in h])/100 
inverse=interp1d(p,h)

#==============================================================================
# Here we import data 
# # Datasets 4exploded and data4 and data5 are not used. Dataset 4(exploded) is not used (Failed experiment)
# # Dataset data4/5nan are not used since the influence of the vacum chamber is very significant (desorption)
#==============================================================================
#os.chdir('/Users/Joram/Documents/Data/Sampler_Development 2017_2016/Vacuum Chamber Oct_2016/Datalogger data 3/') # Go to directory containing files
os.chdir(config.DataDir+'/LISA_Sampler_Development/2016_Datalogger_Vessel/Chamber_data_sets_exp_3/')
data=[]     #list containing datasets
dt=[]       # List Containig dt to determine time deltas to creat time arrays
filelist=['data1','data2','data3'] 

plt.close()
for m in range(0,len(filelist)):
    rawdata1=pd.read_csv('{}.csv'.format(filelist[m]))                                          # Import data as pandas dataframe
    index=int([i for i in range(0,len(rawdata1['Date'])) if rawdata1[' Switch'][i]==570][0])    # ' Switch' == 570 flags the neighbourhood of the beginning of sampling
    #plt.plot(rawdata1[' PressureOut'][index-20:index+100],'o')                                 
    index=rawdata1[' PressureOut'][index-20:index+100].idxmax()                                 # Maximum pressure found after initial sampling starts, Used to align datasets
    #plt.plot(rawdata1[' PressureOut'][index-20:index+20],'o')  
    Servo_closed=[i for i in range(0,len(rawdata1['Date'])) if rawdata1[' Switch'][i]==2]       # Find the flag of termination of sampling
    rawdata1=rawdata1.drop(np.arange(0,index-100,1))    
    rawdata1=rawdata1.drop(np.arange(Servo_closed[0]+26,index-100+len(rawdata1['Date']),1)) 
    rawdata1=rawdata1.reset_index()                                                             # Drop unwanted datapoints
    #plt.plot(rawdata1[' PressureOut'])    
    Time=[]                                                                                     # Time handling.
    for j in range(0,len(rawdata1['Date'])):
        stamp=rawdata1['Date'].iloc[j].split(' ')  
        fig=stamp[1].split(':')
        t=(3600*float(fig[0])+60*float(fig[1])+float(fig[2]))
        Time.append(t)
    rawdata1['Time']=Time
    det=(rawdata1['Time'].iloc[-1]-rawdata1['Time'].iloc[0])/len(rawdata1["Time"])              # Aquire timedeltas for analysis on dt. 
    dt.append(det)
    #plt.plot(rawdata1[' PressureOut'])
    data.append(rawdata1) 

dtm=np.mean(dt)     # mean deltat                                                                                # Time handling. 
dtmstd=np.std(dt)   # standard deviation of delta t (1 sigma, gaussian)
for m in range(0,3):       
    Time=[]
    for j in range(0,len(data[m]['Time'])):
        Time.append(round(j*dtm,9))
    data[m]['Time']=Time
    data[m].index=[pd.to_datetime(str(int(int(Time[i]/60)))+':'+str(np.round(Time[i]-60*int(Time[i]/60),9)),format='%M:%S.%f') for i in range(0,len(Time)) ]
    del(data[m]['Date'])
#    plt.plot(data[m]['Time'],data[m][' PressureOut'])
#==============================================================================
#  All intervals have been selected, and have equally space timearrays     
#==============================================================================
#os.chdir('..')

#==============================================================================
# We require intitial and final pressure in chamber
# Pressurevacu gives the pressure in the chamber prior to pummping
# Pressurevacu1 gives the pressure after sampling
#==============================================================================
p_prio_sampling=[]
p_prio_sampling_std=[]
p_post_sampling=[]
p_post_sampling_std=[]
leakrate_chamber=[]
for i in range(0,3):
    p_prio_sampling.append(np.mean(data[i][' PressureOut'][80:90])) 
    p_prio_sampling_std.append(np.std(data[i][' PressureOut'][80:90]))
    p_post_sampling.append(np.mean(data[i][' PressureOut'][-20:-10])) 
    p_post_sampling_std.append(np.std(data[i][' PressureOut'][-20:-10]))  
    leakrate_chamber.append((data[i][' PressureOut'][-20]-data[i][' PressureOut'][80])/(data[i]['Time'][-20]-data[i]['Time'][80]))
#    plt.plot(data[i][' PressureOut'][80:90],'o')
    #plt.plot(data[i][' PressureOut'][100:180],'b')
#    plt.plot(data[i][' PressureOut'][-20:-10],'o')
#    plt.plot(data[i][' PressureOut'],'b')

drift=pd.DataFrame(data={'Name':filelist,'p_start (mbar)':p_prio_sampling,'p_start std (mbar)':p_prio_sampling_std,'p_end (mbar)':p_post_sampling,'p_end std (mbar)':p_post_sampling_std,'Leak rate mbar/s':leakrate_chamber})    

#os.chdir('Processed data')
#drift.to_csv('Vacuum chamber drift.csv')
#os.chdir('..')


#==============================================================================
# Plot of estimated resolution for several sampling times 
#==============================================================================

times_of_interest=np.array([50,100,150])#np.linspace(5,150,100)#
interpolated_data=[]
data_resampled=[]
for m in range(0,3):
    df=data[m]
    index=[i for i in range(0,len(df[' Switch'])) if df[' Switch'][i]==570]

    index=[i for i in range(0,len(df[' PressureOut'][:index[0]+100])) if df[' PressureOut'][:index[0]+100][i]==max(df[' PressureOut'][:index[0]+100])]
    d=df[index[0]+1:].copy()
    d.loc[:,'Time']=[round(d['Time'][k]-d['Time'][0],9) for k in range(0,len(d['Time']))]
    d.index=[pd.to_datetime(str(int(int(d['Time'][i]/60)))+':'+str(round(d['Time'][i]-60*int(d['Time'][i]/60),9)),format='%M:%S.%f') for i in range(0,len(d['Time']))]
    
    d1=d.resample('5S').mean()
    d2=d.resample('2S').max()
    d3=d.resample('2S').min()
    data_resampled.append(d)
    plt.plot(d1['Time'],d1[' PressureOut'],'o')
    plt.plot(d2['Time'],d2[' PressureOut'],'*')
    plt.plot(d3['Time'],d3[' PressureOut'],'*')
    d=d.resample('5S').mean()
    data_resampled.append(d)
    Pinter=interp1d(d['Time'],d[' PressureOut'],kind='slinear')
    #print(m)
    if m==3:
        interpltd=Pinter(times_of_interest[0])
        interpltd=np.append(interpltd,[np.nan,np.nan])
    else:
        interpltd=Pinter(times_of_interest)
#    x=np.linspace(5,160,1000)
#    y=Pinter(x)
#    plt.plot(x,y) 
#    plt.plot(d['Time'],d[' PressureOut'],'o')   
    
    T=np.mean(df[' TemperatureOut'])
    interpltd=interpltd*(Tstp/(T+Tstp))*(V_b*1000/(Pstp/100))
    interpolated_data.append(interpltd)

#==============================================================================
# With a linear fit, lines for 50,100,150 Seconds of pumping 
# 
#==============================================================================

yerr=0#6.2/1000
                                   # calculated using 0.25% FS uncertainty in pressure measurement
    
#Interdatapointsper=np.array(Interdatapoints).T
#samplesize=Interdatapointsper*2.5/1013
samplesize=np.array(interpolated_data).T
#vmax=250*2.58/1013                               #Theoretical limit of fill bag
colors=['k','k','k']
markers=['d','o','*']
Pcham=p_prio_sampling[:3]
r_sq=[]
stop=[3,3,3]

for i in range(0,len(samplesize)):   
    opt,popt=curve_fit(lin,Pcham[:stop[i]],samplesize[i][:stop[i]])  
    x=np.linspace(0,200,1000)
    y_new=lin(np.array(Pcham[:stop[i]]),*opt)
    r_sq.append(round(r_value(samplesize[i][:stop[i]],y_new)**2,4))
    y_new=lin(x,*opt)
    plt.plot(x,y_new,color=colors[i],linestyle='-.',linewidth=2) #yerr is the same for all at the moment: so maybe not plotting it up? 
    plt.errorbar(Pcham[:stop[i]],samplesize[i][:stop[i]],yerr=yerr,color=colors[i],fmt=markers[i],linestyle='',markersize=10)
#plt.axhline(vmax,color='k')
plt.ylim(0,1)
plt.xlim(0,200)
plt.tick_params(axis='both', which='major', labelsize=16)
plt.ylabel('Sample amount (L$_{stp}$)',fontsize=18)
plt.xlabel('Pressure (hPa)',fontsize=18)
labels=[str(i) for i in times_of_interest]#+' s'
labels=[labels[i]+' s sampling' for i in range(0,len(labels))]


#labels.append('Maximum sample amount')
handles=[]
for m,s,l in zip(markers,colors,labels):
    handles.append(matplotlib.lines.Line2D([],[],marker=m,label=l,color=s))
plt.legend(handles=handles,loc=2,numpoints=1,fontsize=16)
#os.chdir('Processed data')
#plt.savefig('sample_amount_presV2.pdf',format='pdf',figsize=(2,2),bbox_inches='tight')
#plt.show()
plt.close()
#os.chdir('..')

#==============================================================================
# Get data for volume in bag as function of time
#==============================================================================


data1=[]

for m in range(0,len(data)):
    index=[i for i in range(0,len(data[m]['Time'])) if data[m][' Switch'][i]==570]

    index=data[m][' PressureOut'][:index[0]+100].idxmax()
  
    d=data[m][index:]
    d=d[2:]
    #print(d['Time'][0])
    d['Time']=[round(d['Time'][k]-d['Time'][0],9) for k in range(0,len(d['Time']))]
    
    d.index=[pd.to_datetime(str(int(int(d['Time'][i]/60)))+':'+str(round(d['Time'][i]-60*int(d['Time'][i]/60),9)),format='%M:%S.%f') for i in range(0,len(d['Time']))]
    
    d=d.resample('5S').mean()
    data1.append(d)

    plt.plot(d['Time'],d[' PressureOut'],'o')       
    #plt.xlim([index,index]) 
#==============================================================================
#     
#==============================================================================

#plt.show()    
plt.close()

stop=[-3,-3,-3]#,17] #resample 5 Seconds
#stop=[-2,-2,-2,8] #resample 10 Seconds
markers=['o','d','*','s']  
for p,i,m,df in sorted(zip(p_prio_sampling,stop,markers,data1)):
    T=np.mean(df[' TemperatureOut'][:i])
    Tstd=np.std(df[' TemperatureOut'][:i])
    Volume_stp=(Tstp/(Tstp+T))*np.array((df[' PressureOut'][:i]*V_b/(Pstp/100))*1000)
    Volume_stp=np.append(0,Volume_stp[4:])
    Time=np.append(0,df['Time'][4:i])
    plt.plot(Time,Volume_stp,marker=m,linestyle='-.',color='k',label='Chamber pressure: {} (hPa)'.format(round(p,1)),markersize=10,linewidth=2) 
leg=plt.legend(loc=2,numpoints=1,fontsize=16)
plt.ylim(0,1)
plt.tick_params(axis='both', which='major', labelsize=16)
plt.xlabel('Sampling time (s)',fontsize=18)
plt.ylabel('Sample amount (L$_{stp}$)',fontsize=18)
#plt.savefig('Sampling time vs sampleamount_2.pdf',format='pdf',figsize=(2,2),bbox_inches='tight')
#plt.show()
plt.close()


#==============================================================================
# Prepare data for subplots 3,4
#==============================================================================
Times_of_interest_2=np.linspace(0,150,20)#np.array([50,100,150])#np.linspace(5,150,100)#
Interdatapoints_2=[]
data_resampled=[]
ofset=[-30,-30,-30,-225]
rawdata=[]
rawdata_t=[]
for m in range(0,3):
    d=data[m][160:ofset[m]].copy()
    #print(d['Time'][0])
    d.loc[:,'Time']=[round(d['Time'][k]-d['Time'][0],9) for k in range(0,len(d['Time']))]
    d.index=[pd.to_datetime(str(int(int(d['Time'][i]/60)))+':'+str(round(d['Time'][i]-60*int(d['Time'][i]/60),9)),format='%M:%S.%f') for i in range(0,len(d['Time']))]
    rawdata.append(d[' PressureOut']*(Tstp/(T+Tstp))*(V_b*1000/(Pstp/100)/p_prio_sampling[m]))
    rawdata_t.append(d['Time'])    
    optp,poptp=curve_fit(expsumfit,d['Time'],d[' PressureOut']*1000)
    optp[0]=optp[0]/1000
    optp[1]=optp[1]/1000
    p_model=expsumfit(d['Time'],*optp)
    plt.plot(d['Time'],d[' PressureOut'])
    d=d.resample('5S').mean()
    
    data_resampled.append(d)
    plt.plot(d['Time'],d[' PressureOut'])
    #plt.plot(d['Time'],p_model)
    Pinter=interp1d(d['Time'],d[' PressureOut'],kind='slinear')
    #Pinter=interp1d(d['Time'],p_model,kind='slinear')
    interpltd=[]    
    for i in range(0,len(Times_of_interest_2)):
        try:
            interpltd.append(Pinter(Times_of_interest_2[i]))
        except ValueError:
            interpltd.append(np.nan)
#    x=np.linspace(5,160,1000)
#    y=Pinter(x)
#    plt.plot(x,y) 
#    plt.plot(d['Time'],d[' PressureOut'],'o')   
    
    T=np.mean(d[' TemperatureOut'])
    interpltd=np.array(interpltd)*(Tstp/(T+Tstp))*(V_b*1000/(Pstp/100))
    Interdatapoints_2.append(interpltd)
    
#Interdatapointsper=np.array(Interdatapoints).T
#samplesize=Interdatapointsper*2.58/1013.25
samplesize_2=np.array(Interdatapoints_2).T
#vmax=250*2.58/1013                               #Theoretical limit of fill bag
linestyles=['--','-.',':']
markers=['d','o','*']
Pcham=np.array(p_prio_sampling)
r_sq=[]
stop=[3,3,3]
optim=[]
for i in range(0,len(samplesize_2)):   
    
    try:
        opt,popt=curve_fit(lin,Pcham[np.isfinite(samplesize_2[i])],samplesize_2[i][np.isfinite(samplesize_2[i])])  
    except ValueError:
        opt=np.nan
    optim.append(float(opt))

optim=np.array(optim)

#plt.plot(Times_of_interest[np.isfinite(optim1)],optim1[np.isfinite(optim1)])
#plt.plot(Times_of_interest[np.isfinite(optim2)],optim2[np.isfinite(optim2)])
#plt.plot(Times_of_interest[np.isfinite(optim3)],optim3[np.isfinite(optim3)])

optp,poptp=curve_fit(expsumfit,Times_of_interest_2[np.isfinite(optim)],optim[np.isfinite(optim)]*1000)
optp[0]=optp[0]/1000
optp[1]=optp[1]/1000
poptp[0,0]=poptp[0,0]/1000000
poptp[1,1]=poptp[1,1]/1000000

timedume=np.linspace(0,150,1500)
#plt.plot(Times_of_interest[np.isfinite(optim)],expsumfit(Times_of_interest[np.isfinite(optim)],*optp),'k',)
R2=r_value(optim[np.isfinite(optim)],expsumfit(Times_of_interest_2[np.isfinite(optim)],*optp))**2
df={'Parameters':np.array(['x','a','tau']),'Values':optp,'Error':np.sqrt(np.diag(poptp))}
fit_params=pd.DataFrame(df)
#fit_params.to_csv('Fit constantsV3.csv')#
def a_t(time):
    return fit_params['Values'][0]-fit_params['Values'][1]*np.exp(-(time)/ fit_params['Values'][2])
# start time=31.957158613 from data1
# p increase is 51.695403638
# initial time is thus 51.695403638-31.957158613=
Tofset=19.738245025



#==============================================================================
# $ subplots with all the data    
#==============================================================================
xlabs=[config.axl['ts'], config.axl['vsize'],config.axl['ts'],config.axl['vsize'] ] 
ylabs=[config.axl['vsize'],config.axl['pv'],config.axl['lisasdfit'],config.axl['pa']]
xlims=[(0,150),(0,200),(0,160),(0,0.8)]
ylims=[(0,1.2),(0,1.2),(0.003,0.008)]
fig,axes=scantools.plot_init(2,2,xlabs=xlabs,ylabs=ylabs,xlims=xlims,ylims=ylims)
#==============================================================================
#  first figure:
#==============================================================================
stop=[-3,-3,-3]#,17] #resample 5 Seconds
markers=config.Markers
linestyles=['-','-','-']
# colors=['darkblue','Darkgreen','lime','tomato']
colors=config.GruvBoxColors
for p,i,m,df,l,c in sorted(zip(p_prio_sampling,stop,markers,data1,linestyles,colors)):
    T=np.mean(df[' TemperatureOut'][:i])
    Tstd=np.std(df[' TemperatureOut'][:i])
    Volume_stp=(Tstp/(Tstp+T))*np.array((df[' PressureOut'][:i]*V_b/(Pstp/100))*1000)
    Volume_stp=np.append(0,Volume_stp[4:])
    Time=np.append(0,df['Time'][4:i])
    axes[0,0].plot(Time,Volume_stp,marker=m,linestyle=l,color=c,label='{0} hPa'.format(round(p,1)),linewidth=1) 
# leg=axes[0,0].legend(loc=2,numpoints=1,fontsize=6.5)
leg=axes[0,0].legend(loc=2,numpoints=1)
axes[0,0].tick_params(axis='both', which='major')
#Second figure


samplesize=np.array(interpolated_data).T
vmax=300*2.58/1000                               #Practical limit of fill bag

linestyles=['','','','-']
Pcham=p_prio_sampling[:3]
r_sq=[]
stop=[3,3,3]

# second figure
#yerr=0.0076  
#colors=['royalblue','darkcyan','midnightblue','k']
for i in range(0,len(samplesize)):   
    
    opt,popt=curve_fit(lin,Pcham[:stop[i]],samplesize[i][:stop[i]])  

    x=np.linspace(0,200,1000)
    y_new=lin(np.array(Pcham[:stop[i]]),*opt)
    r_sq.append(round(r_value(samplesize[i][:stop[i]],y_new)**2,4))
    y_new=lin(x,*opt)
    axes[0,1].plot(x,y_new,color=colors[i],linestyle='-',linewidth=1) #yerr is the same for all at the moment: so maybe not plotting it up? 
    #colors=['Darkgreen','lime','darkred','k']    
    for m in range(0,len(samplesize)):
        axes[0,1].errorbar(Pcham[:stop[i]][m],samplesize[i][:stop[i]][m],yerr=yerr,color=colors[i],fmt=markers[m],linestyle='')
axes[0,1].axhline(vmax,color='k',linestyle='-.')
axes[0,1].tick_params(axis='both', which='major')
labels=[str(i) for i in times_of_interest]#+' s'
labels=[labels[i]+' s' for i in range(0,len(labels))]
#labels.append('Practical limit')
handles=[]
#colors=['magenta','darkcyan','midnightblue','k']
for m,s,l,li in zip(markers,colors,labels,linestyles):
    handles.append(matplotlib.lines.Line2D([],[],label=l,color=s,linestyle='-'))
leg2=axes[0,1].legend(handles=handles,loc=4,numpoints=1,fontsize=6.5)
#f.savefig('Doublefig.pdf',format='pdf',bbox_inches='tight')

#==============================================================================
# Subplot c
#==============================================================================
axes[1,0].plot(timedume+Tofset,expsumfit(timedume,*optp),color=colors[0],linewidth=2,label='Fit')#: $a=X-b\\exp(\\frac{t}{\\tau})$')#, R$^2$='+str(np.round(R2,4)))
axes[1,0].plot(Times_of_interest_2[np.isfinite(optim)]+Tofset,optim[np.isfinite(optim)],linestyle='',marker='o',color=colors[1],label='Obs. der.')

axes[1,0].legend(loc=4,numpoints=1,fontsize=6.5)
#==============================================================================
# suplot d
#==============================================================================
Pres=np.linspace(10,250,200)
Height=inverse(Pres)
times=np.array([50,100,200,1000])

#colors=['magenta','darkcyan','lime','k']
ax2=axes[1,1].twinx()
V=Pres*a_t(200-Tofset)
Vsample=[V[m] if V[m]<vmax else vmax for m in range(0,len(V))] 
axes[1,1].axvline(vmax,linestyle='-.',color='k')
for c,t in zip(colors,times):
        
#    V=Pres*a_t(180-Tofset)
#    vmax=250*2.58/1000.
#    Vsample_min=[V[m] if V[m]<vmax else vmax for m in range(0,len(V))] 
    
    
    V=Pres*a_t(t-Tofset)
    vmax=300*2.58/1000.
    Vsample_max=[V[m] if V[m]<vmax else vmax for m in range(0,len(V))]  
    axes[1,1].plot(Vsample_max,Height/1000,color=c,linestyle='-',label='{} s'.format(t))
    ax2.plot(Vsample_max,Height/1000,color=c,linestyle='-',label='{} s'.format(t))
axes[1,1].set_ylim(10,30)
ax2.set_ylim(10,30)
ax2.set_ylabel('$z/$km')
y_tick_labels=[atmos.Standard_atmos(i)[0]/100 for i in np.linspace(10000,30000,5)]
y_tick_labels=[round(y,1) for y in y_tick_labels]
ticks_loc = axes[1,1].get_yticks().tolist()
axes[1,1].yaxis.set_major_locator(matplotlib.ticker.FixedLocator(ticks_loc))
axes[1,1].set_yticklabels(y_tick_labels)
#plt.yticks(np.linspace(12,30,10))
axes[1,1].legend(loc=3, ncol=1,fontsize=6.5)
fig.tight_layout()
#f.subplots_adjust(wspace=0.25,hspace=0.25)
fig.savefig(config.FigDir+'lisasd_chamber.pdf',format='pdf',bbox_inches='tight')
plt.close()


exit()

#%%
#==============================================================================
# As vertical resolution with v=5m/s
#==============================================================================
stop=[-3,-3,-3]#,17] #resample 5 Seconds
#stop=[-2,-2,-2,8] #resample 10 Seconds
markers=['o','d','*','s']  
colors=['saddlebrown','Darkgreen','lime','tomato']
for p,i,m,df,c in sorted(zip(p_prio_sampling,stop,markers,data1,colors)):
    T=np.mean(df[' TemperatureOut'][:i])
    Tstd=np.std(df[' TemperatureOut'][:i])
    Volume_stp=(Tstp/(Tstp+T))*np.array((df[' PressureOut'][:i]*V_b/(Pstp/100))*1000)
    Volume_stp=np.append(0,Volume_stp[4:])
    Time=np.append(0,df['Time'][4:i])*5
    plt.plot(Time,Volume_stp,marker='',linestyle='-',color=c,label='Chamber pressure: {} (hPa)'.format(round(p,1)),markersize=10,linewidth=3) 
leg=plt.legend(loc=2,numpoints=1,fontsize=16)
plt.ylim(0,1)
plt.tick_params(axis='both', which='major', labelsize=16)
plt.xlabel('Vertical resolution',fontsize=18)
plt.ylabel('Sample amount (L$_{stp}$)',fontsize=18)
#plt.savefig('Sampling time vs sampleamount_3.pdf',format='pdf',figsize=(2,2),bbox_inches='tight')
plt.show()
plt.close()



colors=['darkred','darkblue','darkcyan']
#for i in range(0,3):
#    plt.plot(rawdata_t[i],rawdata[i],'o',color=colors[i],alpha=0.2,label='raw data {} mbar'.format(Pressurevac[i])) 
plt.plot(timedume,expsumfit(timedume,*optp),'k',linewidth=3,label='Fit: $a=X-b\\exp(\\frac{t}{\\tau})$, R$^2$='+str(np.round(R2,4)))
plt.plot(times_of_interest[np.isfinite(optim)],optim[np.isfinite(optim)],linestyle='',marker='o',color='g',label='Measured')

plt.xlabel('Sampling time (s)',weight='bold',fontsize=14)
plt.ylabel('a (L/hPa)',weight='bold',fontsize=14)
plt.xlim(0,140)
plt.legend(loc=4,fontsize=16,numpoints=1)
#plt.savefig('Slope as a function of t with rawdata.pdf', format='pdf',bbox_inches='tight')
plt.show()
plt.close()
#optp,poptp=curve_fit(expsumfit,Times_of_interest[np.isfinite(optim1)],optim1[np.isfinite(optim1)])
#plt.plot(Times_of_interest[np.isfinite(optim1)],expsumfit(Times_of_interest[np.isfinite(optim1)],*optp),'k')
#optp,poptp=curve_fit(expsumfit,Times_of_interest[np.isfinite(optim2)],optim2[np.isfinite(optim2)])
#plt.plot(Times_of_interest[np.isfinite(optim2)],expsumfit(Times_of_interest[np.isfinite(optim2)],*optp),'k')
#optp,poptp=curve_fit(expsumfit,Times_of_interest[np.isfinite(optim3)],optim3[np.isfinite(optim3)])
#plt.plot(Times_of_interest[np.isfinite(optim3)],expsumfit(Times_of_interest[np.isfinite(optim3)],*optp),'k')
df={'Parameters':np.array(['x','a','tau']),'Values':optp,'Error':np.sqrt(np.diag(poptp))}
fit_params=pd.DataFrame(df)
#fit_params.to_csv('Fit constantsV3.csv')#

for i in range(0,3):
    df=data_resampled[i]
    T=np.mean(df[' TemperatureOut'])
    fig=p_prio_sampling[i]*(Pstp/100)*(T+Tstp)/(V_b*1000*Tstp)
    ymod=fig*expsumfit(df['Time'],*optp)
    plt.plot(df['Time'],ymod,'o')
    plt.plot(df['Time'],df[' PressureOut'],'o')
    print(r_value(df[' PressureOut'],ymod)**2)

for i in range(0,3):
    df=data_resampled[i]
    T=np.mean(df[' TemperatureOut'])
    fig=p_prio_sampling[i]*(Pstp/100)*(T+Tstp)/(V_b*1000*Tstp)
    ymod=fig*expsumfit(df['Time'],*optp)
    plt.plot(df['Time'],df[' PressureOut']-ymod,'o')
    print(np.std(df[' PressureOut']-ymod))
    print(r_value(df[' PressureOut'],ymod)**2)
    

    
#==============================================================================
# Calculate flow rate at stp     
#==============================================================================
#pV=pV so V=V_bag*P_bag/p_stp
colors=['darkgreen','magenta','goldenrod']
for i in range(0,len(data1)):
    n_a=(data1[i][' PressureOut']*V_b*100)/(R*(data1[i][' TemperatureOut']+Tstp)) # Number of moles
    
    
    dn=np.diff(n_a)
    dV=dn*R*np.mean(data1[i][' TemperatureOut']+Tstp)/(p_prio_sampling[i]*100)*1000
    #dV=(dV*(Pressurevac[i]+100)*Tstp)/(Pstp*np.mean(data1[i][' TemperatureOut']+Tstp))*1000    
    #dV=np.diff(V_stp)
    #print(V_stp)
    dt=np.diff(data1[i]['Time'])
    V_rate=(dV*60/dt)
    p_interpolate=interp1d(data1[i]['Time'],data1[i][' PressureOut'])
    
    time=data1[i]['Time'][:-1]+dt/2
    dp=(p_interpolate(time)-p_prio_sampling[i])/p_prio_sampling[i]
    plt.plot(time,V_rate,colors[i],linewidth=2,label='Chamber p={} mbar'.format(p_prio_sampling[i]))
plt.ylim([0,10])
plt.xlabel('Time (s)')
plt.ylabel('Flow rate (l/min)')
plt.legend()
#plt.savefig('Flow rate vs time2.pdf',format='pdf')
plt.show()
plt.close()


#==============================================================================
# Vstp
#==============================================================================
#pV=pV so V=V_bag*P_bag/p_stp
colors=['darkgreen','magenta','goldenrod']
for i in range(0,len(data1)):
    n_a=(data1[i][' PressureOut']*V_b*100)/(R*(data1[i][' TemperatureOut']+Tstp)) # Number of moles
    Vstp=(n_a*R*Tstp/(Pstp))*1000/(p_prio_sampling[i])
    dV=dn*R*np.mean(data1[i][' TemperatureOut']+Tstp)/(p_prio_sampling[i]*100)*1000
    #dV=(dV*(Pressurevac[i]+100)*Tstp)/(Pstp*np.mean(data1[i][' TemperatureOut']+Tstp))*1000    
    #dV=np.diff(V_stp)
    #print(V_stp)
    dt=np.diff(data1[i]['Time'])
    V_rate=(dV*60/dt)
    p_interpolate=interp1d(data1[i]['Time'],data1[i][' PressureOut'])
    
    time=data1[i]['Time'][:-1]+dt/2
    dp=(p_interpolate(time)-p_prio_sampling[i])/p_prio_sampling[i]
    plt.plot(data1[i]['Time'],Vstp,colors[i],linestyle='-',label='Chamber p={} mbar'.format(p_prio_sampling[i]))
#plt.ylim([0,10])
#plt.xlabel('Time (s)')
#plt.ylabel('Flow rate (l/min)')
plt.legend()
#plt.savefig('Flow rate vs time2.pdf',format='pdf')
plt.show()
plt.close()












# start time=31.957158613 from data1
# p increase is 51.695403638
# initial time is thus 51.695403638-31.957158613=
Tofset=19.738245025
def a_t(time):
    return 0.007951-0.004991*np.exp(-time/ 59.610674)



# its necesarry to run a block above first



colors=['k','k','k','g']
markers=['d','o','*','o']
Pcham=p_prio_sampling[:3]
r_sq=[]
stop=[3,3,3]
V_model=[]
times=np.array([50,100,150])-Tofset
for i in range(0,len(times)):
    V=np.array(Pcham)*a_t(times[i])
    V_model.append(V)
  
for i in range(0,len(samplesize)):   
    opt,popt=curve_fit(lin,Pcham[:stop[i]],samplesize[i][:stop[i]])  
    print(r_value(samplesize[i][:stop[i]][::-1],V_model[i][::-1]))
    

    plt.plot(Pcham,V_model[i],color='g',marker='o',linestyle='',markersize=10)
    x=np.linspace(0,200,1000)
    y_new=lin(np.array(Pcham[:stop[i]]),*opt)
    r_sq.append(round(r_value(samplesize[i][:stop[i]],y_new)**2,4))
    y_new=lin(x,*opt)
    plt.plot(x,y_new,color=colors[i],linestyle='-.',linewidth=2) #yerr is the same for all at the moment: so maybe not plotting it up? 
    plt.errorbar(Pcham[:stop[i]],samplesize[i][:stop[i]],yerr=yerr,color=colors[i],fmt=markers[i],linestyle='',markersize=10)
#plt.axhline(vmax,color='k')
plt.ylim(0,1)
plt.xlim(0,200)
plt.tick_params(axis='both', which='major', labelsize=16)
plt.ylabel('Sample amount (L$_{stp}$)',fontsize=18)
plt.xlabel('Pressure (hPa)',fontsize=18)
plt.legend()
labels=np.array(map(str,times_of_interest))#+' s'
labels=[labels[i]+' s sampling' for i in range(0,len(labels))]
labels.append('modelled $V=a(t)*p$')
handles=[]
for m,s,l in zip(markers,colors,labels):
    handles.append(matplotlib.lines.Line2D([],[],marker=m,label=l,color=s,linestyle=''))
leg=plt.legend(handles=handles,loc=2,numpoints=1,fontsize=16)
#plt.savefig('modeledobserved.pdf',format='pdf',bbox_inches='tight')
plt.show()
plt.close()





#==============================================================================
# calculate the expected resolution and sample size as a function of altitude using:
# standard atmosphere
#==============================================================================


#==============================================================================
# standard atmosphere
#==============================================================================

Tofset=19.738245025
def a_t(time):
    return 0.007951-0.004991*np.exp(-time/ 59.610674)



Pres=np.linspace(10,250,200)
Height=inverse(Pres)
times=np.array([50,100,200,1000])
fig,ax=plt.subplots(1,1)
colors=['royalblue','darkcyan','lime','k']
ax2=ax.twinx()
V=Pres*a_t(200-Tofset)
Vsample=[V[m] if V[m]<vmax else vmax for m in range(0,len(V))] 
for c,t in zip(colors,times):
        
    V=Pres*a_t(180-Tofset)
    vmax=250*2.58/1000.
    Vsample_min=[V[m] if V[m]<vmax else vmax for m in range(0,len(V))] 
    
    V=Pres*a_t(t-Tofset)
    vmax=280*2.58/1000.
    Vsample_max=[V[m] if V[m]<vmax else vmax for m in range(0,len(V))]  
    ax.plot(Vsample_max,Height/1000,color=c,linestyle='-',label='Sampling time: {}s'.format(t),linewidth=1.5)
    ax2.plot(Vsample_max,Height/1000,color=c,linestyle='-',label='Sampling time: {}s'.format(t))
        
ax.set_ylim([12,30])
ax2.set_ylim([12,30])
ax.set_ylabel('Altitude (km)',fontsize=14)
ax.set_xlabel('Sample size (L$_{stp}$)',fontsize=14)
y_tick_labels=[atsmo.Standard_atmos(i)[0]/100 for i in np.linspace(10000,30000,9)]
y_tick_labels=[round(y,1) for y in y_tick_labels]
ax.set_yticklabels(y_tick_labels)
ax2.set_ylabel('Atmospheric pressure (hPa)',fontsize=14)
#plt.yticks(np.linspace(12,30,10))
ax.legend(fontsize=14)
#f.savefig('samplesize with altitude.pdf',format='pdf',bbox_inches='tight')
plt.show()
plt.close()



#==============================================================================
# Fitting of data to get pressure int the bags as a function of chamber pressure and time:
# p_bag = Xequilibrium-A * exp(-t/Tau)
#==============================================================================
data_for_fit=[]
data_for_fit_mir=[]
ofset=[-30,-30,-30,-225]
for i in range(0,3):
     m=data[i][165:ofset[i]]
     m['Time']=[round(m['Time'][k]-m['Time'][0],9) for k in range(0,len(m['Time']))]
     m.index=[pd.to_datetime(str(int(int(m['Time'][i]/60)))+':'+str(m['Time'][i]-60*int(m['Time'][i]/60)),format='%M:%S.%f') for i in range(0,len(m['Time']))]
     data_for_fit_mir.append(m)
     m=m.resample('10S').mean()
     data_for_fit.append(m)  

optimzed=[]
optimzed_error=[]
r=[]
#del(data_for_fit[2])
#del(data_for_fit_mir[2])

Pressurevacu=np.array(p_prio_sampling)#np.delete(Pressurevac,2)
for i in range(0,len(data_for_fit)):    
    opt,popt=curve_fit(expsumfit,data_for_fit[i]['Time'],data_for_fit[i][' PressureOut'])   
    optimzed.append(opt)    
    optimzed_error.append(np.sqrt(np.diag(popt)))
    time=np.linspace(0,500,1000)    
    y_new=expsumfit(data_for_fit[i]['Time'],*opt)
    r.append(r_value(data_for_fit[i][' PressureOut'],y_new)**2)   
    plt.plot(data_for_fit[i]['Time'],data_for_fit[i][' PressureOut'],'o')
    y_new=expsumfit(time,*opt)
    plt.plot(time,y_new,'b')  
    plt.xlim(0,300)
    plt.ylim(0,800)


#==============================================================================
# Determin how parameters Xequilibrium, A , Tau depend on the ambient pressure
#==============================================================================

#==============================================================================
# Slice parameters order: 
#==============================================================================
Xequilibrium=np.array(optimzed).T[0]
A=np.array(optimzed).T[1]
Tau=np.array(optimzed).T[2]

X_err=np.array(optimzed_error).T[0]
A_err=np.array(optimzed_error).T[1]
Tau_err=np.array(optimzed_error).T[2]



Xopt,Xpopt=curve_fit(lin,Pressurevacu,Xequilibrium,sigma=X_err)
Aopt,Apopt=curve_fit(lin,Pressurevacu,A,sigma=A_err)
Topt,Tpopt=curve_fit(hyper,Pressurevacu,Tau,sigma=Tau_err)




#Xopt,Xpopt=curve_fit(lin,Pressurevacu,Xequilibrium)
#Aopt,Apopt=curve_fit(lin,Pressurevacu,A)
#Topt,Tpopt=curve_fit(hyper,Pressurevacu,Tau)




pl=np.linspace(0,1000,1000)
rs=[]  
Xmod=lin(Pressurevacu,*Xopt)
rs.append(r_value(Xequilibrium,Xmod))
Amod=lin(Pressurevacu,*Aopt)
rs.append(r_value(A,Amod))
Tmod=hyper(Pressurevacu,*Topt)
rs.append(r_value(Tau,Tmod))
fig,axes=plt.subplots(1,3,figsize=(10,4))
for i in range(0,3):
    axes[i].errorbar(Pressurevacu,np.array(optimzed).T[i],yerr=np.array(optimzed_error).T[i],fmt='o')
    axes[i].set_xlim(0,250)
    axes[i].set_xlabel('Ambient P (mbar)')
    axes[i].set_title('R$^2$ of fit: {}'.format(round(rs[i],2)))
Xmod=lin(pl,*Xopt)

Amod=lin(pl,*Aopt)

Tmod=hyper(pl,*Topt)
axes[0].plot(pl,Xmod)
axes[1].plot(pl,Amod)
axes[2].plot(pl,Tmod)
axes[0].set_ylim(0,700)
axes[1].set_ylim(0,400)
axes[2].set_ylim(0,300)
axes[0].set_ylabel('X')
axes[1].set_ylabel('A')
axes[2].set_ylabel('Tau')

fig.subplots_adjust(wspace=0.4,hspace=0.4)
#os.chdir('Processed data')
#f.savefig('Fit Parameters.pdf',format='pdf')
#os.chdir('..')


def testdp(x):#determined from other vacuum chamber expirements
    return 1.19287476*x+20.39937129
Xmod=lin(Pressurevacu,*Xopt)

Amod=lin(Pressurevacu,*Aopt)
Test=Xmod-Amod
Test2=testdp(Pressurevacu)
#plt.plot(Test,Test2)
r_value(Test2,Test)**2

def pres_bag(p,time):
    x=lin(p,*Xopt)
    a=lin(p,*Aopt)
    t=hyper(p,*Topt)
    pres_bag=expsumfit(time,x,a,t)
    return pres_bag

def pres_bag_inv(p_bag,p):
    x=lin(p,*Xopt)
    a=lin(p,*Aopt)
    t=hyper(p,*Topt)
    time=-t*np.log((x-p_bag)/a)
    return time    
#%%   
pl=np.linspace(0,300,5000)


for i in range(0,len(Pressurevacu)):
    p=pres_bag(Pressurevacu[i],data_for_fit[i]['Time'])
    plt.plot(data_for_fit[i]['Time'],p,color='b')
    plt.plot(data_for_fit[i]['Time'],data_for_fit[i][' PressureOut'],'r') 
    plt.plot(data_for_fit_mir[i]['Time'],data_for_fit_mir[i][' PressureOut'],'r')
    print(r_value(data_for_fit[i][' PressureOut'],p)**2)
        
    p=pres_bag(Pressurevacu[i],pl)
    plt.plot(pl,p,'b')    
plt.xlabel('Time (s)',fontsize=14)
plt.ylabel('P in sampling bag',fontsize=14)
handles=[]
labels=['Model fit','observed']
colors=['b','r']
for l,c in zip(labels,colors):
    handles.append(matplotlib.lines.Line2D([],[],color=c,label=l,linestyle='-'))
plt.legend(handles=handles)
#os.chdir('Processed data')
#plt.savefig('model vs obs.pdf',format='pdf')
plt.show()
plt.close()
#os.chdir('..')

pl=np.linspace(0,300,5000)
x=np.linspace(20,1000,25)

for i in range(0,len(x)):
#    p=pres_bag(x[i],data2[i]['Time'])
#    plt.plot(data2[i]['Time'],p,color='b')
#    plt.plot(data2[i]['Time'],data2[i][' PressureOut'],'r') 
    p=pres_bag(x[i],pl)
    plt.plot(pl,p)







