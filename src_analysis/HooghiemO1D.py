#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import scantools
import config as config
import scan.stico as stico
import numpy as np
import pandas as pd

residuals_m = []
residuals_s = []
# Settings
i='18O'
# modes=['full', 'seasonpipe','season'     , 'simple'     , 'pipe']
# modes=[ 'season']
# modes=[  'simple'     ]
# texfilesrcsigall = open(config.TabDir+'src_sig_all.tex', 'w')
bscen='strict' # "res","res","res",'strict','strict','strict'
mode= 'season'  #   'season'   'pipe' 

xbase,res,residual,lisa,A,b=stico.run_inversion(i,mode=mode,method='hyb',sens_obs=False,fractionation=1,echam_enrich=True,bounds=bscen)

lisa['Altitude']/=1000

xlabs = [config.axl['18o']]*4
ylabs = ["Altitude (km)"]*4
xlims = [(-7,11)]*4

ykey='Altitude'
# ylims = [(380,580)]
ylims = [(14,23)]*4
# ykey='CH4'
# ylims = [(1800,500)]*4
# ylims = [(380,410)]*4
## Print results:
# print(mode)
# print(i)
# print(res)
# print(xbase)
# print(residual)

#####
## 4 panel figure
#####

fig, axes_array = scantools.plot_init(2, 2, xlabs=xlabs, ylabs=ylabs,xlims=xlims,ylims=ylims)
for axes, dat in zip(axes_array.ravel(),np.unique(lisa['Date'])):
    stico.plot_inversion(axes,residual,lisa,i,ykey=ykey,group_by='marker',date=dat,label='All sources',linestyle='-.',color=config.GruvBoxColors[9])

# replace o1d with ch4 source sig
sources=res['x'].copy()
sources[2]=sources[1]
residual_without_o1d=stico.calc_residual(A,sources,lisa,isotope='18O',fractionation=1)
for axes, dat in zip(axes_array.ravel(),np.unique(lisa['Date'])):
    stico.plot_inversion(axes,residual_without_o1d,lisa,i,ykey=ykey,group_by='marker',date=dat,label=r'Without $\textrm{O}(^{1}\textrm{D})$',linestyle=':',color=config.GruvBoxColors[1])


# also co2 with that of CH4
sources[0]=sources[1]
residual_without_o1d=stico.calc_residual(A,sources,lisa,isotope='18O',fractionation=1)
for axes, dat in zip(axes_array.ravel(),np.unique(lisa['Date'])):
    stico.plot_inversion(axes,residual_without_o1d,lisa,i,ykey=ykey,group_by='marker',date=dat,label=r'Without $\textrm{O}(^{1}\textrm{D})$ and  $\textrm{CO}_2$',linestyle=':',color=config.GruvBoxColors[2])
    mask = lisa['Date'] == dat
    stico.add_lisa(axes,lisa[mask],'d18O(CO)',ykey=ykey,fmt='d',xerr=0.5,group_by='marker',color=config.GruvBoxColors[8])
    handles,labels=scantools.getUniqueLegend(axes)
    axes.legend(handles=handles,labels=labels)

fig.tight_layout()
fig.savefig(config.FigDir+"Hooghiem2021_O1D_4Panel.pdf")
# exit()

#
# Several different pots
#
# For display purpose to illustrate the effect, we take the alternative route: 
# CH4 only obtains it source from co2 
# obtain the solution for the source signatures


####
#### A one panel figure
####

# fig, axes = scantools.plot_init(1, 2, xlabs=xlabs, ylabs=ylabs,xlims=xlims,ylims=ylims)
#fig, axes = scantools.plot_init(1, 1, xlabs=xlabs, ylabs=ylabs,xlims=xlims,ylims=ylims)
#stico.plot_inversion(axes,residual,lisa,i,ykey=ykey,group_by='marker',label='with O1D',linestyle='-.',color=config.GruvBoxColors[9])

## replace o1d with ch4 source sig
#sources=res['x'].copy()
#sources[2]=sources[1]

#residual_without_o1d=stico.calc_residual(A,sources,lisa,isotope='18O',fractionation=1)
#stico.plot_inversion(axes,residual_without_o1d,lisa,i,ykey=ykey,group_by='marker',label='No O1D',linestyle=':',color=config.GruvBoxColors[1])

## also co2 with that of CH4
#sources[0]=sources[1]
#residual_without_o1d=stico.calc_residual(A,sources,lisa,isotope='18O',fractionation=1)
#stico.plot_inversion(axes,residual_without_o1d,lisa,i,ykey=ykey,group_by='marker',label='No O1D No CO2',linestyle=':',color=config.GruvBoxColors[2])

#stico.add_lisa(axes,lisa,'d18O(CO)',ykey=ykey,fmt='d',xerr=0.5,group_by='marker',color=config.GruvBoxColors[8])
#handles,labels=scantools.getUniqueLegend(axes)
#axes.legend(handles=handles,labels=labels)

#fig.tight_layout()
#fig.savefig(config.FigDir+"Hooghiem2021_O1DonePanel.pdf")

#####
##### End A one panel figure
#####

#####
## end 4 panel figure
#####

##
##
## Get the tropopause heigh
##
##
#import lodautil
#import atmos
#data =  lodautil.AirCore_load()
#AC_keys = ['RUG002_20170904', 'RUG002_20170905', 'RUG002_20170906', 'RUG002_20170426']
#for dat in AC_keys:
#    tropopause = atmos.tropopause_calculator(data[dat]['GPS_ALT'], data[dat]['T'])
#    for d in np.unique(lisa['Date']):
#        # match AirCore (radiosonde) data to LISA based on date
#        if d.replace('-','') in dat:
#            mask = lisa['Date'] == d 
#            # Correct the altitude to altitude above tropopause
#            lisa['Altitude'][mask]-=tropopause
#ylabs=['Altitude above tropopause (km)']
#ylims=[(0,14)]
#fig, axes = scantools.plot_init(1, 1, xlabs=xlabs, ylabs=ylabs,xlims=xlims,ylims=ylims)
#stico.plot_inversion(axes,residual,lisa,i,ykey=ykey,group_by='marker',label='with O1D',linestyle='-.',color=config.GruvBoxColors[9])

## replace o1d with ch4 source sig
#sources=res['x'].copy()
#sources[2]=sources[1]

#residual_without_o1d=stico.calc_residual(A,sources,lisa,isotope='18O',fractionation=1)
#stico.plot_inversion(axes,residual_without_o1d,lisa,i,ykey=ykey,group_by='marker',label='No O1D',linestyle=':',color=config.GruvBoxColors[1])

## also co2 with that of CH4
#sources[0]=sources[1]
#residual_without_o1d=stico.calc_residual(A,sources,lisa,isotope='18O',fractionation=1)
#stico.plot_inversion(axes,residual_without_o1d,lisa,i,ykey=ykey,group_by='marker',label='No O1D No CO2',linestyle=':',color=config.GruvBoxColors[2])

#stico.add_lisa(axes,lisa,'d18O(CO)',ykey=ykey,fmt='d',xerr=0.5,group_by='marker',color=config.GruvBoxColors[8])
#handles,labels=scantools.getUniqueLegend(axes)
#axes.legend(handles=handles,labels=labels)

#fig.tight_layout()
#fig.savefig(config.FigDir+"Hooghiem2021_O1DonePanel_tropopause.pdf")

##
## Attempt to average results 
##

xlabs = [config.axl['18o']]*2
ylabs = [config.axl['alt']]*2
xlims = [(-6.5,11.5)]*2

ykey='Altitude'
# ylims = [(380,580)]
ylims = [(14,25)]*4
# ykey='p'
# ylims = [(140,20)]*4
print(lisa['PT'])
# exit()
bin_loc=[0,40,70,100,130,160]
# bin_loc=[0,30,60,90,120,150,180]
# bin_loc=reversed([600,550,500,450,400,350])
# bin_loc=np.arange(600,2000,100)
# bin_loc=np.arange(390,410,0.1)
# bin_loc=np.arange(390,410,0.1)
# bin_loc=np.linspace(10,160,7)
bins=pd.cut(lisa['p'],bins=bin_loc)
# print(bins)
# sel is boolean selection of bin and 
def sel_level(data,bins,sel=None):
    if sel==None:
        sel=[True]*len(data)
    mean=[]
    std=[]
    for b in np.unique(bins):
        mean.append(np.nanmean(data[(bins==b)&(sel)]))
        std.append(np.nanstd(data[(bins==b)&(sel)],ddof=1))
    sel=np.isfinite(mean)
    
    mean=np.array(mean)[sel]
    std=np.array(std)[sel]
    return mean,std

fig, axes = scantools.plot_init(1, 1, xlabs=xlabs, ylabs=ylabs,xlims=xlims,ylims=ylims)
# for date,axes,title in zip(['2017-04','2017-09'],axes_array.ravel(),['April 2017','September 2017']):
     
sel = ['2017-09' in d for d in lisa['Date']]

ydata,ystd= sel_level(lisa['p'],bins,sel)
mean,std=sel_level(lisa['d18O(CO)'],bins,sel)

scantools.plot_add(axes,mean,ydata,argsort=False,label='mean',linestyle=':',color=config.GruvBoxColors[9],xerr=std,yerr=ystd)
stico.add_lisa(axes,lisa[sel],'d18O(CO)',ykey=ykey,xerr=0.5,group_by='marker',color=config.GruvBoxColors[8])
for val in bin_loc:
    axes.axhline(val,color='k')
handles,labels=scantools.getUniqueLegend(axes)
axes.legend(handles=handles,labels=labels)
    
fig.tight_layout()
fig.savefig(config.FigDir+"Hooghiem2021_bins_Average.pdf")

# fig, axes = scantools.plot_init(1, 2, xlabs=xlabs, ylabs=ylabs,xlims=xlims,ylims=ylims)
fig,  axes_array = scantools.plot_init(1, 2, xlabs=xlabs, ylabs=ylabs,xlims=xlims,ylims=ylims)
# axes_array=np.array([axes,axes])
for date,axes,title,l in zip(['2017-04','2017-09'],axes_array.ravel(),['April 2017','September 2017'],['-','-']):
    sources=res['x'].copy()
    axes.set_title(title)
     
    sel = [date in d for d in lisa['Date']]
    ydata,ystd= sel_level(lisa['Altitude'],bins,sel)

    residual_with_o1d=stico.calc_residual(A,sources,lisa,isotope='18O',fractionation=1)
    model=residual_with_o1d+lisa['d18O(CO)']
    mean,std=sel_level(model,bins,sel)
    scantools.plot_add(axes,mean,ydata,argsort=False,marker='o',label='All sources',linestyle=l,color=config.GruvBoxColors[9],xerr=std,yerr=ystd)
    
    # replace o1d with ch4 source sig
    sources[2]=sources[1]
    
    residual_without_o1d=stico.calc_residual(A,sources,lisa,isotope='18O',fractionation=1)
    model=residual_without_o1d+lisa['d18O(CO)']
    mean,std=sel_level(model,bins,sel)
    scantools.plot_add(axes,mean,ydata,argsort=False,marker='o',label=r'Without $\textrm{O}({^1}\textrm{D})$',linestyle=l,color=config.GruvBoxColors[1],xerr=std,yerr=ystd)
    
    
    # also co2 with that of CH4
    sources[0]=sources[1]
    residual_without_o1d_co2=stico.calc_residual(A,sources,lisa,isotope='18O',fractionation=1)
    model=residual_without_o1d_co2+lisa['d18O(CO)']
    mean,std=sel_level(model,bins,sel)
    scantools.plot_add(axes,mean,ydata,argsort=False,marker='o',label=r'Without $\textrm{O}({^1}\textrm{D})$ and $\textrm{CO}_2$',linestyle=l,color=config.GruvBoxColors[2],xerr=std,yerr=ystd)
    
    # stico.plot_inversion(axes,residual_without_o1d,lisa,i,ykey=ykey,group_by='marker',label='No O1D No CO2',linestyle=':',color=config.GruvBoxColors[2])
    mean,std=sel_level(lisa['d18O(CO)'],bins,sel)
    scantools.plot_add(axes,mean,ydata,label='Obs.',marker='o',linestyle=l,color=config.GruvBoxColors[8],xerr=std,yerr=ystd)
    
    handles,labels=scantools.getUniqueLegend(axes)
    axes.legend(handles=handles,labels=labels)
    
fig.tight_layout()
fig.savefig(config.FigDir+"Hooghiem2021_O1DonePanel_Average_2.pdf")
    
