#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 20 08:04:12 2018

@author: joram
"""
import matplotlib.colors as mcolors

import numpy as np
from netCDF4 import Dataset
import os
import PyNetCDF_tools as pnc
from glob import glob
import matplotlib.pyplot as plt
import click

colors=['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#46f0f0', '#f032e6', '#bcf60c', '#fabebe', '#008080', '#e6beff', '#9a6324', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1', '#000075', '#808080', '#ffffff', '#000000']
@click.command()
@click.option('--key','-k',type=str,help='Key to compare be compared') 
@click.option('--filters','-f',type=(str,float,float),help='Filter to compare data. sza or levels can be picked. if sza this wil return a plot level vs key. Else key vs sza is plotted',multiple=True)
def main(key,filters):
    os.chdir('/Users/joram/research/data/Sodankyla_Ozone_sonde_2017/jvalresults')
    data_sets=glob('*.nc')
    plt.close()
    filt=[]
    for f in filters:
        filt.append(list(f))
    months=[]
    for data_set in data_sets: 
        nc_fid=Dataset(data_set)
        interest=pnc.data_selector(key,filt,nc_fid)
        if 'sza' in np.array(filt).T:
            y=nc_fid.variables['lev'][:]
            y= np.array([1000., 3000., 5040., 7339., 10248., 14053., 18935., 24966., 32107., 
        40212., 49027., 58204., 67317., 75897., 83472., 89631., 94099.,     
        96838., 98169. ])/100
            x=nc_fid[key][:,interest]
        else:
            x=nc_fid.variables['sza'][:]
            y=nc_fid[key][interest,:]
            y=nc_fid[key][interest,:][0]
     
        if data_set!='jval.nc':
            print data_set
            month=data_set[4:6]
        else:
            month=data_set    
        if month not in months:
            if month!='jval.nc':
                plt.plot(x,y,color=colors[int(month)],label=month)
            
                months.append(month)
            else:
                plt.plot(x,y,color=colors[13],marker='o',label=month)
            
        
        else:
            plt.plot(x,y,color=colors[int(month)])
    if 'sza' in np.array(filt).T:
        xlabel=key+' (1/s)'
        ylabel='p (hpa)'
        plt.ylim(np.max(y),0)
    else:
        ylabel=key+' (1/s)'
        xlabel='sza'
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.show()

if __name__=='__main__':
    main()
