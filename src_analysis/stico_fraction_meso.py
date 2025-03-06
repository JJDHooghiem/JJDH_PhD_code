import stisolib
import atmos
import numpy as np
from netCDF4 import Dataset
import scantools
import matplotlib.pyplot as plt
import config
bot=atmos.Standard_atmos(50E3)
top=atmos.Standard_atmos(90E3)

a_bot=np.array( stisolib.co_3step_OH(*bot) )
a_top=np.array( stisolib.co_3step_OH(*top) )
a_bot/=a_bot[0]
a_top/=a_top[0]
print(1000*(a_top-a_bot))
high_p_lim=15000 #Pa
xlabs=[config.axl['co']]
ylabs=[config.axl['p']]
xlims=[(0,70)]
ylims=[(high_p_lim,50)]


import lodautil 
# ncfid=lodautil.echam.get_ncfid()
# times, dates = lodautil.get_unique_dates()
f_name=config.DataDir+'/ECHAM/LISA/SICM-z4/SICM-z4________20170426_0010_s4d_LISA.nc'
ncfid=Dataset(f_name)
times = lodautil.echam.get_ECHAM_time(ncfid)
# print(len(times))
# exit()
for t in zip(times):
    hours=float(t-np.floor(t))
    hour=np.round(hours*24,2)
    minutes=np.round(float(hour-np.floor(hour))*60,2)
    sec=np.round(float(minutes-np.floor(minutes))*60,0)
    h=np.floor(hour)
    m=np.floor(minutes)
    s=np.round(s,0)
    press = lodautil.echam.get_ECHAM_pp(t, ncfid)
    COx    = lodautil.echam.get_ECHAM_tt(t, 'tracer_gp_CO', ncfid)
    # CH4 = lodautil.echam.get_ECHAM_tt(t, 'tracer_gp_CH4', ncfid)

    fig,axes=scantools.plot_init(1,1,xlabs=xlabs,ylabs=ylabs,xlims=xlims,ylims=ylims)

    mask=(press<high_p_lim)
    # print("CO\n",COx[mask])
    scantools.plot_add(axes,COx[mask]*1E9,press[mask],argsort=False,label=t,color=config.GruvBoxColors[2],linestyle='-' )
    axes.set_title(hour)
    # axes.legend()
    fig.savefig('temp_mov/p_vs_co_%s.png' % hour, format=png) 
    plt.close()
    # print("CO\n",COx[mask]*1E9)
    # print("CH4\n",CH4[mask]*1E9)
