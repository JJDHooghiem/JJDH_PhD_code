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
import numpy as np
import pandas as pd
import scantools
import stisolib
from scipy.interpolate import interp1d

import config
from scipy.optimize import lsq_linear

colors = config.GruvBoxColors
markers = config.Markers
# Oxygen general definition

alpha_co2=0.98

def ozone_in_CO(pres,temp,O3=1*1E-5,rates='JPL'):
    """ozone_in_CO.

    Parameters
    ----------
    pres :
        pres
    temp :
        temp
    O3 :
        O3
    rates :
        rates
    """
    #initial conditions (fields, so we don't care about the other reactions) 
    pres  = pres #pressure
    temp  = temp #temperature
    nden = atmos.ndens(temp,pres)
    
    O     = 0.0001*O3 # Is just so that [O3] >> [O] as in steady state.
    # from mole fraction to number denisties in per cm3 
    O     = O     *nden
    O3    = O3    *nden
    O2    = atmos.xO2    *nden
    
    # as in meccanism caaba 4.0
    if rates=='caaba':
        k_O = atmos.rate_arr(1.3E-10,0,temp)
        k_O3= atmos.rate_arr(5.10E-12,210,temp)
        k_O2= atmos.rate_3rd_iupac(temp,nden,7.0E-31,3.0,1.8E-12,-1.1,0.33)
    # Note that JPL changed their definition to kinf of 300 to 298 going from 
    # 18 to 19 version of the evaluation
    else:
        k_O = atmos.rate_arr(1.1E-10,0,temp)
        k_O3= atmos.rate_arr(5.40E-12,220,temp)
        k_O2= atmos.rate_3rd(temp,nden,4.0E-31,3.6,1.20E-12,-1.1) # page 2-4 checked 2020-11-03 08:44:10
    # compute overal products of nk 
    nk_o  = O*k_O
    nk_o2 = O2*k_O2
    nk_o3 = O3*k_O3
    # statistically distribute the oxygen molecules (reassingin above defs)
    # we only use the terminal oxygen atom in ozone, QOO or OOQ NOT: OQO therefor the statistical weight is 2 for ozne as well. 
    # Battacharya estimated that roughly 2/3 of the isotopic signature is carried hence the somewhat high vlaue for O18 
    x16,x17,x18 = stisolib.stat_distr_full_O(atmos.Od17,atmos.Od18,1)
    n_Od18  = O  * x18
    n_O     = O  * x16 

    x16,x17,x18 = stisolib.stat_distr_full_O(atmos.O2d17,atmos.O3d18,2)
    n_O3d18 = O3 * x18
    n_O3    = O3 * x16
    x16,x17,x18 = stisolib.stat_distr_full_O(atmos.O3d17,atmos.O2d18,2)
    n_O2d18 = O2 * x18   
    n_O2    = O2 * x16  
    
    a = stisolib.alpha_mu(15.0,32.0,34.0)
    
    #If we assume mass depenent kinetics  
    
    k_Od18 =k_O *stisolib.alpha_mu(15.0,16.0,18.0)
    k_O3d18=k_O3*stisolib.alpha_mu(15.0,48.0,50.0)
    k_O2d18=k_O2*stisolib.alpha_mu(15.0,32.0,34.0)
    
    sink_to_16O=n_O*k_O + n_O3*k_O3 + n_O2*k_O2 + 0.5*(k_O3d18*n_O3d18 + k_O2d18* n_O2d18)
    sink_to_18O=0.5*(k_O3d18* n_O3d18 + k_O2d18* n_O2d18)+ n_Od18*k_Od18 
    
    result_withO3=stisolib.ratio_to_delta(sink_to_18O/sink_to_16O, "VSMOW18")
    #print('With ozone %4.2f per mil ' %result_withO3)
    
    sink_to_16O=n_O2*k_O2 + 0.5*(k_O2d18* n_O2d18)
    sink_to_18O=0.5*k_O2d18* n_O2d18 
    
    result_noO3=stisolib.ratio_to_delta(sink_to_18O/sink_to_16O, "VSMOW18")
    #print('Without ozone %4.2f per mil ' %result_noO3)
    
    return result_noO3,result_withO3,nk_o, nk_o2,nk_o3

def rel_o(nk_o,nk_o2,nk_o3):
    """rel_o.

    Parameters
    ----------
    nk_o :
        nk_o
    nk_o2 :
        nk_o2
    nk_o3 :
        nk_o3
    """
    ksum=nk_o+nk_o2+nk_o3
    f_nk_o  = nk_o /ksum
    f_nk_o2 = nk_o2/ksum
    f_nk_o3 = nk_o3/ksum
    return f_nk_o,f_nk_o2,f_nk_o3
#
# Pure LISA analysis
#
def get_efeps_at(lisa,interpolated=True,daymean=False,method='hyb'):
    lisa['ECHAM_time'], _ = lodautil.get_sample_dt(lisa)
    ncfid = lodautil.get_ncfid(interpolated=interpolated, daymean=daymean)
    sink_enr_18=[]
    sink_enr_13=[]
    sink_enr_17=[]
    echamy=['E18pCO','E17pCO','E13pCO','CO']
    for t,p,ch4 in zip(lisa['ECHAM_time'],lisa['p'],lisa['CH4']): 
        echam_enr=lodautil.get_echam_tracers_gp(t,[p*100],echamy,ncfid,method=method,ch4=[ch4])
        sink_enr_13.append(1e3*(echam_enr['E13pCO'][0]/echam_enr['CO'][0]-1))
        sink_enr_17.append(1e3*(echam_enr['E17pCO'][0]/echam_enr['CO'][0]-1))
        sink_enr_18.append(1e3*(echam_enr['E18pCO'][0]/echam_enr['CO'][0]-1))

    lisa['sink_en_13']=np.array(sink_enr_13)
    lisa['sink_en_17']=np.array(sink_enr_17)
    lisa['sink_en_18']=np.array(sink_enr_18)
    return lisa
def cor_d_with_e(d,e):
    d=1000*((1+d/1000)/(1+e/1000)-1)
    return d

def hist(ax,residual,color):
    from scipy.stats import norm
    import matplotlib.pyplot as plt
    ran=max(residual)-min(residual)
    n, bins, patches = ax.hist(residual,bins=int( ran/0.5), density=True, orientation='horizontal')
    p = plt.setp(patches, 'facecolor', color , 'edgecolor', color, label=None,alpha=0.25 )
    # Create normal distributions for the line plots over the interval of the x-axis
    sc = residual.std()
    bins = np.arange( min(residual),  max(residual), 0.5)
    n = norm.pdf(bins, residual.mean(), residual.std())   
    ax.plot(n, bins, linestyle='-', color='k', linewidth=1,label=None)
    # ax.annotate(r'Uncertainty $\sigma=%.0f\,$\textperthousand' % np.std(residual) ,xy=(1.04*np.max(n),min(residual)-2 ))  # plot the PDF of the histogram in blue
    return

def keeling_co2(axes_array,xlims,mc=False,plot=False,echam_enrich=True):
    """TODO: Docstring for keeling.
    Returns
    -------
    TODO
    """
    LISA = lodautil.var_select(lodautil.flattened_LISA(), 'd18O(CO)')
    LISA=LISA[(LISA['p']<60)].reset_index()
    # mifers=np.array([-0.2,-0.13,-0.1])
    if echam_enrich:
        LISA= get_efeps_at(LISA)
        d3=cor_d_with_e(LISA['d13C(CO)'],LISA['sink_en_13'])
        d8=cor_d_with_e(LISA['d18O(CO)'],LISA['sink_en_18'])
    else:
        d3=LISA['d13C(CO)']
        d8=LISA['d18O(CO)']
    co=LISA['CO']
    if mc:
        c13=[]
        o18=[]
        for i in range(10000):
            random_eps13=np.random.normal(0.0,0.5,3)
            random_eps18=np.random.normal(0.0,0.5,3)
            d3=cor_d_with_e(LISA['d13C(CO)'],LISA['sink_en_13']+random_eps13)
            d8=cor_d_with_e(LISA['d18O(CO)'],LISA['sink_en_18']+random_eps18)
            c13.append(mc_analysis(co,d3,3,0.5))
            o18.append(mc_analysis(co,d8,3,0.5))
        # print('mean d18o: %.1f pm %.1f' % (np.mean(o18),np.std(o18)))
        # print('mean d13c: %.1f pm %.1f' % (np.mean(c13),np.std(c13)))
        hist(axes_array[0],np.array(c13),'k')
        hist(axes_array[0],np.array(o18),'k')
        axes_array[0].annotate('Monte-Carlo\n histograms for\n'+r'$\delta_{\textrm{source}}$',xy=(-0.01,0.5) , xycoords="axes fraction")
    if plot and mc:
        xerr=[]
        # for com in co: 
            # print(com)
            # xerr.append(np.std(1/np.random.normal(loc=com,scale=3,size=10000)))
        regres_and_plot(axes_array,1/co,d8,'k',":",xlims,r"${}^{18}\textrm{O}$",'d',res=np.std(np.array(o18)),xerr=3/co**2,yerr=[0.5]*3)
        regres_and_plot(axes_array,1/co,d3,'k',"-.",xlims,r"${}^{13}\textrm{C}$",'o',res=np.std(np.array(c13)),xerr=3/co**2,yerr=[0.5]*3)
    return 

def regres_and_plot(axes,x,y,color,linestyle,xlims,label,marker,res,xerr,yerr): 
    x, y, xerr = zip(*sorted(zip(x, y,xerr)))
    conf = 0.68
    fitparams, r2, fittedvalues, cb_low, cb_upp, pb_low, pb_upp, ce,f_pvalue = scantools.regression( x, y, conf=conf)
    # print((ce[:,0]-ce[:,1])/2)
    axes[1].errorbar(x, y, xerr=xerr,yerr=yerr,marker=marker, linestyle='', color=color,label=label+' data')
    xp=np.array(*xlims)
    axes[1].plot(xp, fitparams[1]*xp+fitparams[0], color=color, linestyle=linestyle,label='regression')
    axes[1].annotate(r'$\delta_{\textrm{source}}($%s$)=%.0f\pm%.0f\,$ \textperthousand' % (label,fitparams[0],res), xy=(0, fitparams[0]), xycoords='data',
            xytext=(0.02, 0.5*fitparams[0]), textcoords='data',
            va='top', ha='left',
            arrowprops=dict(arrowstyle="->"))
    return
def mc_analysis(x,y,x_sig,y_sig):
    x, y = zip(*sorted(zip(x, y)))
    x+=np.random.normal(0.0,x_sig,3)
    y+=np.random.normal(0.0,y_sig,3)
    conf = 0.68
    fitparams, r2, fittedvalues, cb_low, cb_upp, pb_low, pb_upp, ce,f_pvalue = scantools.regression( 1/x, y, conf=conf)
    return fitparams[0]
# def keeling_co2(axes_array,echam_enrich=False):
#     """TODO: Docstring for keeling.
#     Returns
#     -------
#     TODO
#     """
#     LISA = lodautil.var_select(lodautil.flattened_LISA(), 'd18O(CO)')
#     LISA=LISA[(LISA['p']<60)].reset_index()
#     LISA= get_efeps_at(LISA)
#     # mifers=np.array([-0.2,-0.13,-0.1])
#     if echam_enrich:
#         d3=cor_d_with_e(LISA['d13C(CO)'],LISA['sink_en_13'])
#         d8=cor_d_with_e(LISA['d18O(CO)'],LISA['sink_en_18'])
#     else:
#         d3=LISA['d13C(CO)']
#         d8=LISA['d18O(CO)']
#     scantools.statplot(axes_array[0],1/LISA['CO'],d8)
#     scantools.statplot(axes_array[1],1/LISA['CO'],d3)
#     return 
#
# Here start the utils
#
def daywindow(datestr,window_of_oppertunity):
    """TODO: Docstring for daywindow.
    :returns: TODO
    datstr is a date string yyyymmdd
    window_of_oppertunity: int, number of days before and after which is in de window
    """
    dt=pd.to_datetime(datestr,format="%Y%m%d")
    allowed_dates=[]
    for i in range(-window_of_oppertunity,window_of_oppertunity+1):
        allowed_dates.append((dt+pd.to_timedelta(i,unit='day')).strftime("%Y%m%d"))
    return allowed_dates

def echam_correct_fractions(echam_results):
    fCO2inCO = echam_results['FHVCO']/echam_results['CO'] 
    fCH4inCO = echam_results['FCMCO']/echam_results['CO'] 
    fO1DinCO = echam_results['FMO1DCO']/echam_results['CO'] 
    # Avoid bias because of double counting. This computation is biased since the
    # life time of species is different. E.G. FOZCO2 might be different at the time
    # that fCO2inCO was created. since CO will produce CO2 when transported downwards,         
    
    # the ozone tagged scheme was flawed. remove this?
    try:
        FOZviaCO2=(echam_results['FOZCO2']/echam_results['CO2'])*(fCO2inCO)
        fO3inCO=echam_results['FOZCO']/echam_results['CO']
        fO3inO2=echam_results['FOZO2']/echam_results['O2']
        # Should we or shouldn't we count the FCO2 that gets back? 
        fO3inCO=fO3inCO-FOZviaCO2-fO1DinCO-(fCH4inCO-fO1DinCO)*fO3inO2
    except KeyError:
        fO3inCO=np.array([np.nan]*len(fO1DinCO))    

    # FOZCO2 is likely to increase. 
    # fozo1d/o1d=1 always. so is unbiased 
    fO1DinCO=fO1DinCO-fCO2inCO*(echam_results['FMO1DCO2']/echam_results['CO2']) #<TAGJ41002FMO1D> is in SICM5.eqn 2020-12-15 15:16:52
    # Also FCMCO2+hv gets back into CO
    # all fO1d is via ch4
    fCH4inCO=fCH4inCO-fO1DinCO-fCO2inCO*(echam_results['FCMCO2']/echam_results['CO2'])    # baaaaaaaaaaaaaaaaaaaaad programming:. 
    # print(fCH4inCO+fCO2inCO+fO1DinCO+fO3inCO)
    f_res=1-(fCH4inCO+fCO2inCO+fO1DinCO)
    return fCH4inCO,fCO2inCO,fO1DinCO,f_res

def calc_co_ch4():
    co2src=12.05
    LISA=lodautil.var_select(lodautil.flattened_LISA(),'d18O(CO)')
    LISA=LISA[(LISA['p']<60)]
    times,dates=lodautil.get_unique_dates(LISA)
    ncfid=lodautil.get_ncfid(interpolated=True)
    O1D=[]
    dch4=[]
    for t,dat in zip(times,dates):
        COx=lodautil.echam.get_ECHAM_tt(t,'tracer_gp_CO',ncfid)
        HVCO=lodautil.echam.get_ECHAM_tt(t,'tracer_gp_FHVCO',ncfid)/COx
        fO1D=lodautil.echam.get_ECHAM_tt(t,'tracer_gp_FMO1DCO',ncfid)/COx
        fM=lodautil.echam.get_ECHAM_tt(t,'tracer_gp_FCMCO',ncfid)/COx
        press=lodautil.echam.get_ECHAM_pp(t,ncfid)
        mask=(press>1000)&(press<5000)
        co=LISA['CO'][(LISA['Date']==dat)]
        co18o=LISA['d18O(CO)'][(LISA['Date']==dat)]
        hvco=interp1d(COx[mask]*1E9,HVCO[mask],kind='nearest',fill_value='extrapolate')(co)
        fm=interp1d(COx[mask]*1E9,fM[mask],kind='nearest',fill_value='extrapolate')(co)
        O1D.append(interp1d(COx[mask]*1E9,fO1D[mask],kind='nearest',fill_value='extrapolate')(co))
        # print(1-fm,fm)
        dch4.append((co18o-(1-fm)*co2src)/(fm))
    return dch4,O1D
#
# Inversion LISA + ECHAM data
#
def get_matrix(lisa,ncfid,mode='pipe',method='hyb'):
    """get_matrix.
    Will obtian a matrix of fractions
    Each fraction should be the source 
    Their will be N rows, which is corresponds to N observations
    Their will be M columns, wich corresponds to the number of sources 
    Parameters
    ----------
    lisa_times :
        lisa_times
    ch4 :
        ch4
    lisa_p :
        lisa_p
    """
    #  
    N=len(lisa)
    if mode =='season':
        A=np.empty((N,5))
    elif mode =='seasonpipe':
        
        A=np.empty((N,9))
    
    elif mode =='simple':
        A=np.empty((N,4))

    elif mode =='full':
        A=np.empty((N,N+3))
    else:
        A=np.empty((N,6))
    month=None
    loc=None
    for i,lisa_t,lisa_p,ch4,date in zip(range(N),lisa['ECHAM_time'],100*lisa['p'],lisa['CH4'],lisa['Date']):
        if (mode=='season' )|( mode=='seasonpipe'):
            month=date[5:7]
        if mode=='full':
            loc=i
        # print(lisa_t,[lisa_p],mode,month,method,[ch4],loc)
        # print(get_fractions(lisa_t,[lisa_p],ncfid,mode,month=month,method=method,ch4=[ch4],loc=loc))
        A[i,:]=get_fractions(lisa_t,[lisa_p],ncfid,N,mode,month=month,method=method,ch4=[ch4],loc=loc)
    return A

def alpha_from_deltas(d_source,d_product,standard):
    """TODO: Docstring for get_alpha.
    Returns
    -------
    TODO

    """
    r_s=stisolib.delta_to_ratio(d_source,standard)
    r_p=stisolib.delta_to_ratio(d_product,standard)
    alpha = r_p/r_s
    return alpha 

def calc_model_alphas(d):
    """TODO: Docstring for calc_model_alphas.
    Returns
    -------
    TODO

    """
    
    r=len(d) 
    Sources=np.append([atmos.CO2d18,atmos.O2d18,atmos.O1Dd18],[0]*(r-3))
    alphas=alpha_from_deltas(Sources,d,"VSMOW18")

    return alphas

def get_fractions(lisa_time,lisa_p,ncfid,lenlisa,mode='pipe',month=None,loc=None,**kwargs):
    """function that does slol 

    Parameters
    ----------
    lol : TODO

    Returns
    -------
    TODO

    """
    echamy=['CO2','CO','FHVCO','FCMCO','FMO1DCO','FCMCO2','FMO1DCO2','O2','FOZO2']
    # data = lisa_data , time is t for singel observation
    # we should be able to realy retrive one time of observation
    echam_data=lodautil.get_echam_tracers_gp(lisa_time,lisa_p,echamy,ncfid,**kwargs)
    fch4,fco2,fo1d,_=[float(value) for value in echam_correct_fractions(echam_data)]

    # fch4_o1d=3*fo1d
    # fch4=fch4-fch4_o1d
    # fo1d=1.26*fo1d
    # fch4=fch4+3*fo1d

    res=1-fco2-fo1d-fch4
    if mode=='simple': 
        fractions=np.array([fco2,fch4,fo1d,res])

    if mode=='full': 
        res_array=np.zeros(lenlisa)
        res_array[loc]=res
        fractions=np.append(np.array([fco2,fch4,fo1d]),res_array)
    if mode=='pipe': 
        fpipe_high , fpipe_mid , fpipe_low =0,0,0
        if lisa_p[0]<6000:
            fpipe_high=res
        elif lisa_p[0]<10000 and lisa_p[0]>6000:
            fpipe_mid=res
        else:   
            fpipe_low=res
        fractions=np.array([fco2,fch4,fo1d,fpipe_high,fpipe_mid,fpipe_low])
    if mode=='season':
        f_apr , f_sep=0,0
        if month == '04':
            f_apr=res
        else:
            f_sep=res
        fractions=np.array([fco2,fch4,fo1d,f_apr,f_sep])
    if mode=='seasonpipe':
        fpipe_apr_low , fpipe_apr_mid , fpipe_apr_high , fpipe_sep_low , fpipe_sep_mid , fpipe_sep_high=0,0,0,0,0,0
        if month == '04':
            if lisa_p[0]<6000:
                fpipe_apr_high=res
            elif lisa_p[0]<10000 and lisa_p[0]>6000:
                fpipe_apr_mid=res
            else:   
                fpipe_apr_low=res
        else:
            if lisa_p[0]<6000:
                fpipe_sep_high=res
            elif lisa_p[0]<10000 and lisa_p[0]>6000:
                fpipe_sep_mid=res
            else:   
                fpipe_sep_low=res
        fractions=np.array([fco2,fch4,fo1d,fpipe_apr_low,fpipe_apr_mid ,fpipe_apr_high ,fpipe_sep_low,fpipe_sep_mid,fpipe_sep_high])
    return fractions

def calc_d_r_term(r_term,alpha=1,standard='VSMOW18'):
    r=(r_term/(alpha-alpha*r_term))
    dvalue =stisolib.ratio_to_delta(r,standard)
    return dvalue 

def calc_r_term(dvalue,alpha=1,standard='VSMOW18'):
    r=stisolib.delta_to_ratio(dvalue,standard)
    r_term=(alpha*r)/(1+alpha*r)
    return r_term 

def result_to_d(x,isotope):
    N=len(x)
    result=np.empty(N)
    _,k=get_keys(isotope)
    for i in range(0,N):
        result[i]=calc_d_r_term(x[i],standard=k)
    return result

def change_fraction(pos,factor,sacrafice,A):
    Aprime=A.copy()
    for i in range(0,len(A)):
        oldf=A[i,pos]
        newf=factor*A[i,pos]
        dif=newf-oldf
        # Check if sacrafice belongs to fmid/fpipe/ftrop
        if sacrafice in [3,4,5]:
            sacrafice=np.nonzero(A[i,3:])[0][0]+3
            
        if abs(dif)>A[i,sacrafice]:
            # catch cases where the reduction is larger than sacrifice
            # captures sign)
            dif=(dif/abs(dif))*A[i,sacrafice]
        Aprime[i,sacrafice]-=dif
        Aprime[i,pos]+=dif
    return Aprime

def get_keys(isotope):
    d={"18O":['d18O(CO)','VSMOW18'],"13C":['d13C(CO)','VPDB13']}
    lisak,st=d[isotope]

    return lisak,st

def get_obs(lisa,isotope='18O',fractionation='conv',offset=False,echam_enrich=False):
    """TODO: Docstring for get_obs.
    Returns
    -------
    TODO
    fractionation : str
        conv for conventioanl 3st for Sergey Gromov's 3-step model

    """
    lisak,st=get_keys(isotope)
    N=len(lisa)
    obs=np.empty(N)
    for i,d,p,T in zip(range(0,N),lisa[lisak],lisa['p'],lisa['T']):
        alpha=get_alpha(p*100,T,isotope,fractionation)
        if not offset==False:
            if offset==True:
                kick=np.random.normal(0,0.5) # 1 permil =2sigma 0.5 is one sigma
                d+=kick
            else:
                d+=offset

        if echam_enrich:
           # kick2=0.0
           kick2=np.random.normal(0,0.5)
           d=1000*((1+d/1000)/(1+(lisa['sink_en'][i]+kick2)/1000)-1)
                # d=d-lisa['sink_en'][i]
           # print(d)
        obs[i]=calc_r_term(d,alpha,st)
    return obs 

def get_alpha(p,T=None,isotope='13C',fractionation='conv'):
    if fractionation=='3st':
        k_oh_co, k_oh_13co, k_oh_c17o, k_oh_c18o =stisolib.co_3step_OH(p,T)
        if isotope=='13C':
            alpha=  k_oh_13co/k_oh_co
        elif isotope=='18O':
            alpha=  k_oh_c18o/k_oh_co
    if fractionation==1:
        alpha=1
    else:
        if isotope=='13C':
            alpha=stisolib.alpha_oh_c13(p)
        elif isotope=='18O':
            alpha=stisolib.alpha_oh_o18(p)
    return alpha

def add_lisa(axes,lisa,key,ykey='p',group_by='color',**kwargs):
    if group_by=='color':
        for dat, c in zip(np.unique(lisa['Date']), colors):
            mask = lisa['Date'] == dat
            scantools.plot_add(axes,lisa[key][mask], lisa[ykey][mask], marker='o', linestyle='-', color=c, label="Lisa "+dat,**kwargs)
    if group_by=='marker':
        for dat, m in zip(np.unique(lisa['Date']),markers):
            mask = lisa['Date'] == dat
            scantools.plot_add(axes,lisa[key][mask], lisa[ykey][mask], linestyle='-', marker=m, label="Lisa "+dat,**kwargs)
    return
def plot_dat_lisa(axes,data,lisa,ykey='p',lab='',**kwargs):
    for dat, c in zip(np.unique(lisa['Date']), colors):
        mask = lisa['Date'] == dat
        scantools.plot_add(axes,data[mask], lisa[ykey][mask],label=dat+' '+lab, argsort=False,marker='o', color=c, **kwargs)
    return

def compute_mif(x18_src_sig,A,lisa,miftype='mdf',alphas=None,res=None,fractionation='conv',echam_enrich=False):
    if miftype=='mdf':
        x17 = stisolib.calc_d17o_mdf(x18_src_sig)
        x_mod = calc_r_term(x17, standard='VSMOW17')
    elif miftype=='mif':
        x17 = x18_src_sig
        x_mod = calc_r_term(x17, standard='VSMOW17')
    elif miftype=='mdfalpha':
        alphas = alphas**stisolib.mdf_slope
        alphas[3:] = 1
        rest=stisolib.calc_d17o_mdf(np.array(x18_src_sig[3:]))
        x17 = np.append(np.array([atmos.CO2d17, atmos.O2d17, atmos.O1Dd17]), rest)#, 0.52*x18[5]])
        x_mod = calc_r_term(x17, alphas, standard='VSMOW17')
    elif miftype=='mifalpha':
        alphas = alphas**stisolib.mdf_slope
        alphas[3:] = 1
        rest=np.array(x18_src_sig[3:])
        x17 = np.append(np.array([atmos.CO2d17, atmos.O2d17, atmos.O1Dd17]), rest)#, 0.52*x18[5]])
        # print(x17)
        x_mod = calc_r_term(x17, alphas, standard='VSMOW17')
    r_term = A.dot(x_mod)
    # result = np.empty(len(r_term))
    if fractionation==1:
        result = calc_d_r_term(r_term,  standard='VSMOW17')
        # print(result)
        if echam_enrich:
            # print(lisa['sink_en_17'])
            result = 1000*( (1+result/1000)*(1+lisa['sink_en_17']/1000)-1 )
    elif fractionation=='conv':
        # print(lisa['p']*100)
        result = calc_d_r_term(r_term,stisolib.alpha_oh_o17(lisa['p']*100),  standard='VSMOW17')
    if not res==None:
        d18_obs_mod = calc_residual(A,res['x'], lisa,fractionation=fractionation)+lisa['d18O(CO)'] 

        mif = stisolib.calc_mif(result,d18_obs_mod)
    else:
        mif = stisolib.calc_mif(result,lisa['d18O(CO)'])
    error = stisolib.calc_mif_cor(mif)
    
    return mif,error

def run_inversion(isotope, interpolated=False,method='hyb',daymean=False,mode='season',fractionation='conv',offset=False,sens_obs=False,echam_enrich=False,bounds='free'):
    lisa = lodautil.var_select(lodautil.flattened_LISA(), 'd18O(CO)')
    lisa = lisa.loc[(lisa['p'] < 140 )&(lisa['CO']<70)]
    lisa=lisa.reset_index()
    lisa['ECHAM_time'], _ = lodautil.get_sample_dt(lisa)
    ncfid = lodautil.get_ncfid(interpolated=True, daymean=False)
    if echam_enrich:
        sink_enr=[]
        sink_enr_17=[]
        for t,p,ch4 in zip(lisa['ECHAM_time'],lisa['p'],lisa['CH4']): 
            echam_enr=lodautil.get_echam_tracers_gp(t,[p*100],['E18pCO','CO'],ncfid,method=method,ch4=[ch4])
            enr=echam_enr['E18pCO'][0]/echam_enr['CO'][0]
            sink_enr.append(1e3*(enr-1))

            echam_enr_17=lodautil.get_echam_tracers_gp(t,[p*100],['E17pCO','CO'],ncfid,method=method,ch4=[ch4])
            enr_17=echam_enr_17['E17pCO'][0]/echam_enr['CO'][0]
            sink_enr_17.append(1e3*(enr_17-1))
        lisa['sink_en']=np.array(sink_enr)
        lisa['sink_en_17']=np.array(sink_enr_17)
        # print(lisa['sink_en'])
        # lisa = lisa.loc[(lisa['sink_en'] > -15)]
        lisa=lisa.reset_index()
    b = get_obs(lisa, isotope=isotope, fractionation=fractionation,offset=offset,echam_enrich=echam_enrich)
    A = get_matrix(lisa,  ncfid, mode=mode, method=method)
    bh,bl=get_bounds(isotope,len(A[0]),bounds=bounds)
    res = lsq_linear(A, b, bounds=(bl,bh),method='bvls',tol=1e-20 ,max_iter=1000)
    # print(res)
    residual = calc_residual(A, res['x'], lisa, isotope=isotope, fractionation=fractionation)
    xbase = result_to_d(res['x'], isotope=isotope)

    if sens_obs==True:
        sens_obs=np.empty((len(lisa),len(A[0])))
        for i in range(0,len(lisa)):
            # lisa_prime=lisa.drop([i])
            b_prime = np.delete(b,i)#get_obs(lisa_prime, isotope=isotope, fractionation=fractionation,offset=offset,echam_enrich=echam_enrich)
            # print(len(b))
            A_prime = np.delete(A,i,axis=0)#get_matrix(lisa_prime,  ncfid, mode=mode, method=method)
            # print(len(A))
            # bh,bl=get_bounds(isotope,len(A_prime[0]),bounds=bounds)
            # residual = calc_residual(A, res['x'], lisa_prime, isotope, fractionation)
            res_prime = lsq_linear(A_prime, b_prime, bounds=(bl,bh),method='bvls', tol=1e-20,max_iter=1000)
            sens_obs[i] = result_to_d(res_prime['x'], isotope=isotope)
            # print(residual+lisa_prime)
        # print(np.mean(sens_obs.T,axis=1))
        # print(np.std(sens_obs.T,axis=1))
        return xbase,res,residual,lisa,A,b,sens_obs
    else:
        return xbase,res,residual,lisa,A,b

def get_bounds(isotope,lenobs,bounds='free'):
    _,standard=get_keys(isotope)
    # print(bounds)
    if bounds=='free':
        bh = np.array([calc_r_term(10000,1,standard)] *lenobs)
        bl = np.array([calc_r_term(-1000,1,standard)] *lenobs)
    elif bounds=='res':
        bh = np.append(np.array([calc_r_term(200,1,standard),calc_r_term(200,1,standard),calc_r_term(1000,1,standard)]),np.array([calc_r_term(24,1,standard)] *(lenobs-3)))
        bl = np.append(np.array([calc_r_term(-200,1,standard),calc_r_term(-200,1,standard),calc_r_term(-1000,1,standard)]),np.array([calc_r_term(-0,1,standard)]*(lenobs-3)))
    elif bounds=='strict':
        bh = np.append(np.array([calc_r_term(200,1,standard),calc_r_term(15,1,standard),calc_r_term(1000,1,standard)]),np.array([calc_r_term(24,1,standard)] *(lenobs-3)))
        bl = np.append(np.array([calc_r_term(-200,1,standard),calc_r_term(-5,1,standard),calc_r_term(-1000,1,standard)]),np.array([calc_r_term(0,1,standard)]*(lenobs-3)))
    elif bounds=='bt':
        bh = np.append(np.array([calc_r_term(200,1,standard),calc_r_term(0,1,standard),calc_r_term(1000,1,standard)]),np.array([calc_r_term(24,1,standard)] *(lenobs-3)))
        bl = np.append(np.array([calc_r_term(-200,1,standard),calc_r_term(-5,1,standard),calc_r_term(-1000,1,standard)]),np.array([calc_r_term(0,1,standard)]*(lenobs-3)))
    elif bounds=='onlych4':
        bh = np.append(np.array([calc_r_term(200,1,standard),calc_r_term(0,1,standard),calc_r_term(1000,1,standard)]),np.array([calc_r_term(100,1,standard)] *(lenobs-3)))
        bl = np.append(np.array([calc_r_term(-200,1,standard),calc_r_term(-5,1,standard),calc_r_term(-1000,1,standard)]),np.array([calc_r_term(0,1,standard)]*(lenobs-3)))

    elif bounds=='co2':
        bh = np.append(np.array([calc_r_term(34,1,standard),calc_r_term(0,1,standard),calc_r_term(1000,1,standard)]),np.array([calc_r_term(100,1,standard)] *(lenobs-3)))
        bl = np.append(np.array([calc_r_term(33,1,standard),calc_r_term(-5,1,standard),calc_r_term(-1000,1,standard)]),np.array([calc_r_term(0,1,standard)]*(lenobs-3)))
    return bh,bl

def sens_fractions(isotope,xbase,lisa,A,b,percentage=10):
    factors = [1-percentage/100, 1+percentage/100]
    locs = [int(i) for i in range(0, len(A[0]))]
    d = np.array(np.meshgrid(locs, locs, factors))
    sets = np.rollaxis(d, 0, 4).reshape(len(factors)*len(locs)**2, 3)
    sets = sets[sets[:, 0] != sets[:, 1]]
    sens_results=[]
    src = ['CO2', 'CH4', 'O1D', 'f1', 'f2', 'f3','f4', 'f5', 'f6']
    bh,bl=get_bounds(isotope,len(xbase))
    for i in sets:
        i, j, f = i
        if j in [3,4,5,6,7,8,9]:
            # print(i)
            i = int(i)
            j = int(j)
            Aprime = change_fraction(i, f, j, A)
            res = lsq_linear(Aprime, b,bounds=(bl,bh),method='bvls', tol=1e-40,max_iter=1000)
            x = res['x']
            residual = calc_residual(A, x, lisa)
            x = result_to_d(x,isotope) - xbase
            x = list(x)
            x.append(src[i])
            x.append(src[j])
            x.append(f)
            np.array(x)
            sens_results.append(x)
    sens_results=np.array(sens_results)
    return sens_results
def sens_stats(sens_results):
     
    src = ['CO2', 'CH4', 'O1D', 'fhigh', 'fmid', 'flow']
    sens_stats={}
    factors=np.unique(sens_results.T[-1])
    for s in src:
        if not s in [ 'fhigh', 'fmid', 'flow']:
            for fac in factors:
                data=sens_results[( sens_results.T[-3]==s )&(sens_results.T[-1]==fac)]
                data=data.T
                sens_stats['$f(\ch{'+s+'})$ %s' % fac]={}
                sens_stats['$f(\ch{'+s+'})$ %s' % fac]['mean']=[np.mean(data[i].astype(float)) for i in [0,1,2]]
                sens_stats['$f(\ch{'+s+'})$ %s' % fac]['std']=[np.std(data[i].astype(float)) for i in [0,1,2]]
    return sens_stats

def src_sig_table(xbase,fname,i):
    if i=='18O':
        r=len(xbase)
        alphas = calc_model_alphas(xbase)

        epsilons = 1000*(alphas-1)
        alphas = np.append(alphas[:3], ['-']*(r-3))
        epsilons = np.append(epsilons[:3], ['-']*(r-3))

        xbases = np.append([r"$\delta^{18}\ch{O}$"], xbase)
        alphas = np.append([r"$\alpha$"], alphas)
        epsilons = np.append([r"$\varepsilon$"], epsilons)

        prec = np.array([1]*7)
        scantools.npa_to_tex_table(xbases, prec,fname)

        prec = np.array([3]*7)
        scantools.npa_to_tex_table(alphas, prec,fname)

        prec = np.array([1]*7)
        scantools.npa_to_tex_table(epsilons, prec,fname)
    else:
        pass
    return

def sens_results_to_table(sens_results,i):
    sensrcsig = open(config.TabDir+'sensitivity_src_sig_%s.tex' % i, 'w')
    for key in sens_results.keys():
        texline=[]
        texline.append(key)
        for m,s in zip( sens_results[key]['mean'],sens_results[key]['std']):
            # a='$%.2f\pm%.2f$' % (m,s)
            a='$%.1f$' % (m)
            texline.append(a)
        texline=np.array(texline)
        scantools.npa_to_tex_table(texline, 0,sensrcsig )
    sensrcsig.close()
    return

def plot_inversion(axes,residual,lisa,isotope,ykey='p',group_by='color',date=None,**kwargs):
    lisak,_=get_keys(isotope)
    model=residual+lisa[lisak]
    if not date==None:
        mask = lisa['Date'] == date
        model=model[mask]
        lisa=lisa[mask]
    if group_by=='color':
        for dat, c in zip(np.unique(lisa['Date']), colors):
            mask = lisa['Date'] == dat
            scantools.plot_add(axes,model[mask], lisa[ykey][mask],  argsort=False,color=c, **kwargs)

    if group_by=='marker':
        for dat, m in zip(np.unique(lisa['Date']),markers):
            mask = lisa['Date'] == dat
            scantools.plot_add(axes,model[mask], lisa[ykey][mask],  argsort=False,marker=m, **kwargs)
    return

def calc_residual(A,x,lisa,isotope='18O',fractionation='conv'):
    """TODO: Docstring for get_obs.
    Returns
    -------
    TODO

    """
    results=np.dot(A,x)
    N=len(results)
    residual=np.empty(N)
    lisak,st=get_keys(isotope)
    for i,d,r,p,T in zip(range(0,N),lisa[lisak],results,lisa['p'],lisa['T']):
        alpha=get_alpha(p*100,T,isotope,fractionation)
        if 'sink_en' in lisa.keys():
            d=1000*((1+d/1000)/(1+lisa['sink_en'][i]/1000)-1)
            # print(d)
        residual[i]=calc_d_r_term(r,alpha,standard=st)-d
    return residual
#
# Figures
#
def echamfx(axes,var1,var2,interpolated=False):
    """echamFXinCO.

    Parameters
    ----------
    interpolated :
        interpolated
    alt :
        alt
    xlabel :
        xlabel
    ylabelname :
        ylabelname
    """
    LISA = lodautil.var_select(lodautil.flattened_LISA(), 'd18O(CO)')
    ncfid=lodautil.get_ncfid(interpolated,daymean=True)
    times,dates=lodautil.get_unique_dates(LISA)
    echamy=[var1 ,var2]
    for time,dat,c in zip(times,dates,colors):
        time=np.floor(time)+0.5 # Halfway through the day
        data=lodautil.date_select(LISA,dat)
        echam_data=lodautil.get_echam_tracers_gp(time,data['p']*100,echamy,ncfid,method='hyb',ch4=data['CH4'])
        f=(echam_data[var1]/echam_data[var2])
        axes.plot(f, data['p'] , color=c , marker='o' , linestyle='-'  , label='%s' % dat)
    return  

def echamfxinco(axes_array,interpolated=True,experiment='z4',method='hyb',ylabel='p',**kwargs):
    """echamFXinCO.

    Parameters
    ----------
    interpolated :
        interpolated
    alt :
        alt
    xlabel :
        xlabel
    ylabelname :
        ylabelname
    """
    ylabel=ylabel
    LISA = lodautil.var_select(lodautil.flattened_LISA(), 'd18O(CO)')
    ncfid=lodautil.get_ncfid(interpolated,experiment=experiment)
    times,dates=lodautil.get_unique_dates(LISA)
    echamy=['CO2' ,'CO','FHVCO','FCMCO','FMO1DCO','FOZCO','FOZCO2','FCMCO2','FMO1DCO2','FOZO2','O2']
    for time,dat,c in zip(times,dates,colors):
        data=lodautil.date_select(LISA,dat)
        # 12:00 utc:
        press=lodautil.echam.get_ECHAM_pp(time,ncfid)
        # Tracers 
        echam_data=lodautil.get_echam_tracers_gp(time,data['p']*100,echamy,ncfid,method=method,ch4=data['CH4'])
        fractions=echam_correct_fractions(echam_data)

        for ax,frac in zip(axes_array.ravel(),fractions):
            scantools.plot_add(ax,frac, data[ylabel] ,argsort=False, color=c ,  label='%s' % ( dat),**kwargs)
    return 

