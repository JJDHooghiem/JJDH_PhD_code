import lodautil
import config
import scantools
import pandas as pd
from netCDF4 import Dataset
import numpy as np 

data_Lisa=lodautil.lisa.var_select(lodautil.lisa.flattened_LISA(),'d18O(CO)').reset_index()
data_B96=pd.read_csv(config.DataDir+'/CO_stable_isotope_data/new.dat',sep="\t")
data_CARIB=Dataset(config.DataDir+'/CO_stable_isotope_data/isoCO_C1_ext.nc')

xlabs=[config.axl['13cco']]
ylabs=[config.axl['18oco']]
xlims=[(-60,-20)]
ylims=[(-15,15)]
fig,axes=scantools.plot_init(1,1,xlabs=xlabs,ylabs=ylabs,xlims=xlims,ylims=ylims)

# scantools.plot_add(axes,d["d13CO"],d["d18CO"],marker=config.Markers[2],color=config.GruvBoxColors[2],linestyle='',label="Caribic 1")
# scantools.plot_add(axes,d["d13co_ozc"],d["d18co_ozc"],marker=config.Markers[2],color=config.GruvBoxColors[2],linestyle='',label="Caribic 1")
b=data_CARIB['press'][:]
b[b.mask]=np.nan
lbound=-90
hbound=90
mask=(data_CARIB['lat'][:]>lbound)&(data_CARIB['lat'][:]<hbound)&(b<300)
T_carib=np.array(data_CARIB["temp"][mask])+273.15
p_carib=np.array(data_CARIB["press"][mask])
pot_car=(T_carib)*(1000/p_carib)**0.286

# scantools.plot_add(axes,np.array(data_CARIB["d13CO"][:]),np.array(data_CARIB["d18CO"][:]),scatter=True,marker=config.Markers[8],c=pot_car,label="Caribic 1 uncor.",vmin=300,vmax=550,cmap=config.GruvBox_cm)


scantools.plot_add(axes,np.array(data_CARIB["d13co_ozc"][mask]),np.array(data_CARIB["d18co_ozc"][mask]),scatter=True,marker=config.Markers[2],c=pot_car,vmin=300,vmax=550,cmap=config.GruvBox_cm)

scantools.plot_add(axes,data_B96["d13CO"],data_B96["d18CO"],marker=config.Markers[1],color=config.GruvBoxColors[8],linestyle='',label="B96")
# scantools.plot_add(axes,lisa["d13C(CO)"],lisa["d18O(CO)"],marker=config.Markers[0],color=config.GruvBoxColors[0],linestyle='',label="lisa 2017")
for dat,l in zip(np.unique(data_Lisa['Date']),config.Linestyles):
    Lisa=lodautil.date_select(data_Lisa,dat)
    p=Lisa['p'].argsort()
    x=np.array(Lisa["d13C(CO)"])[p]
    y=np.array(Lisa["d18O(CO)"])[p]
    scantools.plot_add(axes,x,y,marker='d',color='k',label="lisa %s" % dat,argsort=False,linestyle=l,zorder=1)
# scantools.getUniqueLegend()

sc=scantools.plot_add(axes,data_Lisa["d13C(CO)"],data_Lisa["d18O(CO)"],marker=config.Markers[0],c=data_Lisa["PT"],scatter=True,cmap=config.GruvBox_cm,vmin=300,vmax=550,zorder=2)
fig.tight_layout()

cbar=fig.colorbar(sc,ax=axes)
cbar.ax.set_ylabel(config.axl['th'], rotation=270)
axes.plot([np.nan],[np.nan],color=config.GruvBoxColors[0],linestyle='',label="Caribic 1",marker=config.Markers[2])
leg = axes.legend(numpoints=1)
for i in range(1,5):
    leg.legendHandles[i].set_color(config.GruvBoxColors[0])
fig.tight_layout()

fig.savefig(config.FigDir+'stico_all_co_iso.pdf')
