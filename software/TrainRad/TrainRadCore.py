#/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Define a dicionary containg flight info 
#
# import TrainRadCore as TRC
import pandas as pd
from datetime import datetime
from glob import glob
from scipy.interpolate import interp1d
import Barometric 
import numpy as np
import scantools 
import config
import matplotlib.pyplot as plt 

joint_sets=[["001", "002"], ["003","004","005"], ["006","007","008"], ["009","010","011"], ["012","013","014"], ["015","016","017"], ["018","019","020"], ["021","022","023"], ["024","025","026"]]

def find_set(key):
    """TODO: Docstring for find_set.
    Returns
    -------
    TODO
    """
    for sets in joint_sets:
        if key in sets:
            break 
    return sets

LaunchTime = { "001":"10:47:00",
        "002":"10:49:00",
        "003":"08:13:00",
        "004":"08:16:00",
        "005":"08:28:00",
        "006":"09:25:00",
        "007":"09:27:00",
        "008":"09:29:00",
        "009":"08:25:00",
        "010":"08:27:00",
        "011":"08:28:00",
        "012":"12:28:00",
        "013":"12:30:00",
        "014":"12:30:00",
        "015":"07:59:00",
        "016":"08:00:00",
        "017":"08:00:00",
        "018":"10:39:00",
        "019":"10:41:00",
        "020":"10:43:00",
        "021":"07:05:00",
        "022":"07:05:00",
        "023":"07:08:00",
        "024":"08:08:00",
        "025":"08:10:00",
        "026":"08:11:00",
}

flight_files={"001":"AC_TRN_RINGO_20190611_001.mto",
"002":"AC_TRN_RINGO_20190611_002.mto",
"003":"AC_TRN_RINGO_20190612_003.mto",
"004":"AC_TRN_RINGO_20190612_004.mto",
"005":"AC_TRN_RINGO_20190612_005.mto",
"006":"AC_TRN_RINGO_20190616_006.mto",
"007":"AC_TRN_RINGO_20190616_007.mto",
"008":"AC_TRN_RINGO_20190616_008.mto",
"009":"AC_TRN_RINGO_20190617_009.mto",
"010":"AC_TRN_RINGO_20190617_010.mto",
"011":"AC_TRN_RINGO_20190617_011.mto",
"012":"AC_TRN_RINGO_20190617_012.mto",
"013":"AC_TRN_RINGO_20190617_013.mto",
"014":"AC_TRN_RINGO_20190617_014.mto",
"015":"AC_TRN_RINGO_20190618_015.mto",
"016":"AC_TRN_RINGO_20190618_016.mto",
"017":"AC_TRN_RINGO_20190618_017.mto",
"018":"AC_TRN_RINGO_20190618_018.mto",
"019":"AC_TRN_RINGO_20190618_019.mto",
"020":"AC_TRN_RINGO_20190618_020.mto",
"021":"AC_TRN_RINGO_20190620_021.mto",
"022":"AC_TRN_RINGO_20190620_022.mto",
"023":"AC_TRN_RINGO_20190620_023.mto",
"024":"AC_TRN_RINGO_20190621_024.mto",
"025":"AC_TRN_RINGO_20190621_025.mto",
"026":"AC_TRN_RINGO_20190621_026.mto"}

GroundPressure = {
        "001":996.50381514256 ,
        "002":996.50381514256 ,
        "003":994.458188906499,
        "004":994.458188906499,
        "005":994.458188906499,
        "006":1007.38096498539,
        "007":1007.38096498539,
        "008":1007.38096498539,
        "009":1004.33190733574,
        "010":1004.33190733574,
        "011":1004.33190733574,
        "012":1002.74253112867,
        "013":1002.74253112867,
        "014":1002.74253112867,
        "015":998.520942387699,
        "016":998.520942387699,
        "017":998.520942387699,
        "018":997.187980336404,
        "019":997.187980336404,
        "020":997.187980336404,
        "021":999.905061318157,
        "022":999.905061318157,
        "023":999.905061318157,
        "024":1004.98737136217,
        "025":1004.98737136217,
        "026":1004.98737136217,
}

def pdPrepend(dat):
    df=dat.copy().drop(list(range(1,len(dat))))
    df.iloc[0]=np.nan
      
    
    dat=df.append(dat).reset_index()
    return dat

def date_to_seconds(year,month,day,hour=0,minutes=0,seconds=0):
    """TODO: Docstring for date_to_day.
    :returns: TODO

    """

    seconds_since=(datetime(year,month,day,hour,minutes,seconds)-datetime(2000,1,1,0,0,0)).total_seconds()
    return seconds_since

def Met_seconds(Date):
    time_s=[]
    for d in Date:
        date,time=d.split(' ')
         
        year,month,day=date.split('-')
        hour,minutes,seconds=time.split(':')
        time_s.append(date_to_seconds(int(year),int(month),int(day),int(hour),int(minutes),int(seconds)))
    return time_s

def readData(path_to_data):
    dat=pd.read_csv(path_to_data,sep=' ') 
    dat['DateTime']=pd.to_datetime(dat["Date"]+' '+dat['Time'],format='%Y-%m-%d %H:%M:%S')
    return dat 


def removeDuplicates(dat):
    duplicates=[]
    for i in range(len(dat)-1):
        if (dat['Alt'][i]==dat['Alt'][i+1])&(dat['RH'][i]==dat['RH'][i+1])&(dat['T'][i]==dat['T'][i+1]):
            # we keep the first encounter
            duplicates.append(i+1)
    dat=dat.drop(duplicates)
    dat=dat.reset_index(drop=True) 
    # print("Found %d duplicates. Kept the first occurance." % len(duplicates))
    return dat
# Determined from https://www.daftlogic.com/sandbox-google-maps-find-altitude.htm
# on 2020-06-18 10:30:49

StationAltitude=134
minspeed=4

def findtouchdown_fromSpeed(data):
    dat=data.copy()
    w=np.diff(dat['Alt'])/np.diff(Met_seconds(dat["Date"]+' '+dat['Time']))
    if (all([(np.abs(w[-10+j])>=3) for j in range(10)])):
        print("No  touchdown yet\nNothing will be done to the data") 
    else:
        for i in list(range(len(w)))[::-1]:
            if all([(np.abs(w[i-j])>=3) for j in range(10)]):
                i=i
                break
        if ((dat["DateTime"][i+2]-dat["DateTime"][i+1]).total_seconds()==1):
            ii=i+1
            # print("index = %d" % ii)
            # print(w[i+1-10:i+1])
            a=list(range(i+2,len(dat['Alt'])))
            dat=dat.drop(a)
            
        else:
            i+=1
            # print(w[i-10:i])
            meanspeed=np.mean(w[i-10:i+1])
            stdspeed=np.std(w[i-10:i+1])
            try:
                dat_mean=dat.iloc[i+1:i+11].mean().to_frame().T
            except IndexError:
                dat_mean=dat.iloc[i+1:].mean().to_frame().T
            if len(dat[i+1:])<10:
                N=len(dat[i+1:])
            else:
                N=10
            # print(len(dat))
            meanAltitude=dat_mean.loc[0,'Alt']
            # print("Mean speed: %.3f stdev %.3f, N=%d" % (meanspeed,stdspeed,N))

            dt=pd.to_timedelta(round(((dat['Alt'][i]-meanAltitude)/meanspeed)),unit='s')
            if dt.total_seconds()==0:
                dt=pd.to_timedelta(1,unit='s')
            
            t=dat["DateTime"][i]-dt

            a=list(range(i+1,len(dat['Alt'])))
             
            dat_mean['T']  = find_non_nan(dat['T'],i)
            dat_mean['RH'] = find_non_nan(dat['RH'],i)
            dat_mean['Lat']= find_non_nan(dat['Lat'],i)
            dat_mean['Lon']= find_non_nan(dat['Lon'],i)
            # print(dat_mean['RH'])
            dat=dat.drop(a)
            dat_mean['flagAlt']='MEAN'
            dat_mean['DateTime']=t 
            dat_mean['Time']=str(t.time()) 
            dat_mean['Date']=dat["Date"][1]
            
            dat=dat.append(dat_mean)
            # print(dat.iloc[-1])
    return dat

def find_non_nan(dataset,a):
    val=np.nan
    b=a+1
    while np.isnan(val):
        val=np.nanmean(dataset.iloc[a:b])
        b+=1
    return val
def findLaunch_fromSpeed(dat):
    w=np.diff(dat['Alt'])/np.diff(Met_seconds(dat["Date"]+' '+dat['Time']))
    for i in range(len(w)):
        if all([(np.abs(w[i+j])>=minspeed) for j in range(10)]):
            # print(w[i:i+10])
            if (i>0):
                if ((dat["DateTime"][i]-dat["DateTime"][i-1]).total_seconds()==1)&(dat['Alt'][i]<145):
                    cut=i-1
                    a=list(range(cut))
                    dat=dat.drop(a)
                    dat=dat.reset_index(drop=True) 
                
                else:
                    cut=i
                    # print("Launch occured before data was collected\nor long time between launch and data collection")
                    
                    meanspeed=np.mean(w[i:i+10])
                    stdspeed=np.std(w[i:i+10])
                    # print("Mean speed: %.3f stdev %.3f, N=10" % (meanspeed,stdspeed))
                    dt=pd.to_timedelta(round(((dat['Alt'][i]-StationAltitude)/meanspeed)),unit='s')
                    if dt.total_seconds()==0:
                        dt=pd.to_timedelta(1,unit='s')
                    
                    t=dat["DateTime"][i]-dt
                    a=list(range(cut))
                    dat=dat.drop(a)
                    dat=dat.reset_index(drop=True) 
                    # print(t)
                    dat=pdPrepend(dat)
                    dat.loc[0,'Alt']=StationAltitude
                    dat.loc[0,'flagAlt']='SAS'
                    dat.loc[0,'DateTime']=t 
                    dat.loc[0,'Time']=str(t.time()) 
                    dat.loc[0,'Date']=dat["Date"][1]
            else:
                # print("Launch occured before data was collected\nor long time between launch and data collection")
                
                meanspeed=np.mean(w[i:i+10])
                stdspeed=np.std(w[i:i+10])
                # print("Mean speed: %.3f stdev %.3f, N=10" % (meanspeed,stdspeed))
                dt=pd.to_timedelta(round(((dat['Alt'][i]-StationAltitude)/meanspeed)),unit='s')
                if dt.total_seconds()==0:
                    dt=pd.to_timedelta(1,unit='s')

                t=dat["DateTime"][0]-dt
                # print("dt = %.3f" % int(dt.total_seconds()))
                # print(t)
                dat=pdPrepend(dat)
                dat.loc[0,'Alt']=StationAltitude
                dat.loc[0,'flagAlt']='SAS'
                dat.loc[0,'DateTime']=t 
                dat.loc[0,'Time']=str(t.time()) 
                dat.loc[0,'Date']=dat["Date"][1]
            break
    return dat

def findLaunch(dat,i):
    fln=i.split('_')[-1].split('.')[0] 
    t=LaunchTime[fln]
    t=pd.to_datetime(dat["Date"][1]+' '+str(t),format='%Y-%m-%d %H:%M:%S')
    for i in range(len(dat)):

        if (dat["DateTime"][i].time()>=t.time()):
            if i!=0:
                if (dat["DateTime"][i]-t).total_seconds()==0:
                    cut=i            
                    a=list(range(cut))
                    dat=dat.drop(a)
                    dat=dat.reset_index(drop=True) 
                elif (t-dat["DateTime"][i-1]).total_seconds()<=2:
                    cut=i            
                    a=list(range(cut))
                    dat=dat.drop(a)
                    dat=dat.reset_index(drop=True) 
                else:
                    cut=i            
                    a=list(range(cut))
                    dat=dat.drop(a)
                    dat=dat.reset_index(drop=True) 
                    dat=pdPrepend(dat)
                    dat['Alt'].iloc[0]=StationAltitude
                    dat['flagAlt'].iloc[0]='SA'
                    dat['DateTime'].iloc[0]=t
                    dat['Time'].iloc[0]=str(t.time()) 
                    dat['Date'].iloc[0]=dat["Date"][1]
                break
            else:
                dat=pdPrepend(dat)
                dat['Alt'].iloc[0]=StationAltitude
                dat['flagAlt'].iloc[0]='SA'
                dat['DateTime'].iloc[0]=t 
                dat['Time'].iloc[0]=str(t.time()) 
                dat['Date'].iloc[0]=dat["Date"][1]
                break
    return dat

def LoadData(filename):
    '''
    This loads the data mto of filename, from were Trainou data is located. 
    '''
    dateflight=filename.split('/')[-1].split('_')[3]+'_'+filename.split('/')[-1].split('_')[4].split('.')[0]  
    dat=readData(filename)
    dat=removeDuplicates(dat)
    S_2000=Met_seconds(dat["Date"]+' '+dat['Time'])
    dat.insert(loc=0, column='time_s', value=np.array(S_2000)-S_2000[0])
    return dat

def LoadDataAll():
    '''
    This loads all the data, from were Trainou data is located. 
    '''
    TrainData={}
    # count=1
    for filename in glob('/home/joram/research/data/TrainRad/*.mto'):
        datefligt=filename.split('/')[-1].split('_')[3]+'_'+filename.split('/')[-1].split('_')[4].split('.')[0]  
        TrainData[datefligt]=LoadData(filename)
        # if count==1:
        #     break
# "Date" "Time" "T" "RH" "DP" "Esat" "Tin" "Batt" "Alt" "WindSpeed" "WindDir" "VertSpeed" "Lat" "Lon" "sat" "SN" "P"
# 2019-06-11 09:59:22 20.2 40 6.17 23.65 32 6.1 135 0 270 -0.1 47.97429 2.09227 8 "021A922A2F" 994.817
    return TrainData

def fixFrequency(dat):
    new_index=list(range(int(dat['time_s'].iloc[-1])))
    df=pd.DataFrame()
    df['time_s']=new_index
    df=df.merge(dat,how="outer",on='time_s')
    df.loc[:,'Alt']=df['Alt'].interpolate()
    # df=df.resample('2S').nanmean()
    return df  

def filMethodInterpolate(data):
    dat=data.copy()
    dat.loc[:,'T']=dat['T'].interpolate()
    dat.loc[:,'RH']=dat['RH'].interpolate()
    # dat['Lat'].iloc[:]=dat['Lat'].interpolate()
    # dat['Lon'].iloc[:]=dat['Lon'].interpolate()
    return dat
maxgap=5

def fil_small_gaps(dat):
    """TODO: Docstring for fil_small_gaps.

    Parameters
    ----------
    arg1 : TODO

    Returns
    -------
    TODO

    """
    dat.loc[:,'T']=scantools.fill_df(dat['T'],limit=maxgap)
    dat.loc[:,'RH']=scantools.fill_df(dat['RH'],limit=maxgap)
    
    return dat

def filMethodStealFrom(data,otherdat,key,force=False):
    dat=data.copy()
    gapsel=np.isnan(dat[key])
    startdescent=dat['Alt'].idxmax()
    int_values=np.array([])
    inthegaps=[]
    # print('before',len(dat[np.isfinite(dat[key])]))
    for i in range(len(gapsel)):
        if (gapsel[i]==True)&(i not in inthegaps):
            for j in range(i+1,len(gapsel)):
                inthegaps.append(j)
                if gapsel[j]==False:
                    # print("%d till %d" % (gapleftbound,gaprighbound))
                    break
            alt=np.array(dat['Alt'][i:j])
            if i<=startdescent:
                top=otherdat['Alt'].idxmax()
                a=otherdat['Alt'][:top+1]
                t=otherdat[key][:top+1]
                if force==True:
                   mask=(np.isfinite(a)&np.isfinite(t))
                   a= a[mask]
                   t= t[mask]
                   if len(a)>=2:
                       halp=interp1d(a,t,bounds_error=False,fill_value=np.nan)(alt)
                   else:
                       halp=np.array([np.nan]*len(alt))
                   int_values=np.concatenate((int_values,halp))
            
                else:
                    if all(np.isfinite(t[((a>=alt[0])&(a<=alt[-1]))])):
                        int_values=np.concatenate((int_values,interp1d(a,t,bounds_error=False,fill_value=np.nan)(alt)))
                    else:
                        int_values=np.concatenate((int_values,np.array([np.nan]*len(alt))))
            else:
                top=otherdat['Alt'].idxmax()
                a=otherdat['Alt'][top+1:]
                t=otherdat[key][top+1:]
                if force==True:
                   mask=(np.isfinite(a)&np.isfinite(t))
                   a= a[mask]
                   t= t[mask]
                   if len(a)>=2:
                       int_values=np.concatenate((int_values,interp1d(a,t,bounds_error=False,fill_value=np.nan)(alt)))
                   else:
                       int_values=np.concatenate((int_values,np.array([np.nan]*len(alt))))
                else:
                    if all(np.isfinite(t[((a<=alt[0])&(a>=alt[-1]))])):
                        int_values=np.concatenate((int_values,interp1d(a,t,bounds_error=False,fill_value=np.nan)(alt)))
                    else:
                        int_values=np.concatenate((int_values,np.array([np.nan]*len(alt))))
    dat.loc[gapsel,key]=int_values
    # print('after' ,len(dat[np.isfinite(dat[key])]))
    # dat['RH'].loc[gapsel]=rh_int
    # Still interpolate location. 
    return dat

def processMet(dat):
    T_b=np.nanmean(dat['T'].iloc[0:10])
    RH_b=np.nanmean(dat['RH'].iloc[0:10])
    Lat_b=np.nanmean(dat['Lat'].iloc[0:10])
    Lon_b=np.nanmean(dat['Lon'].iloc[0:10])

    dat['flagAlt']=['O']*len(dat)
    dat=findLaunch_fromSpeed(dat)
    dat=findtouchdown_fromSpeed(dat)

    # dat=findLaunch(dat,i)
    S_2000=Met_seconds(dat["Date"]+' '+dat['Time'])
    dat.loc[:,'time_s']=np.array(S_2000)-S_2000[0]
    dat=fixFrequency(dat)
    T_l=dat['T'].iloc[-1]
    rh_l=dat['RH'].iloc[-1]     

    dat.loc[([not a for a in scantools.moving_average_outlier_detection(dat['T'],10,strict_factor=5 )]),'T']=np.nan
    dat.loc[([not a for a in  scantools.moving_average_outlier_detection(dat['RH'],10,strict_factor=5 )]),'RH']=np.nan

    dat.loc[(dat['RH']>100),'RH']=np.nan
    dat.loc[(dat['T']<-60),'T']=np.nan
    dat.loc[dat.index[-1],'T']=T_l
    dat.loc[dat.index[-1],'RH']=rh_l
    
    dat.loc[0,'T']=T_b
    dat.loc[0,'RH']=RH_b
    dat.loc[0,'Lat']=Lat_b
    dat.loc[0,'Lon']=Lon_b

    if np.isnan(dat['T'].iloc[-1]):
        fillastval(dat,'T') 
    if np.isnan(dat['RH'].iloc[-1]):
        fillastval(dat,'RH') 
    # print(dat['T'].iloc[-1])
    t=[dat['DateTime'].iloc[0]+pd.Timedelta(s,'S') for s in dat['time_s']]
    # print(t==dat['DateTime'])
    # Fill up necessiry components already
    dat.loc[:,'DateTime']=t
    dat.loc[(pd.isnull(dat['Date'])),'Date']=[t.strftime("%Y-%m-%d") for t in dat['DateTime'].loc[(pd.isnull(dat['Date']))]]
    dat.loc[(pd.isnull(dat['Time'])),'Time']=[t.strftime("%H:%M:%S") for t in dat['DateTime'].loc[(pd.isnull(dat['Time']))]]
    dat=fil_small_gaps(dat)
    dat.loc[:,'Lat']=dat['Lat'].interpolate()
    dat.loc[:,'Lon']=dat['Lon'].interpolate()
    dat['GeopotH']=Barometric.heigth_to_geopotH(dat["Alt"],dat["Lat"]) 
    # dat['Gamma']=Barometric.GammaFromZ(dat["Alt"],dat["Lat"])
    # print(dat.iloc[0])
    # print(dat.iloc[-1])
    

    # dat=filMethodInterpolate(dat)
    return dat

def fillastval(dat,key):
    top=dat['Alt'].idxmax()
    y=np.array(dat[key].iloc[:top])
    mask=np.isfinite(y)
    x=np.array(dat['Alt'].iloc[:top])[mask]
    y=y[mask]
    # print(dat['Alt'].iloc[:top][0])
    dat.loc[dat.index[-1],key]=interp1d(x,y)(dat['Alt'].iloc[-1])
    return 

def fil(dat,otherdat=None,method="steal",**kwargs):
    if method=="steal":
        data=filMethodStealFrom(dat,otherdat,'T',**kwargs)
        data=filMethodStealFrom(data,otherdat,'RH',**kwargs)
    elif method=="interpolate":
        data=filMethodInterpolate(dat)

    # homogonise data
    data.loc[:,'Lat']=data['Lat'].interpolate()
    data.loc[:,'Lon']=data['Lon'].interpolate()
    return data

def computerPressure(data,key):
    # require data at launch 
    dat=data.copy()
    dat.loc[:,'P']=np.nan
    mask=(np.isfinite(dat['T'])&np.isfinite(dat['GeopotH'])&np.isfinite(dat['RH']))
    T       = np.array(dat [ 'T']     [mask ]     )+273.15
    RH      = np.array(dat [ 'RH']    [mask ]    )
    Zgeopot = np.array(dat [ 'GeopotH']   [mask ])
    P0=GroundPressure[key]
    p=Barometric.barometric_p(T,RH,Zgeopot,P0)
    dat.loc[mask,'P']=np.array(p,dtype=np.float64)
    return dat 

def plot_split_asde(xdata,ydata,axas,axde,**kwargs):
    top=ydata.idxmax()
    scantools.plot_add(axas,np.array(xdata.iloc[:top]),np.array(ydata.iloc[:top]),**kwargs)
    scantools.plot_add(axde,np.array(xdata.iloc[top:]),np.array(ydata.iloc[top:]),**kwargs)
    return

def plot_results(data,axes_array,**kwargs):
    plot_split_asde(data['T']+273.15,data['Alt'],axes_array[0,0],axes_array[0,1],**kwargs)
    plot_split_asde(data['RH'],data['Alt'],axes_array[1,0],axes_array[1,1],**kwargs)
    plot_split_asde(data['P'],data['Alt'],axes_array[2,0],axes_array[2,1],**kwargs)
    return
def plot_raw(data):
    xlabs=['T (K)','T (K)','RH','RH']
    ylabs=['z']*4
    xlims=[(210,310), (210,310),(-1,100),(-1 ,100)]
    ylims=[(0,35000)]*4
    fig,axes=scantools.plot_init(2,2,xlabs=xlabs,ylabs=ylabs,xlims=xlims,ylims=ylims)
    top=data['Alt'].idxmax()
    
    scantools.plot_add(axes[0,0],data['T'].iloc[:top]+273.15,data['Alt'].iloc[:top] , marker='o',linestyle='',color=config.GruvBoxColors[0],argsort=False)
    scantools.plot_add(axes[0,1],data['T'].iloc[top:]+273.15,data['Alt'].iloc[top:] , marker='o',linestyle='',color=config.GruvBoxColors[0],argsort=False)
    scantools.plot_add(axes[1,0],data['RH'].iloc[:top],data['Alt'].iloc[:top] , marker='o',linestyle='',color=config.GruvBoxColors[0],argsort=False)
    scantools.plot_add(axes[1,1],data['RH'].iloc[top:],data['Alt'].iloc[top:] , marker='o',linestyle='',color=config.GruvBoxColors[0],argsort=False)
    
    plt.show()
    return

def plot_comp(data,data_raw,key):
    xlabs=['T (K)','T (K)','RH','RH']
    ylabs=['z']*4
    xlims=[(210,310), (210,310),(-1,100),(-1 ,100)]
    ylims=[(0,35000)]*4
    fig,axes=scantools.plot_init(2,2,xlabs=xlabs,ylabs=ylabs,xlims=xlims,ylims=ylims)
    top_r=data_raw['Alt'].idxmax()
    top=data['Alt'].idxmax()
    
    scantools.plot_add(axes[0,0],data_raw['T'].iloc[:top_r]+273.15,data_raw['Alt'].iloc[:top_r] , marker='d',linestyle='',color=config.GruvBoxColors[2],argsort=False)
    scantools.plot_add(axes[0,0],data['T'].iloc[:top]+273.15,data['Alt'].iloc[:top] , marker='o',linestyle='',color=config.GruvBoxColors[0],argsort=False)
    
    scantools.plot_add(axes[0,1],data_raw['T'].iloc[top_r:]+273.15,data_raw['Alt'].iloc[top_r:] , marker='d',linestyle='',color=config.GruvBoxColors[2],argsort=False)
    scantools.plot_add(axes[0,1],data['T'].iloc[top:]+273.15,data['Alt'].iloc[top:] , marker='o',linestyle='',color=config.GruvBoxColors[0],argsort=False)
    
    scantools.plot_add(axes[1,0],data_raw['RH'].iloc[:top_r],data_raw['Alt'].iloc[:top_r] , marker='d',linestyle='',color=config.GruvBoxColors[2],argsort=False)
    scantools.plot_add(axes[1,0],data['RH'].iloc[:top],data['Alt'].iloc[:top] , marker='o',linestyle='',color=config.GruvBoxColors[0],argsort=False)
    
    scantools.plot_add(axes[1,1],data_raw['RH'].iloc[top_r:],data_raw['Alt'].iloc[top_r:] , marker='d',linestyle='',color=config.GruvBoxColors[2],argsort=False)
    scantools.plot_add(axes[1,1],data['RH'].iloc[top:],data['Alt'].iloc[top:] , marker='o',linestyle='',color=config.GruvBoxColors[0],argsort=False)
    
    # scantools.plot_add(axes,data2['T']+273.15,data2['Alt'] , marker='d',linestyle='-',color=config.GruvBoxColors[1],argsort=False)
    # scantools.plot_add(axes,data3['T']+273.15,data3['Alt'] , marker='*',linestyle='-',color=config.GruvBoxColors[2],argsort=False)
    # scantools.plot_add(axes,data1_23['T']+273.15,data1_23['Alt'],marker='>',linestyle='-',color=config.GruvBoxColors[3],argsort=False)
    # scantools.plot_add(axes,data1_32['T']+273.15,data1_32['Alt'],marker='v',linestyle='-',color=config.GruvBoxColors[4],argsort=False)
    fig.tight_layout()
    fig.savefig('%s_raw_vs_clean.pdf' % key )
    return

def save_as_tsv(data,fname):
    """TODO: Docstring for save_as_tsv.
    Returns
    -------
    TODO

    """
    desired_keys=['time', 'Pscl', 'T', 'RH', 'v', 'u', 'Height', 'P', 'TD',
           'MR', 'DD', 'FF', 'AZ', 'El', 'Range', 'Lon', 'Lat', 'SpuKey',
           'UsrKey', 'RadarH']
    
    
    fil_value=-32768.00

    Headerstring='''
    Converted from imet to match Vaisala RS format
    
    Information about sounding:
    ==================================
    
    Ignore: Station:                  xxxx
    Ignore: Launch time:              {0}
    Ignore: RS type:                  {rstype}
    Ignore: RS number:                
    Ignore: Reason for termination:   Manual stop
    Ignore: Sounding SW version:      MW31 3.66.0
    
    Ignore: PTU calculations in research mode
    
    ==================================
    
    
    Information about map: FLEDT               
    ==================================
    
    
       Record name:    Unit:           Data type:          Divisor: Offset:
       ---------------------------------------------------------------------
        time            sec             float (4)          1        0       
        Pscl            ln scaled       float (4)          1        0       
        T               K               float (4)          1        0       
        RH              %               float (4)          1        0       
        v               m/s             float (4)          -1       0       
        u               m/s             float (4)          -1       0       
        Height          m               float (4)          1        0       
        P               hPa             float (4)          1        0       
        TD              K               float (4)          1        0       
        MR              g/kg            float (4)          1        0       
        DD              dgr             float (4)          1        0       
        FF              m/s             float (4)          1        0       
        AZ              dgr             float (4)          1        0       
        El              dgr             float (4)          1        0       
        Range           m               float (4)          1        0       
        Lon             dgr             float (4)          1        0       
        Lat             dgr             float (4)          1        0       
        SpuKey          bitfield        unsigned short (2) 1        0       
        UsrKey          bitfield        unsigned short (2) 1        0       
        RadarH          m               float (4)          1        0       
    
    *************************************************************************************************\n'''.format('{}',rstype='m10')
    
    date=data['Date'][0]
    index=len(data)
    new=pd.DataFrame(index=[i for i in range(0,index)],columns=desired_keys)
    new=new.fillna(fil_value)
     
    new.loc[:,'Lat']=data['Lat']
    new.loc[:,'Lon']=data['Lon']
    new.loc[:,'Height']=data['Alt']
    total_seconds=[int(data['Time'][i].split(':')[0])*3600+int(data['Time'][i].split(':')[1])*60+int(data['Time'][i].split(':')[2]) for i in range(0,index)]
    new.loc[:,'time']=np.array(total_seconds)-total_seconds[0]
    new.loc[:,'P']=data['P']
    new.loc[:,'T']=data['T']+273.15
    new.loc[:,'RH']=data['RH']
    md=np.deg2rad(270-data['WindDir'])
    new.loc[:,'v']=data['WindSpeed']*np.sin(md)
    new.loc[:,'u']=data['WindSpeed']*np.cos(md)
    date+=' '+data['Time'][0]       #original was: 13:22:45 should we shift? lets wait and see. 
    # print(date)
    date+=' UTC'
    
    with open(fname+'.tsv','w') as fobj:
        fobj.write(Headerstring.format(date))
        new.to_csv(fobj,'\t',index=False)
        fobj.close()
    return
