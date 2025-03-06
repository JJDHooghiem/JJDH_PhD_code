# -*- coding: utf-8 -*-
"""
Created on Wed Nov 29 15:06:59 2017

@author: Joram
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from glob import glob
import ScAn.config as config
from datetime import datetime
def get_flow_rates():
    """
    Obtains the mean flow rate during IRMS sampling from LISA samples. 
    """
    filelist=glob('/home/joram/research/data/LISA_CO_Measurements/2017_Flow_corrections/*')
    m=[]
    for f in filelist:
        if f.endswith('.txt'):
            m.append(f)
    filelist=m
    del(m)
    #%%
    flowrates_all=[]
    for f in filelist:
        logfile=open(f,'r')
        logfile_striped=[]
        stored_log_files=[]
        u=10
        for line in logfile:
            s=line.rstrip()
            s=s.split('\t') 
            if u==0:
                u+=1
            if len(s)>1:
                if s[1]== 'V_PUMP CLOSE':
                    u=0    
            if u==1 and len(s)==5:
            
                df=[s[0]]
                df.extend(map(float,s[1:]))
                df.append(f)
                logfile_striped.append(df)
            if len(s)>1:
                if s[1]=='MV6 CLOSE':
                    u=10
                    if logfile_striped: 
                        stored_log_files.append(logfile_striped)
                    logfile_striped=[]
                    
        flowrates=[]
        counter=1
        for log_file in stored_log_files:
            log_file_frame=pd.DataFrame(log_file,columns=['TimeStamp','Pressure','Flow_rate','MFCSET','MPV_Pos','Name_log_file'])
            if log_file_frame['MPV_Pos'][0]==6:        
                # plt.plot(range(len(log_file_frame['Flow_rate'])),log_file_frame['Flow_rate'],'o')
                flowrate=[]
                mean_flow=np.nanmean(log_file_frame['Flow_rate'])
                flowrate.append(mean_flow)
                flowrate.append(f.split('logfile_')[1].split('.')[0])
                flowrate.append(counter)
                counter+=1
                flowrate.append(log_file_frame['TimeStamp'][0])
                flowrates.append(flowrate)
        flowrates_all.extend(np.array(flowrates))
    # plt.ylabel('Flow')
    # plt.xlabel('Time')
    # plt.savefig(config.FigDir+'COIRMS_Flow.pdf')
    flowrates_all=pd.DataFrame(flowrates_all,columns=['Flow_rate','Name_log_file','Measurement no','StartM'])
    flightDate=[]
    presLev=[]
    mesNo=[]
    for name,no in zip(flowrates_all['Name_log_file'],flowrates_all['Measurement no']):
        s=name.split('hPa')
        p=s[0].replace('_','')
        if p+s[1].split('_')[0]=='1502':
            mesNo.append(int(3))
        else:
            mesNo.append(int(no))
        presLev.append(int(p))
        s=s[-1].split('_')[-3:]
        flightDate.append(pd.to_datetime(s[0]+s[1]+s[2], format="%Y%m%d").date())
    flowrates_all['flightDate']=flightDate
    flowrates_all['presLev']=presLev
    flowrates_all['mesNo']=mesNo
    return flowrates_all 

def get_calcyl_co_data():
    """
    loads the CO irms calibration data into a pandas datafrime and adds a timestamp column
    """
    cyl_data=pd.read_csv('/home/joram/research/data/LISA_CO_Measurements/CalCylinderMeasurements.csv')
    cyl_data['Datetime']=pd.to_datetime(cyl_data['Datetime '],format="%d/%b/%y %H:%M")
    cyl_data['times']=ts2t(cyl_data['Datetime'])
    return cyl_data

def ts2t(timestamps):
    """
    Computes the amount of seconds elapsed since a 1 1 1970
    """
    times=[(t-datetime(1970,1,1)).total_seconds() for t in timestamps]
    return times

def get_irms_co_data():
    """
    loads the CO irms data into a pandas datafrime and adds a timestamp column
    """
    
    lisa_data=pd.read_csv('/home/joram/research/data/LISA_CO_Measurements/LisaCOallCALIBRATED.csv')

    lisa_data['Datetime']=pd.to_datetime(lisa_data['Datetime'],format="%d/%b/%y %H:%M")
    lisa_data['times']=ts2t(lisa_data['Datetime'])
    flightDate=[]
    presLev=[]
    mesNo=[]
    for val in lisa_data['FileHeader: Filename']:
        s=val.split('Sod_Strat_')[-1].split('_')
        # 26_Apr_2017_200hPa_1_V6_20F_300S_14900_0_1.dxf
        flightDate.append(pd.to_datetime(s[0]+s[1]+s[2], format="%d%b%Y").date())
        presLev.append(int(s[3].split('h')[0]))
        mesNo.append(int(s[4]))
    lisa_data['flightDate']=flightDate
    lisa_data['presLev']=presLev
    lisa_data['mesNo']=mesNo
    frates=[]
    flowrates=get_flow_rates()
    for dv,pv,nv in zip(lisa_data['flightDate'],lisa_data['presLev'],lisa_data['mesNo']):
        for f,d,p,n in zip(flowrates['Flow_rate'],flowrates['flightDate'], flowrates['presLev'], flowrates['mesNo']):

            if ( dv==d )&(pv==p)&(nv==n):
                frates.append(float(f))
                break
    lisa_data['Flow_rate']=np.array(frates)
    lisa_data['COfcor']=(20/lisa_data['Flow_rate'])*lisa_data['CO ppb']

    return lisa_data
