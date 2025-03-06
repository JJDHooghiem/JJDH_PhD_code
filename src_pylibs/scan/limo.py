"""
This code was written for the analysis presented in the disseration of Joram Jan Dirk Hooghiem
Functions that do the core analysis are presented in here.  

This program is free software: you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software Foundation, 
version 3. This program is distributed in the hope that it will be useful, but 
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS 
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. 

You should have received a copy of the GNU General Public License along with this 
program. If not, see <http://www.gnu.org/licenses/>.
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import atmos
import lodautil
import matplotlib.pyplot as plt
import numpy as np
import scantools
import stisolib
from scipy.interpolate import interp1d
from scipy.stats import pearsonr
import config

colors = config.GruvBoxColors
markers = config.Markers

def plot_fhvvsco(axes, interpolated=False):
    """plot_TracerTracer.
    ads a plot the the axes instance of photolysis derived fraction of co.
    Parameters.
    axes: axes subplot object which should contain the figure. 
    interpolated: Boolean. Default=True. Type of subsampling from EMAC simulation results used.    Either interpolated or nearest data on track. The difference is in fact minor.  
    """
    lisa = lodautil.LISA_load()
    ncfid = lodautil.get_ncfid(interpolated)
    ppb = 1E9
    for dat, c in zip(lisa.keys(), colors):
        LISA = lisa[dat]
        times = lodautil.get_sample_dt(LISA)
        t = times[0][0]
        COx = lodautil.echam.get_ECHAM_tt(t, 'tracer_gp_CO', ncfid)
        HVCO = lodautil.echam.get_ECHAM_tt(t, 'tracer_gp_FHVCO', ncfid)
        # HVCO = lodautil.echam.get_ECHAM_tt(t, 'tracer_gp_FCMCO', ncfid)
        press = lodautil.echam.get_ECHAM_pp(t, ncfid)
        sel = (press <= 5000) & (2000 <= press) & (COx*ppb < 100)
        axes.plot(ppb*COx[sel], HVCO[sel]/COx[sel], 'o', color=c, label=dat)
    return

def plot_tracer_profiles(axes_array,key ,interpolated=True,ac=True):
    """plot_TracerTracer.
    plots profiles of different tracers sorted by date. 

    axes_array: array containing the axes subplot objects which will hold the figures.

    key: "CO", "CH4", or "CO2"  

    interpolated: Boolean. Default=True. Type of subsampling from EMAC simulation results used.    Either interpolated or nearest data on track. The difference is in fact minor. 
    
    ac: boolean. if true aircore data will be included if possible.

    """
    if ac==True:
        AirCore = lodautil.AirCore_load()

    lisa = lodautil.LISA_load()
    ncfid = lodautil.get_ncfid(interpolated)
    echam_unit=lodautil.echam_unit[key]
    for dat, axes in zip(sorted(lisa.keys()),axes_array.ravel()):
        LISA = lisa[dat]
        times = lodautil.get_sample_dt(LISA)
        t = times[0][0]

        x_echam = lodautil.echam.get_ECHAM_tt(t, 'tracer_gp_%s' % key, ncfid)
        pres_echam = lodautil.echam.get_ECHAM_pp(t, ncfid)/100
        scantools.plot_add(axes,echam_unit*x_echam, pres_echam,argsort="False", marker='>', color=colors[1], label='EMAC')

        if key in ['CO','CH4']:
            times = lodautil.get_sample_dt(LISA, model="CAMS")
            hours = times[0][0]
            # press = nc_fid['level'][:]*100
            lat = [np.mean(LISA['Lat'])]
            lon = [np.mean(LISA['Lon'])]
            press = lodautil.get_cams_pressure(dat, lat, lon, hours)/100
            dataset = lodautil.get_cams_nc_fid(dat)
            var = lodautil.get_cams_profile( lodautil.cams_key[key], hours, lat, lon,  dataset)*lodautil.cams_unit[key]
            scantools.plot_add(axes,var, press,argsort=False, marker='*',color=colors[2], label='CAMS')
        if ac==True:
            col=0
            for f in AirCore.keys():
                if dat in f:
                    y=AirCore[f][key]
                    x=AirCore[f]['P']
                    x,y=scantools.asym_convolve(x,y,5)
                    scantools.plot_add(axes,y,x,argsort=False, marker='o', color=colors[3+col], label=f.split('_')[0])
                    col+=1
        scantools.plot_add(axes,LISA[key], LISA['p'],argsort=False,marker='d', color=colors[0], label='Lisa ')
        axes.legend(loc='best')
        axes.set_title(dat[:4]+'-'+dat[4:6]+'-'+dat[6:]) 
    return

def plot_FHVCOvsP(fig,axes_array,interpolated=False):
    """
    Similar to  plot_fhvvsco now vs pressure. also the CO2 loss rate and carbon monoxide profiles are plotted.

    """
    ncfid = lodautil.get_ncfid(interpolated, daymean=True)
    ppb = 1E9
    times, dates = lodautil.get_unique_dates()
    for t, dat, c in zip(times, dates, colors):
        t = np.floor(t)+0.5
        COx = lodautil.echam.get_ECHAM_tt(t, 'tracer_gp_CO', ncfid)
        HVCO = lodautil.echam.get_ECHAM_tt(t, 'tracer_gp_FHVCO', ncfid)
        # This is only CH4 derived CO2?
        # FCMCO2/CO2 = (JCO2*XFCMCO2)/(JCO2*CO2) = PTLFCMCO2/XPTLCO2
        # XPTLCO2 = CO2/FCMCO2
        CO2 = lodautil.echam.get_ECHAM_tt(t, 'tracer_gp_CO2', ncfid)
        FCMCO2 = lodautil.echam.get_ECHAM_tt(t, 'tracer_gp_FCMCO2', ncfid)
        JCO2 = (CO2/FCMCO2)*lodautil.echam.get_ECHAM_tt(t,
                                                        'tracer_gp_XPTLFCMCO2', ncfid)

        press = lodautil.echam.get_ECHAM_pp(t, ncfid)
        axes_array[0].plot(ppb*COx, press, 'o', color=c, label=dat)
        axes_array[1].plot(HVCO/COx, press, 'o', color=c, label=dat)
        axes_array[2].plot(JCO2, press, 'o', color=c, label=dat)
    return 


def plot_dtdp(axes_array):
    """

    """
    ncfid = lodautil.get_ncfid(interpolated=True, daymean=True)
    LISA = lodautil.flattened_LISA()
    dt = np.array([])
    dc = np.array([])
    dp = np.array([])
    for dat, m in zip(lodautil.get_dates(LISA), markers):
        data = lodautil.date_select(LISA, dat)
        echamy = ['ECHAM5_tm1',  'p']

        # lisa_time=get_sample_paramsLtoE(data)[0][-1]
        lisa_time = np.floor(lodautil.get_sample_dt(data)[0][0])+0.5
        lisa_p = data['p']*100
        ch4 = data['CH4']
        for c, v in zip(colors, ['hyb']):
            echam_T = lodautil.get_echam_at_LISA(
                lisa_time, lisa_p, 'ECHAM5_tm1', ncfid, ch4=ch4, method=v)
            echam_p = lodautil.get_echam_at_LISA(
                lisa_time, lisa_p, 'p', ncfid, ch4=ch4, method=v)
            echam_co = lodautil.get_echam_at_LISA(
                lisa_time, lisa_p, 'tracer_gp_CO', ncfid, ch4=ch4, method=v)
            axes_array[0, 0].plot(echam_p-lisa_p, lisa_p,
                                  color=c, marker=m, label=dat+' '+v)
            axes_array[0, 1].plot(echam_T-data['T'], lisa_p,
                                  color=c, marker=m, label=dat+' '+v)
            # axes_array[1,0].plot(echam_p-lisa_p,1E9*echam_co-data['CO'],color=c,marker=m,label=dat+' '+v)
            # axes_array[1,1].plot(echam_T-data['T'],1E9*echam_co-data['CO'],color=c,marker=m,label=dat+' '+v)
            dt = np.append(dt, echam_T-data['T'])
            dc = np.append(dc, 1E9*echam_co-data['CO'])
            dp = np.append(dp, echam_p-lisa_p)

    mask = (abs(dc) < 20)
    dt = dt[mask]
    dc = dc[mask]
    dp = dp[mask]

    scantools.statplot(axes_array[1, 0], dp, dc)
    scantools.statplot(axes_array[1, 1], dt, dc)
    return



def echamBudget(axes,interpolated=False):
    """echamBudget.
    Computes a figure with the isotope budget of CO, by using values from literature 
    """
    LISA = lodautil.var_select(lodautil.flattened_LISA(), 'd18O(CO)')
    model_results={}

    ncfid=lodautil.get_ncfid(interpolated)
    for dat,c in zip(lodautil.get_dates(LISA),colors):
        data=LISA[LISA['Date']==dat]
        # 12:00 utc:
        time=lodautil.get_sample_dt(data)[0]
        # time=get_sample_paramsLtoE(data)[0]
        fO3inCO,fO3inCO_cor,fCH4inCO,fCO2inCO,fO1DinCO=echamFractions(time,ncfid)
        press=lodautil.echam.get_ECHAM_pp(time,ncfid)
        mask=(press<20000) 
        xkey=data['CH4']
        CO  = lodautil.echam.get_ECHAM_tt(time,'tracer_gp_CO',ncfid)
        CH4  = lodautil.echam.get_ECHAM_tt(time,'tracer_gp_CH4',ncfid)*1E9
        COeps13  = 1e3*(lodautil.echam.get_ECHAM_tt(time,'tracer_gp_E13CO',ncfid)/CO-1)
        COeps18  = 1e3*(lodautil.echam.get_ECHAM_tt(time,'tracer_gp_E18CO',ncfid)/CO-1)
        fCO2inCO_at_LISA = interp1d(CH4[mask],fCO2inCO[mask],fill_value='extrapolate')(   xkey)
        fCH4inCO_at_LISA = interp1d(CH4[mask],fCH4inCO[mask],fill_value='extrapolate')(   xkey)
        fO1DinCO_at_LISA = interp1d(CH4[mask],fO1DinCO[mask],fill_value='extrapolate')(   xkey)
        fO3inCO_at_LISA  = interp1d( CH4[mask],fO3inCO[mask],fill_value='extrapolate')(     xkey)

        fO3inCO_at_LISA  = interp1d( CH4[mask],fO3inCO_cor[mask],fill_value='extrapolate')( xkey)
        CO_at_LISA       = 1E9*interp1d(  CH4[mask],CO[mask],fill_value='extrapolate')(           xkey)

        COeps18_at_LISA  = interp1d( CH4[mask],COeps18[mask],fill_value='extrapolate')(     xkey)
        COeps13_at_LISA  = interp1d( CH4[mask],COeps13[mask],fill_value='extrapolate')(     xkey)

        #
        # some values tried to optimise data from lisa 
        #
        budgetO=fCO2inCO_at_LISA*(44)+fO1DinCO_at_LISA*(150)+COeps18_at_LISA+fO3inCO_at_LISA*80
        budgetC=COeps13_at_LISA+fCO2inCO_at_LISA*(-18.8)+fO3inCO_at_LISA*-30

        axes[0,0].plot(data['d18O(CO)']-budgetO,data['p'],color=c,marker='o',linestyle='',label='$p$ interpolated')
        axes[0,1].plot(data['d18O(CO)']-budgetO,fCH4inCO_at_LISA,color=c,marker='o',linestyle='')
        axes[1,0].plot(data['d13C(CO)']-budgetC,data['p'],color=c,marker='o',linestyle='')
        axes[1,1].plot(data['d13C(CO)']-budgetC,fCH4inCO_at_LISA,color=c,marker='o',linestyle='')
    return fig,axes 

def echamNMHC(interpolated=False):
    """echamNMHC.
    produces figures to look at the several Non Methane Hydrocarbons simulated by EMAC at lisa observations.
    """
    LISA = lodautil.var_select(lodautil.flattened_LISA(), 'd18O(CO)')
    ncfid=lodautil.get_ncfid(interpolated)
    fig,ax=plt.subplots(1,1,figsize=(3,3))
    for dat,c in zip(lodautil.get_dates(LISA),colors):
        data=LISA[LISA['Date']==dat]
        time=lodautil.get_sample_dt(data)[0][0]

        press=lodautil.echam.get_ECHAM_pp(time,ncfid)
        # Tracers 
        C2H2  = 1E12*lodautil.echam.get_ECHAM_tt(time,'tracer_gp_C2H2',ncfid)
        C2H4  = 1E12*lodautil.echam.get_ECHAM_tt(time,'tracer_gp_C2H4',ncfid)
        C2H6  = 1E12*lodautil.echam.get_ECHAM_tt(time,'tracer_gp_C2H6',ncfid)
        C3H6  = 1E12*lodautil.echam.get_ECHAM_tt(time,'tracer_gp_C3H6',ncfid)
        C3H8  = 1E12*lodautil.echam.get_ECHAM_tt(time,'tracer_gp_C3H8',ncfid)
        C5H8  = 1E12*lodautil.echam.get_ECHAM_tt(time,'tracer_gp_C5H8',ncfid)
        mask=(press<20000) 
        ax.plot(C2H6[mask],press[mask],color=c,marker='d',linestyle='',label=r'\textrm{C2H6} %s' %dat )
        ax.plot(C3H8[mask],press[mask],color=c,marker='o',linestyle='',label=r'\textrm{C3H8} %s' %dat )
        ax.plot(C2H2[mask],press[mask],color=c,marker='o',linestyle='',label=r'\textrm{C2H2} %s' %dat )
        ax.plot(C2H4[mask],press[mask],color=c,marker='o',linestyle='',label=r'\textrm{C2H4} %s' %dat )
        ax.plot(C3H6[mask],press[mask],color=c,marker='o',linestyle='',label=r'\textrm{C3H6} %s' %dat )
        ax.plot(C5H8[mask],press[mask],color=c,marker='o',linestyle='',label=r'\textrm{C5H8} %s' %dat )
        # ax.plot(fO3inO1D[mask],press[mask],color=c,marker='>',linestyle='')
        ax.set_xlabel('mole fraction ppt')
        ax.set_ylabel('$p$ (Pa)')
        ax.set_ylim(20000,0)
    return fig,ax 

# ltd is set of tex formatted strings t
ltd={'T': '$T$','PT': r'$\theta$', 'p': r'$p$', 'CH4':r'$\textrm{CH}_{4}$',
        'N2O':r'$\textrm{N}_{2}\textrm{O}$', 'CO':r'$\textrm{CO}$', 'CO2':r'$\textrm{CO}_{2}$'}

def echam_taylor(lisakey, echamkey, ncfid):
    """echam_taylor.
    Collects data for a Taylor diagram with data from the LISA sampler as independend variable. lisakey and echamkey are the respective names in the datasets for LISA and EMAC (ECHAM5/Messy) atmosphere model.
  
    """
    yi = []
    for v in ['p', 'pot', 'CH4', 'hyb']:
        x, y = lodautil.collect_lisa_echam(lisakey, echamkey, ncfid, method=v)
        yi.append([np.std(y)/np.std(x), pearsonr(x, y)[0]])
    stdref = np.std(x)/np.std(x)
    return stdref, yi

def echam_taylor_plot(lisakey,echamkey,title,ncfid,*args,**kwargs):
    """
    Creates a taylor diagram in an existing figure
    """
    if isinstance (lisakey,list):
        stdrefs=[]
        yis=[]
        for xk,yk in zip(lisakey,echamkey):
            f,y=echam_taylor(xk,yk,ncfid)
            stdrefs.append(f)
            yis.append(y)
        taydia=scantools.TaylorDiagram(stdrefs[0], *args,**kwargs)
        for yi,c,spec in zip(yis,colors[1:],lisakey):
            for dd,lab,m in zip (yi,['$p$',r'$\theta$',r'$\textrm{CH}_{4}$','hyb'],markers[1:]):
                taydia.add_sample(*dd,color=c,marker=m,label=lab+'-'+ltd[spec] )
    else:
        stdref,yi=echam_taylor(lisakey,echamkey,ncfid)
        taydia=scantools.TaylorDiagram(stdref, *args,**kwargs)
        for dd,lab in zip (yi,['$p$',r'$\theta$',r'$\textrm{CH}_{4}$']):
            taydia.add_sample(*dd,marker='o',label=lab)
    taydia.add_contours(colors='k')
    taydia.add_grid()
    for k,m in zip(['T','CO','CH4'],markers[:7]):
        if k in lisakey:
            x,y=lodautil.collect_lisa_cams(k)

            yi=[np.std(y)/np.std(x),pearsonr(x,y)[0]]
            taydia.add_sample(*yi,color=colors[6],marker=m,label='CAMS'+'$p$'+'-'+k)
    return

def compareModel(lisakeys,echamkeys):
    """
    Creates a Taylor diagram comparing data to LISA (lisakeys). 
    """
    ncfid=lodautil.get_ncfid(interpolated=False,daymean=False)
    h,w=scantools.get_figsize(1,1)
    fig=plt.figure(figsize=(config.figwidth,h))
    # fig=plt.figure(figsize=(h,w))
    # spec=fig.add_gridspec(ncols=2, nrows=1, width_ratios=[1,1/scantools.fig_adjust_factor], height_ratios=[1])
    spec=fig.add_gridspec(ncols=2, nrows=1, width_ratios=[(config.figwidth-h)/config.figwidth,h/config.figwidth], height_ratios=[1])
    echam_taylor_plot(lisakeys,echamkeys,None,ncfid,spec=spec,fig=fig,rect=122,xlabel=r"$\sigma/\sigma_{\text{L}}$",label='LISA')
    return fig
#
# LISA ECHAM 1 1 plots
#
def eval_echam_oneone(axes_array,lisakeys,echamkeys):
    """
    Collects data and checks the 1 to 1 correspondence of simulated vs (independend) LISA observations.
    """
    ncfid=lodautil.get_ncfid(interpolated=True,daymean=False)
    data_dif={}
    for v,lab,c in zip(['p','pot','CH4','hyb'],['$p$',r'$\theta$',r'$\textrm{CH}_{4}$','hyb'],colors):
        data_dif[lab]={}
        for axes,lisakey,echamkey in zip(axes_array.ravel(),lisakeys,echamkeys):
            x,y=lodautil.collect_lisa_echam(lisakey,echamkey,ncfid,method=v) 
            if lisakey=='p':
                x=x/100
                y=y/100
            scantools.axoneone(axes,x,y,color=c,lab=lab)
            data_dif[lab][lisakey]=y-x
    return data_dif

def colifetime(fig=None,axes=None, interpolated=False ,experiment='z4',**kwargs):
    """
    computes and plot the CO lifetime.  
    """
    # LISA = lodautil.var_select(lodautil.flattened_LISA(), 'd18O(CO)')
    LISA = lodautil.flattened_LISA()
    ncfid=lodautil.get_ncfid(interpolated,daymean=True,experiment=experiment)
    for dat,c in zip(lodautil.get_dates(LISA),colors):
        data=lodautil.date_select(LISA,dat)
        time=np.floor(lodautil.get_sample_dt(data)[0][0])+0.5
        # press=lodautil.echam.get_ECHAM_pp(time,ncfid)
        tauco= lodautil.echam.get_ECHAM_tt(time,'tauCO',ncfid)
        # tauco= lodautil.echam.get_ECHAM_tt(time,'tracer_gp_OH',ncfid)
        tpot = lodautil.echam.get_ECHAM_tt(time,'ECHAM5_tpot',ncfid)
        # axes.plot(tauco/(3600*24),press,color=c,label=dat) 
        # axes.plot(tauco,tpot,color=c,label=dat,**kwargs) 
        axes.plot(tauco/(3600*24*365),tpot,color=c,label=dat,**kwargs) 
    return  

def echam_st(dp, dt,rO1D='jpl',interpolated=False ):
    """
    A forward model to compute co and its stable isotopes from O1D/OH/CH4 and CL fields from EMAC simulations
    Parameters
    ----------
    interpolated :
        interpolated
    """
    LISA = lodautil.flattened_LISA()
    model_results = {}
    ncfid = lodautil.get_ncfid(interpolated=interpolated, daymean=True)
    for dat in lodautil.get_dates(LISA):
        data = lodautil.date_select(LISA, dat)
        # CH4=data['CH4']*1E-9
        time = np.floor(lodautil.get_sample_dt(data)[0][-1])+0.5
        # get daily mean variables

        # This is only CH4 derived CO2?
        # FCMCO2/CO2 = (JCO2*XFCMCO2)/(JCO2*CO2) = PTLFCMCO2/XPTLCO2
        # XPTLCO2 = CO2/FCMCO2

        O1D = lodautil.echam.get_ECHAM_tt(time, 'tracer_gp_O1D', ncfid)
        OH = lodautil.echam.get_ECHAM_tt(time, 'tracer_gp_OH', ncfid)
        CH4 = lodautil.echam.get_ECHAM_tt(time, 'tracer_gp_CH4', ncfid)
        CO   = lodautil.echam.get_ECHAM_tt(time,'tracer_gp_CO',ncfid)
        Cl = lodautil.echam.get_ECHAM_tt(time, 'tracer_gp_Cl', ncfid)

        press = lodautil.echam.get_ECHAM_pp(time, ncfid)
        temp = lodautil.echam.get_ECHAM_tt(time, 'ECHAM5_tm1', ncfid)
        co_base, CH4_sink_b= co_stst(press, temp, CH4, Cl, OH, O1D)
        co_dif,CH4_sink= co_stst( press+dp, temp+dt, CH4, Cl, OH, O1D,rO1D=rO1D)
        sink_dif=CH4_sink-CH4_sink_b

        model_results[dat]={}
        model_results[dat]['COst']=co_base
        model_results[dat]['COm']=CO*1E9
        model_results[dat]['dif']=co_dif-co_base
        model_results[dat]['pres']=press
        model_results[dat]['sink']=sink_dif
        model_results[dat]['sinkCH4']=CH4_sink_b
        model_results[dat]['CH4']=CH4*1E9
    return model_results

def plot_profiles(axes_array,echamy,echamkeys,interpolated=True,daymean=False):
    """
    Plots profiles.
    """
    LISA=lodautil.flattened_LISA()
    ncfid=lodautil.get_ncfid(interpolated=interpolated,daymean=daymean)
    for dat,c in zip(lodautil.get_dates(LISA),colors):
        data=lodautil.date_select(LISA,dat)
        time=np.floor(lodautil.get_sample_dt(data)[0])+0.5
        y = lodautil.echam.get_ECHAM_tt(time[0],echamy,ncfid)
        for xkey,axes in zip(echamkeys,axes_array.ravel()):
            x = lodautil.echam_unit[xkey]*lodautil.echam.get_ECHAM_tt(time[0],'tracer_gp_'+xkey,ncfid)
            axes.plot(x,y,color=c,label=dat) 
    return

def plot_rel_rates(axes_array):
    """
    Plots several loss rates of ch4. 
    """
    ncfid=lodautil.get_ncfid(interpolated=True,daymean=False)
    LISA=lodautil.flattened_LISA()
    for dat,m in zip(lodautil.get_dates(LISA),markers):
        data=lodautil.date_select(LISA,dat)
        echamy = ['ECHAM5_tm1',  'p']

        lisa_time=lodautil.get_sample_dt(data)[0][-1]
        # lisa_time=np.floor(get_sample_paramsLtoE(data)[0][0])+0.5
        lisa_p=data['p']*100
        ch4=data['CH4']
        lisarates=eval_rates(lisa_p,data['T'])[1:]
        # for axes,x in zip(axes_array.ravel(),lisarates):
            # axes.plot(x,lisa_p,color=c,marker='d',label=dat)
        for c,v in zip(colors,['press','hyb']):
            echam_T= lodautil.get_echam_at_LISA(lisa_time,lisa_p,'ECHAM5_tm1',ncfid,ch4=ch4,method=v)
            echam_p= lodautil.get_echam_at_LISA(lisa_time,lisa_p,'p',ncfid,ch4=ch4,method=v)
            # print(echam_p-lisa_p)
            # print(echam_T-data['T'])
            echamrates=eval_rates(echam_p,echam_T)[1:]
            for axes,x,b in zip(axes_array.ravel(),echamrates,lisarates):
                axes.plot(x/b,lisa_p,color=c,marker=m,label=dat+' '+v)
    return

def eval_rates(pres,temp):
    """
    evaluates reaction rate constants of gas phase reactions 
    """
    pres   = pres #pressure
    temp   = temp #temperature
    nden   = atmos.ndens(temp,pres)
    # CH4 + O1D -> products
    k_CH4_O1D = 1.75E-10*np.exp(temp*0)
    # CH4 + Cl -> products
    k_CH4_Cl  = 6.6E-12*np.exp(-1240./temp) #atkinson2006
    # CH4 + OH -> products
    k_CH4_OH  = 1.85E-20*np.exp(2.82*np.log(temp)-987./temp) #atkinson2003
    # OH + CO -> products
    k_CO,_,_,_ = stisolib.co_3step_OH(pres,temp)
    # k_CO      = (1.57E-13+(3.54E-33)*nden)
    return k_CH4_O1D, k_CH4_Cl ,k_CH4_OH ,k_CO     

def co_stst(pres, temp, CH4, Cl, OH,O1D,rO1D='jpl'):
    """
    Computing the steady state value of CO from mole fractions of 
    CH4, Cl, OH,O1D
    
    """
    pres = pres  # pressure
    temp = temp  # temperature
    nden = atmos.ndens(temp, pres)
    CH4 = CH4
    Cl = Cl
    OH = OH
    O1D = O1D
    # from mole fraction to number denisties in per cm3
    n_Cl = Cl * nden
    n_OH = OH * nden
    n_O1D = O1D * nden
    n_CH4 = CH4 * nden

    # CH4 sink reactions:
    # k_O1D = atmos.rate_arr(1.75E-10,0.0,temp)
    # k_Cl  = atmos.rate_arr(7.1E-12,1270.0,temp)
    # k_OH  = atmos.rate_arr(2.45E-12,1775.0,temp)
    if rO1D=='v':
        k_O1D = atmos.rate_arr(1.91E-10,0.0,temp)
    else:
        k_O1D = 1.75E-10*np.exp(temp*0)
    k_Cl = 6.6E-12*np.exp(-1240./temp)  # 1759}
    k_OH = 1.85E-20*np.exp(2.82*np.log(temp)-987./temp)  # 1627

    # CO + OH
    # k_CO = (1.57E-13+(3.54E-33)*nden)
    k_CO,_,_,_ = stisolib.co_3step_OH(pres,temp)

    CO_p = (k_O1D * n_O1D +
            k_Cl * n_Cl +
            k_OH * n_OH)
    
    CO_p = (k_O1D * n_O1D +
            k_Cl * n_Cl +
            k_OH * n_OH)*n_CH4
    CH4_sink=(3600*24*365)*1E9*CO_p/nden
    CH4_Life = n_CH4/CO_p/(3600*24*365)
    CO_s = k_CO * n_OH
    
    CO_stst = CO_p/CO_s

    CO_mol = 1E9*CO_stst/nden
    return CO_mol,CH4_sink
