#!/usr/bin/env python3
# Don't remove the line below, it is checked by "one to run them all"
# --otrta-p--
# extension p means parallel, s is for single
"""
This code was written for the analysis presented in the disseration of Joram Jan Dirk Hooghiem
"""
import config
import scantools
import pandas as pd

# Header infromation
h=[ 'site','year','month','co']
# Directory containing data
ddir=config.DataDir+'/flask_co/'

#initialise figure and axes objects
xlabs=[config.axl['yr']]
ylabs=[config.axl['co']]
xlims=[(2010,2020)]
ylims=[(35,125)]
fig,axes=scantools.plot_init(1,1,xlabs=xlabs,ylabs=ylabs,xlims=xlims,ylims=ylims)

data=pd.read_csv(ddir+'mlo_co.txt',sep='\s+',names=h, skiprows=70)
# Plot monthly data mid-month 
data['t']=data['year']+(data['month']-0.5)/12
scantools.plot_add(axes,data['t'],data['co'],argsort=False,marker='o',color=config.GruvBoxColors[0], label="Mauna Loa")

data=pd.read_csv(ddir+'spo_co.txt',sep='\s+',names=h, skiprows=68)
data['t']=data['year']+(data['month']-0.5)/12

scantools.plot_add(axes,data['t'],data['co'],argsort=False ,marker='o',color=config.GruvBoxColors[1],label="South Pole")
axes.legend()
fig.tight_layout()
fig.savefig(config.FigDir+'int_co_rec.pdf')
