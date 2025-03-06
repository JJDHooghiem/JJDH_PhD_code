#!/usr/bin/env python
# -*- coding: utf-8 -*-
from colisalib import *
from lodautil import LISA_load
values=get_irms_co_data()

datalisa=LISA_load()

for date in np.unique(values['flightDate']):
    data=values[(values['flightDate']==date)]
    data_co=data['COfcor'][(data['mesNo']==1)]
    data_t=data['Datetime'][(data['mesNo']==1)]
    data_p=data['presLev'][(data['mesNo']==1)]
    data_p,data_t,data_co=zip(*sorted(zip(data_p,data_t,data_co)))
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

    datamean.to_csv('/home/joram/research/data/LISA_CO_Measurements/'+str(date).replace('-','')+'CO_IRMS_UU_Processed.csv',columns=['presLev','Datetime','CO','13C','13C std','18O','18O std'], index=False,na_rep='NaN')














