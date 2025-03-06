#/usr/bin/env python
# -*- coding: utf-8 -*-
# Define a dicionary containg flight info 
import TrainRadCore as TRC
import numpy as np
import matplotlib.pyplot as plt
import scantools
import config
import matplotlib as mpl
import matplotlib.pyplot as plt 
import sys

import multiprocessing
mpl.use("Qt5Agg")
plt.rcParams.update({"text.usetex":False})

path='/home/joram/research/data/TrainRad/'

# target_key=sys.argv[-1]
# TrainData=TRC.LoadData()
global datasets
datasets={}
for key in TRC.flight_files.keys():
    datasets[key]={}
    datasets[key]['raw']=TRC.LoadData(path+TRC.flight_files[key])
    datasets[key]['clean']=TRC.processMet(datasets[key]['raw'])

def worker_calc_p(target_key):
    print("########################################\n\n")
    print(target_key)
    print("########################################\n\n")
    TRC.plot_comp(datasets[target_key]['clean'],datasets[target_key]['raw'],target_key)
    keys=TRC.find_set(target_key)
    stolen={}
    for key in keys:
        if key not in target_key:
            stolen[target_key+'_'+key]=TRC.fil(datasets[target_key]['clean'],otherdat=datasets[key]['clean'],force=True)
    
    for key in stolen.keys():
        stolen[key]=TRC.computerPressure(stolen[key],target_key)
    
    
    data_int=TRC.computerPressure(datasets[target_key]['clean'].copy(),target_key)
    
    print(np.min(data_int['P']))
    print(data_int['P'].iloc[-1])
    
    xlabs=['T (K)','T (K)','RH','RH','p (hPa)','p (hPa)']
    ylabs=['z']*6
    xlims=[(210,310), (210,310),(-20,120),(-20,120),(0,1050),(0,1050)]
    ylims=[(0,35000)]*6
    
    fig,axes=scantools.plot_init(3,2,xlabs=xlabs,ylabs=ylabs,xlims=xlims,ylims=ylims)
    
    for key,c,m in zip(stolen.keys(),config.GruvBoxColors[1:],config.Markers[1:]): 
        print(np.min(stolen[key]['P']))
        print(stolen[key]['P'].iloc[-1])
    
        TRC.save_as_tsv(stolen[key],TRC.flight_files[target_key].replace('.mto','')+'_'+key.replace(target_key,''))
        TRC.plot_results(stolen[key], axes ,  marker=m , linestyle='-' , label=key   , color=c , argsort=False)
    TRC.plot_results(data_int , axes ,  marker='o' , linestyle='-' , label='int' , color=config.GruvBoxColors[0] , argsort=False)
    TRC.save_as_tsv(data_int,TRC.flight_files[target_key].replace('.mto',''))
    for ax in axes.ravel():
        ax.legend()
    fig.tight_layout()
    fig.savefig('%s_all_data.pdf' % target_key)
    return

print(datasets.keys())
pool=multiprocessing.Pool()
pool.map(worker_calc_p,TRC.flight_files.keys())
pool.close()
pool.join()
exit()

# for key in TRC.flight_files.keys():
#     datasets[key]={}
#     datasets[key]['raw']=TRC.LoadData(path+TRC.flight_files[key])
#     datasets[key]['clean']=TRC.processMet(datasets[key]['raw'])


for target_key in TRC.flight_files.keys():
# for target_key in ['002']:
    print("########################################\n\n")
    print(target_key)
    print("########################################\n\n")
    keys=TRC.find_set(target_key)
    stolen={}
    for key in keys:
        if key not in target_key:
            stolen[target_key+'_'+key]=TRC.fil(datasets[target_key]['clean'],otherdat=datasets[key]['clean'],force=True)
    
    for key in stolen.keys():
        stolen[key]=TRC.computerPressure(stolen[key],target_key)
    
    
    data_int=TRC.computerPressure(datasets[target_key]['clean'].copy(),target_key)
    
    print(np.min(data_int['P']))
    print(data_int['P'].iloc[-1])
    
    xlabs=['T (K)','T (K)','RH','RH','p (hPa)','p (hPa)']
    ylabs=['z']*6
    xlims=[(210,310), (210,310),(-20,120),(-20,120),(0,1050),(0,1050)]
    ylims=[(0,35000)]*6
    
    fig,axes=scantools.plot_init(3,2,xlabs=xlabs,ylabs=ylabs,xlims=xlims,ylims=ylims)
    
    for key,c,m in zip(stolen.keys(),config.GruvBoxColors[1:],config.Markers[1:]): 
        print(np.min(stolen[key]['P']))
        print(stolen[key]['P'].iloc[-1])
    
        TRC.save_as_tsv(stolen[key],TRC.flight_files[target_key].replace('.mto','')+'_'+key.replace(target_key,''))
        TRC.plot_results(stolen[key], axes ,  marker=m , linestyle='-' , label=key   , color=c , argsort=False)
    TRC.plot_results(data_int , axes ,  marker='o' , linestyle='-' , label='int' , color=config.GruvBoxColors[0] , argsort=False)
    TRC.save_as_tsv(data_int,TRC.flight_files[target_key].replace('.mto',''))
    for ax in axes.ravel():
        ax.legend()
    fig.tight_layout()
    fig.savefig('%s_all_data.pdf' % target_key)
    # plt.show()
exit()
