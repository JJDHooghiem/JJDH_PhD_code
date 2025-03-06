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

# # scantools.plot_add(axes,d["d13CO"],d["d18CO"],marker=config.Markers[2],color=config.GruvBoxColors[2],linestyle='',label="Caribic 1")
# # scantools.plot_add(axes,d["d13co_ozc"],d["d18co_ozc"],marker=config.Markers[2],color=config.GruvBoxColors[2],linestyle='',label="Caribic 1")
T_carib=np.array(data_CARIB["temp"])+273.15
p_carib=np.array(data_CARIB["press"])
pot_car=(T_carib)*(1000/p_carib)**0.286

# scantools.plot_add(axes,np.squeeze(np.array(data_CARIB["d13co_ozc"][:])),np.squeeze(np.array(data_CARIB["d18co_ozc"][:])),scatter=True,marker=config.Markers[2],c=pot_car,label="Caribic 1",vmin=300,vmax=550,cmap=config.GruvBox_cm)
print(np.array(data_CARIB["d18CO"][:]))
print(pot_car)
# scantools.plot_add(axes,np.array(data_CARIB["d13CO"][:]),np.array(data_CARIB["d18CO"][:]),scatter=True,marker=config.Markers[8],c=pot_car,label="Caribic 1 uncor.",vmin=300,vmax=550,cmap=config.GruvBox_cm)
scantools.plot_add(axes,np.array([400,500,540]),np.array([400,500,540]),scatter=True,marker=config.Markers[8],c=np.array([400,500,540]),label="Caribic 1 uncor.",vmin=300,vmax=550,cmap=config.GruvBox_cm)

# scantools.plot_add(axes,data_B96["d13CO"],data_B96["d18CO"],marker=config.Markers[1],color=config.GruvBoxColors[8],linestyle='',label="B96")
# # scantools.plot_add(axes,lisa["d13C(CO)"],lisa["d18O(CO)"],marker=config.Markers[0],color=config.GruvBoxColors[0],linestyle='',label="lisa 2017")
for dat,l in zip(np.unique(data_Lisa['Date']),config.Linestyles):
    Lisa=lodautil.date_select(data_Lisa,dat)
    p=Lisa['p'].argsort()
    x=np.array(Lisa["d13C(CO)"])[p]
    y=np.array(Lisa["d18O(CO)"])[p]
    scantools.plot_add(axes,x,y,marker='',color='k',label="lisa %s" % dat,argsort=False,linestyle=l,zorder=1)
# scantools.getUniqueLegend()
leg = axes.legend()

sc=scantools.plot_add(axes,data_Lisa["d13C(CO)"],data_Lisa["d18O(CO)"],marker=config.Markers[0],c=data_Lisa["PT"],scatter=True,cmap=config.GruvBox_cm,vmin=300,vmax=550,zorder=2)
fig.tight_layout()

cbar=fig.colorbar(sc,ax=axes)
cbar.ax.set_ylabel(r'$\theta$ K', rotation=270)
# for i in range(2,6):
#     leg.legendHandles[i].set_color(config.GruvBoxColors[0])
# fig.tight_layout()

fig.savefig(config.FigDir+'stico_all_co_iso.png')
