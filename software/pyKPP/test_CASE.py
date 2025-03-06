import pyKPP
import stisolib
import config
basename='/home/joram/.local/src/kpp/CO_iso/strato_CO'
kpp_dat=pyKPP.kpp_load_data(basename+'.map',basename+'.dat')

isotopologues={ "C_17_OO"    :["CO2"   ,  "VSMOW17"  , 2],
"C_18_OO"    :["CO2"    ,  "VSMOW18" , 2],
"C_17_O"     :["CO"     ,  "VSMOW17" , 1], 
"C_18_O"     :["CO"     ,  "VSMOW18" , 1], 
"_13_CO"     :["CO"     ,  "VPDB13"  , 1], 
"_13_CH3"    :["CH3"    ,  "VPDB13"  , 1], 
"_13_CH3O"   :["CH3O"   ,  "VPDB13"  , 1], 
"_13_CH3O2"  :["CH3O2"  ,  "VPDB13"  , 1], 
"_13_CH3OOH" :["CH3OOH" ,  "VPDB13"  , 1], 
"H_13_CO"    :["HCO"    ,  "VPDB13"  , 1], 
"_13_CH2O"   :["CH2O"   ,  "VPDB13"  , 1], 
"_13_CO2"    :["CO2"    ,  "VPDB13"  , 1], 
"_13_CH4"    :["CH4"    ,  "VPDB13"  , 1]}

specs={"CH3":'ppt'     ,
"CH3O"      :'ppt'     ,
"CH3O2"     :'ppt'     ,
"CH3OOH"    :'ppt'     ,
"HCO"       :'ppt'     ,
"CH2O"      :'ppt'     ,
"CO2"       :'ppm'     ,
"CO"        :'ppb'     ,
"CH4"       :'ppb'    }

def compute_ratios(dat,minor):
    """TODO: Docstring for compute_ratios.
    Returns
    -------
    TODO

    """
    s=isotopologues[minor]
    r=(1/s[2])*dat[minor]/dat[s[0]]
    isotope_ratio=stisolib.ratio_to_delta(r,s[1])
    return isotope_ratio

def data_fixer(kpp_dat,key):
    """TODO: Docstring for data_fixer.

    Parameters
    ----------
    arg1 : TODO

    Returns
    -------
    TODO

    """
    if key in isotopologues:
        var=compute_ratios(kpp_dat,key)
    elif key in specs:
        var=kpp_dat[key]/pyKPP.units[specs[key]]
    else:
        var=0
    return var

import scantools
xlabs=[('time')]*4
ylabs=[config.axl['co'],config.axl['ch4'],config.axl['13c'],config.axl['18o']]
ylims=[(30,34),(1680,1710),(-70,0),(-15,70)]
time=kpp_dat['Time']/24
xlims=[(time[0],time.iloc[-1])]*4
# ylims=[()]
fig,axes=scantools.plot_init(2,2,xlabs=xlabs,ylabs=ylabs,xlims=xlims,ylims=ylims)
scantools.plot_add(axes[0,0],time,data_fixer(kpp_dat,'CO'),argsort=False)
scantools.plot_add(axes[0,1],time,data_fixer(kpp_dat,'CH4'),argsort=False)

for key in ["_13_CO"  , "_13_CO2",  "_13_CH4"]:
    scantools.plot_add(axes[1,0],time,data_fixer(kpp_dat,key),argsort=False)

for key in ["C_18_OO" , "C_18_O" ]:
    scantools.plot_add(axes[1,1],time,data_fixer(kpp_dat,key),argsort=False)
fig.tight_layout()
fig.savefig('test.pdf')
