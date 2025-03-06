import colisalib
import matplotlib.pyplot as plt
import numpy as np
import lodautil
import matplotlib
import pandas as pd
import ScAn.stico as stico
matplotlib.use('Qt5Agg')
matplotlib.rc('text',usetex=False)
import colisalib
dataLISA=lodautil.LISA_load()
dataLISA=stico.check_COstab(dataLISA)
data=colisalib.get_flow_rates()

values=colisalib.get_irms_co_data()
datasets={}
for date in np.unique(values['flightDate']):
    data=values[(values['flightDate']==date)]
    data_f=[float(a) for a in data['Flow_rate'][(data['mesNo']==1)]]
    data_co=data['COfcor'][(data['mesNo']==1)]
    data_t=data['Datetime'][(data['mesNo']==1)]
    data_p=data['presLev'][(data['mesNo']==1)]
    data_p,data_t,data_co,data_f=zip(*sorted(zip(data_p,data_t,data_co,data_f)))
    datamean=data.groupby('presLev').mean()
    datastd=data.groupby('presLev').std()
    datamean['Datetime']=data_t
    datamean['CO']=np.round(data_co,2)
    datamean['13C']=np.round(datamean['13C'],2)
    datamean['18O']=np.round(datamean['18O'],2)
    datamean['13C std']=np.round(datastd['13C'],2)
    datamean['18O std']=np.round(datastd['18O'],2)
    datamean['presLev']=data_p
    datamean=datamean[::-1]
    datamean.index=range(len(datamean))
    key=str(date).replace('-','')
    datasets[key]=datamean
plt.close()
#
#
# The block below is used to select the same co sample to link to flow rate. 
#
#
for date in dataLISA:
    dataLISA[date]['COdif']=dataLISA[date]['CO']-dataLISA[date]['CO IRMS']
    if datasets[date]['CO'][0]==dataLISA[date]['CO IRMS'][0]:
        # print(datasets[date]['CO'][0],dataLISA[date]['CO IRMS'][0])
        plt.plot(dataLISA[date]['d18O(CO)'][:len(datasets[date]['CO'])],dataLISA[date]['COdif'][:len(datasets[date]['CO'])], 'o',label=date)
plt.legend()
plt.show()
plt.close()

for date in dataLISA:
    plt.plot(dataLISA[date]['d18O(CO)'],dataLISA[date]['Weighted p(mbar)'],label=date)
plt.legend()
plt.show()
plt.close()
