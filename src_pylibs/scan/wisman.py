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
import os
import time
from glob import glob
from io import StringIO

import atmos
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import config
import stisolib
from scipy import stats
from scipy.interpolate import interp1d
from scipy.odr import *
from scipy.optimize import curve_fit
from scipy.optimize import nnls as nnls

def mixing_keeling(inverse_mole,oxygen,carbon,mole_err,ox_er,co_er,save=False):
    """mixing_keeling.

    Produces a keeling plot, based on the input data.
    inverse mole is the inverse of the mole fractions in ppb -1
    oxigen are oxygen isotopes. carbon carbon isotopes
    set save=string to save the figure

    Parameters
    ----------
    inverse_mole : array 
        inverse mole fractions, array 
    oxygen : array
        oxygen delta values in per mill
    carbon : array
        carbon delta values in per mill
    mole_err : array
        mole_err error on the inverse mole fractions
    ox_er : array
        ox_er error on the oxygen delta values, same unit as the is the delta values
    co_er : array
        ox_er error on the delta values, same unit as the is the delta values
    save :  
        if save is not false, wil save the figure with the name parsed into config.figDir/<save>.pdf 
    """

    CO_inf=inverse_mole
    C13=carbon
    O18=oxygen
    CO_err=mole_err
    C13_err=co_er
    O18_err=co_er
    def linfit(p,x):
        a,b=p
        return a*x+b
    print(stats.linregress(CO_inf,C13))
    print(stats.linregress(CO_inf,O18))
    #
    # =============================================================================
    # Fit C13 using ODR, which is accepts the error in both x and y for the least squares method
    # ODR is orthogonal distance regression.
    # =============================================================================
    lin_model=Model(linfit)                             # Define Model object to be used by ODR
    data=RealData(CO_inf,C13,sx=CO_err,sy=C13_err)      # dataset to be modeled by odr
    odr=ODR(data,lin_model,beta0=[0,0])                 # combine the previousley determined model data
    out=odr.run()                                       # run odr
    inter1=out.beta                                     # Optain the results from ODR
    err1=np.sqrt(np.diag(out.cov_beta))[1]              # optain the standard error of the fit from the diagonal of the covariance matrix
    out.pprint()
    # =============================================================================
    # Same for )18
    # =============================================================================
    lin_model=Model(linfit)
    data=RealData(CO_inf,O18,sx=CO_err,sy=O18_err)
    odr=ODR(data,lin_model,beta0=[0,0])
    out=odr.run()
    inter2=out.beta
    err2=np.sqrt(np.diag(out.cov_beta))[1]
    out.pprint()
    # =============================================================================
    # The fitted line x_model and y1 and y2 for plotting purposes
    # =============================================================================
    x_model=np.linspace(0,35,2)
    y1=linfit(inter1,x_model)
    y2=linfit(inter2,x_model)

    fig, axes_array=plt.subplots(1,2,figsize=[11,5])# Figure with predifine size
    # =============================================================================
    # Plotting using matplotilib
    # =============================================================================
    #axes_array[0].errorbar(CO_inf,C13,xerr=CO_err,yerr=C13_err,fmt='d',linestyle='-',color='sage')
    axes_array[0].errorbar(CO_inf,C13,xerr=CO_err,yerr=C13_err,fmt='d',linestyle='-',color='darkred')
    axes_array[0].plot(x_model,y1,'darkred')
    axes_array[0].set_ylabel(r'$\delta ^{13}$C  (\textperthousand VPDB)')
    axes_array[0].set_xlabel('1000/[CO]  (ppb$^{-1}$)')
    #axes_array[1].errorbar(CO_inf,O18,xerr=CO_err,yerr=O18_err,fmt='d',linestyle='-',color='sage')
    axes_array[1].errorbar(CO_inf,O18,xerr=CO_err,yerr=O18_err,fmt='d',linestyle='-',color='darkred')
    axes_array[1].plot(x_model,y2,'darkred')
    axes_array[1].set_ylabel(r'$\delta ^{18}$O (\textperthousand VSMOW)') #‰
    axes_array[1].set_xlabel(u'1000/[CO]  (ppb$^{-1}$)')

    axes_array[0].annotate(u'Intercept: ${0}\pm{1}$ (\\textperthousand VPDB)'.format(round(inter1[1],2),round(err1,2)),xy=(3,np.floor(inter1[1])))
    axes_array[1].annotate(u'Intercept: ${0}\pm{1}$ (\\textperthousand VSMOW)'.format(round(inter2[1],2),round(err2,2)),xy=(3,np.floor(inter2[1])))

    axes_array[0].set_title('(a)')
    axes_array[1].set_title('(b)')
    if save!=False:
        fig.savefig(config.FigDir+save+'.pdf',format='pdf',bbox_inches='tight')
    return inter1,inter2

def back_calc(temp,pres,co,t_tot,t_trop,dt,alt,oh=1.2E6 ,iso='false'):
    """back_calc.
     
    Analysing the effect of OH on the wildfire plume CO. Calculating backwards for t_tot
    first step is isentropic transport at t_tot-t_trop. at temp and pres. 
    Secondly vertical transport is simulated for a time t_trop, with timesteps dt
    Standard atmosphere at a certain altitudes computes pressure and temperature for the chemistry. Their is a jump in altitude where step 1 and step 2 interfere.

    optional arguement iso can be: 'C13', 'O17', 'O18' when the given CO is actually one of the isotopologues.
    how long in the troposphere Typical lifetime fo CO in plumes from
    publications used
    \citep{Mauzerall1998} OH concentration in smoke plume
    \citep{McCabe2001} rate constant of CO + OH reaction
    \citep{Gromov2013} for isotope fractionation constants

    Parameters
    ----------
    temp : float
        temperature in Kelvin
    pres : float
        pressure in Pa
    co : float
        Carbon monoxide mole fraction
    t_tot : float
        t_tot
    t_trop : float
        t_trop
    dt : float
        time step in seconds
    alt : float
        altiutde in km 
    oh : float
        OH number density in cm^-3
    iso : string
       iso options to calculate fractionation of the stable isotopes.
       Options are "C13", "O18", "O18", and 'false', default 'false'.
    
    Returns
    -------
    co_end_strat : float
        end result of the model computation in the stratosphere
    co_end
        end result of the model computation in the troposphere
    """
    if iso=='false':
        # creata null function that returns one
        def alpha(pres):
            return 1
    elif iso=='C13':
        alpha=stisolib.alpha_oh_c13
    elif iso=='O17':
        alpha=stisolib.alpha_oh_o17
    elif iso=='O18':
        alpha=stisolib.alpha_oh_o18
# =============================================================================
# ### step 1: horizpontal advection for the amount tstrat ###
# =============================================================================
    t_strat=t_tot-t_trop              # total time spent at pres 1 and temp 1
    oh=oh                             # ndens of oh in molecules per cm3 )-4 km: 2.7E6  4-8 km: 1.6E6 8-12km: 1.2E6
    k_oh=(1.57E-13+(3.54E-33)*atmos.ndens(temp,pres))*alpha(pres)            # Rate constant of co + oh
    t=0
    co_end_strat=[]
    while t<t_strat:
        co=co*atmos.ndens(temp,pres)
        co=co/np.exp(-k_oh*oh*dt)
        co=co/atmos.ndens(temp,pres)
        t+=dt

    co_end_strat=co  #result of back tracing in the stratosphere
# =============================================================================
# ### step 2: vertical advection for the amount ttot-tstrat ###
# =============================================================================
    w=alt/t_trop   # vertical speed
    tsim=0
    while tsim<t_trop:
        alt=alt-w*dt
        if alt>8.0:
            oh=1.2E6
        elif alt>4.0:
            oh=1.6E6
        else:
            oh=2.7E6
        pres,temp=atmos.Standard_atmos(alt*1000.)

        nden=atmos.ndens(temp,pres)
        k_oh=(1.57E-13+(3.54E-33)*nden)*alpha(pres)
        co=co*nden
        co=co/np.exp(-k_oh*oh*dt)
        co=co/nden
        tsim+=dt
    co_end=co
    return co_end_strat,co_end

# 2020-10-06 11:31:49 not used in the analysis: 
def forward_calc(temp,pres,co,t_tot,t_trop,dt,alt,iso='false'):
    """forward_calc.
    The same as back_calc but instead a forward calculation
    Parameters
    ----------
    temp : float
        temperature in Kelvin
    pres : float
        pressure in Pa
    co : float
        Carbon monoxide mole fraction
    t_tot : float
        t_tot
    t_trop : float
        t_trop
    dt : float
        time step in seconds
    alt : float
        altiutde in km 
    oh : float
        OH number density in cm^-3
    iso : string
       iso options to calculate fractionation of the stable isotopes.
       Options are "C13", "O18", "O18", and 'false', default 'false'.
    Returns
    -------
    co_end_strat : float
        end result of the model computation in the stratosphere
    co_end
        end result of the model computation in the troposphere
    """
    if iso=='false':
        def alpha(pres):
            return 1
    elif iso=='C13':
        alpha=stisolib.alpha_oh_c13
    elif iso=='O17':
        alpha=stisolib.alpha_oh_o17
    elif iso=='O18':
        alpha=stisolib.alpha_oh_o18

    w=alt/t_trop   # vertical speed
    tsim=0
    altitude=0
    # =============================================================================
    # ### step 2: horizpontal advection for the amount tstrat ###
    # =============================================================================
    while tsim<t_trop:
        if altitude>8.0:
            oh=1.2E6
        elif altitude>4.0:
            oh=1.6E6
        else:
            oh=2.7E6
        pres,temp=Standard_atmos(altitude*1000)
        nden=atmos.ndens(temp,pres)
        k_oh=(1.57E-13+(3.54E-33)*nden)*alpha(pres)
        co=co*nden
        co=co*np.exp(-k_oh*oh*dt)
        co=co/nden
        altitude+=w*dt
        tsim+=dt
    co_end_trop=co
    t_strat=t_tot-t_trop              # total time spent at pres 1 and temp 1
    oh=1.2E6                 # ndens of oh in molecules per cm3 )-4 km: 2.7E6  4-8 km: 1.6E6 8-12km: 1.2E6
    pres=200.                   # pressure im mbar
    temp=240.                   # temperature in kelvin
    k_oh=(1.57E-13+(3.54E-33)*ndens(temp,pres))*alpha(pres)            # Rate constant of co + oh
    co=co*ndens(temp,pres)
    co=co*np.exp(-k_oh*oh*t_strat)
    co=co/ndens(temp,pres)
    co_end_strat=co                                                    #result of back tracing in the stratosphere
    return co_end_trop,co_end_strat

def exp_mod(t,f_strat,Tend):
    """exp_mod.

    Parameters
    ----------
    t :
        time in seconds
    f_strat :
        fraction of stratospheric molecules
    Tend :
        total transport time in seconds
    
    Returns
    ------  
    dil_ratio : 
        the dilution ratio
    """
    k_ev=-np.log(1-f_strat)/Tend
    dil_ratio=np.exp(k_ev*t) 
    return dil_ratio 

def lin_mod(t,f_strat,Tend):
    """lin_mod.

    Parameters
    ----------
    t :
        time in seconds
    f_strat :
        fraction of stratospheric molecules
    Tend :
        total transport time in seconds
    
    Returns
    ------  
    dil_ratio : 
        the dilution ratio
    """
    k_ev=( 1/(1-f_strat) -1)/Tend
    dil_ratio=1+k_ev*t 
    return dil_ratio 

def sqrt_mod(t,f_strat,Tend):
    """sqrt_mod.

    Parameters
    ----------
    t :
        time in seconds
    f_strat :
        fraction of stratospheric molecules
    Tend :
        total transport time in seconds
    
    Returns
    ------  
    dil_ratio : 
        the dilution ratio
    """
    k_ev=(( 1/(1-f_strat) )**2-1)/Tend
    dil_ratio=np.sqrt(1+k_ev*t) 
    return dil_ratio 

def chem_mix_model_num(temp,pres,co,oh,co_bg,c13o_bg,co18_bg,C13O,C18O,dt,Tend,f_strat,mixingmodel):
    """chem_mix_model_num.
    nummerical method. was compared to the analytical method in chem_mix_model

    Parameters
    ----------
    temp :
        temperature in Kelvin
    pres :
        pressure in Pascal
    co :
        CO mole fraction in ppb internal conversion to cm-3
    oh :
        oh number densitye cm^-3
    co_bg :
        co_bg molefraction of the plume back ground
    c13o_bg :
        c13o_bg C13-delta value of background CO per mil
    co18_bg :
        co18_bg O18 delta value of backgournd CO per mil
    C13O :
        C13O C13-delta value of background CO per mil
    C18O :
        C18O O18 delta value of backgournd CO per mil
    dt :
        dt time step in seconds
    Tend :
        Tend total transport time in seconds
    f_strat :
        f_strat total stratoshperic fraction of air mixed into the plume at Tend
    mixingmodel :
        mixingmodel to be used. options are exp_mod, sqrt_mod, and lin_mod.
    """
    nden=atmos.ndens(temp,pres)
    C12O16=nden*co*10**(-9)
    #Ratio=C12O18/C12O16, then C12O16*Ratio=C12O18
    C13O16=np.repeat(C12O16*stisolib.delta_to_ratio(C13O,'VPDB13'),len(f_strat))
    C12O18=np.repeat(C12O16*stisolib.delta_to_ratio(C18O,'VSMOW18'),len(f_strat))
    C12O16=np.repeat(C12O16,len(f_strat))
    #Ratio=C12O18/C12O16, then C12O16*Ratio=C12O18
    k_co_oh=(1.57E-13+(3.54E-33)*nden)
    k_c13o_oh=k_co_oh*stisolib.alpha_oh_c13(pres)
    k_co18_oh=k_co_oh*stisolib.alpha_oh_o18(pres)
    
    CO_bg=nden*co_bg*10**(-9)
    C13O_bg=CO_bg*stisolib.delta_to_ratio(c13o_bg,'VPDB13')
    C18O_bg=CO_bg*stisolib.delta_to_ratio(co18_bg,'VSMOW18')
    T_tot=Tend
    OH=oh
#    counter=0
   # CO_ar=np.empty(Tend/dt)  
    while Tend>0:
        #Calculate Timedependt fraction of stratospheric inmixing
        f_plume=1-(mixingmodel(Tend+dt,f_strat,T_tot)-mixingmodel(Tend,f_strat,T_tot))/mixingmodel(Tend+dt,f_strat,T_tot)
        C12O16=C12O16/np.exp(-k_co_oh*OH*dt) # Chemistry back calculate for a small time step dt
        C12O16=(C12O16-(1-f_plume)*CO_bg)/f_plume  # mixing newplume=(1-f)*strat+fplume so backward: plume=(newplume-(1-f)*strat)/f
        C13O16=C13O16/np.exp(-k_c13o_oh*OH*dt) # Chemistry back calculate for a small time step dt
        C13O16=(C13O16-(1-f_plume)*C13O_bg)/f_plume  # mixing newplume=(1-f)*strat+fplume so backward: plume=(newplume-(1-f)*strat)/f
        C12O18=C12O18/np.exp(-k_co18_oh*OH*dt) # Chemistry back calculate for a small time step dt
        C12O18=(C12O18-(1-f_plume)*C18O_bg)/f_plume  # mixing newplume=(1-f)*strat+fplume so backward: plume=(newplume-(1-f)*strat)/f
#        CO_ar[counter]=C12O16[-1]
   #     counter+=1
        Tend-=dt
        
    C13=stisolib.ratio_to_delta(C13O16/C12O16,'VPDB13')
    O18=stisolib.ratio_to_delta(C12O18/C12O16,'VSMOW18')
    
    CO=(C12O16/nden)*10**9
#    CO=(CO_ar/nden)*10**9   
    return O18, C13, CO

def chem_mix_model(temp,pres,co,oh,co_bg,c13o_bg,co18_bg,C13O,C18O,dt,f_strat):
    """chem_mix_model.
    Mixing model as derived in Hooghiem2020.

    Parameters
    ----------
    temp :
        temperature in Kelvin
    pres :
        pressure in Pascal
    co :
        CO mole fraction in ppb internal conversion to cm-3
    oh :
        oh number densitye cm^-3
    co_bg :
        co_bg molefraction of the plume back ground
    c13o_bg :
        c13o_bg C13-delta value of background CO per mil
    co18_bg :
        co18_bg O18 delta value of backgournd CO per mil
    C13O :
        C13O C13-delta value of background CO per mil
    C18O :
        C18O O18 delta value of backgournd CO per mil
    dt :
        dt time step in seconds
    Tend :
        Tend total transport time in seconds
    f_strat :
        f_strat total stratoshperic fraction of air mixed into the plume at Tend

    Returns
    -------
    O18 : 
        The computed O18 value per mil
    C13 : 
        The computed C13 value per mil
    CO  :
        CO mole fraction in ppb 
    """
    nden=atmos.ndens(temp,pres)
    C12O16=nden*co*10**(-9)
    C13O16=C12O16*stisolib.delta_to_ratio(C13O,'VPDB13')
    C12O18=C12O16*stisolib.delta_to_ratio(C18O,'VSMOW18')

    k_co_oh=(1.57E-13+(3.54E-33)*nden)
    k_c13o_oh=k_co_oh*stisolib.alpha_oh_c13(pres)
    k_co18_oh=k_co_oh*stisolib.alpha_oh_o18(pres)
    
    k_ev=-np.log(1-f_strat)/dt
    OH=oh
   
    CO_bg=nden*co_bg*10**(-9)
    C13O_bg=CO_bg*stisolib.delta_to_ratio(c13o_bg,'VPDB13')
    C18O_bg=CO_bg*stisolib.delta_to_ratio(co18_bg,'VSMOW18')
    
    a=-k_ev-k_co_oh*OH
    b=k_ev*CO_bg
    
    C12O16=(C12O16+b/a)*np.exp(-a*dt)-b/a
    
    a=-k_ev-k_c13o_oh*OH
    b=k_ev*C13O_bg   
    C13O16=(C13O16+b/a)*np.exp(-a*dt)-b/a
    
    a=-k_ev-k_co18_oh*OH
    b=k_ev*C18O_bg
    C12O18=(C12O18+b/a)*np.exp(-a*dt)-b/a
    
    C13=stisolib.ratio_to_delta(C13O16/C12O16,'VPDB13')
    O18=stisolib.ratio_to_delta(C12O18/C12O16,'VSMOW18')
    
    CO=(C12O16/nden)*10**9
        
    return O18, C13, CO

def plot_result(results,fig=None,ax=None):
    """plot_result.
    Plots the set of monte carlo results
    Parameters
    ----------
    results : np.array
        results of the Monte Carlo simulation
    fig :
        matplotlib figure instance 
    ax :
        axex instance of matplotlib
    """
    if fig==None:
        fig,ax=plt.subplots(1,1)
        ax.hist(results.T[1],bins=100,alpha=0.6,density='True',label='Troposphere '+str(np.round(np.median(results.T[1])*100))+'$\pm$'+str(np.round(np.median(abs(results.T[1]-np.median(results.T[1])))*100)))
        ax.hist(results.T[2],bins=100,alpha=0.6,density='True',label='Stratosphere '+str(np.round(np.median(results.T[2])*100))+'$\pm$'+str(np.round(np.median(abs(results.T[2]-np.median(results.T[2])))*100)))
        ax.legend()
    else:
        ax.hist(results.T[1],bins=100,alpha=0.6,density='True',label='Troposphere '+str(np.round(np.median(results.T[1])*100))+'$\pm$'+str(np.round(np.median(abs(results.T[1]-np.median(results.T[1])))*100)))
        ax.hist(results.T[2],bins=100,alpha=0.6,density='True',label='Stratosphere '+str(np.round(np.median(results.T[2])*100))+'$\pm$'+str(np.round(np.median(abs(results.T[2]-np.median(results.T[2])))*100)))
        ax.legend()
 
    print(statistics.mode(np.round(results.T[1],3)))
   
    print(statistics.mode(np.round(results.T[2],3)))
    return fig,ax

def transform_end_members(plume,troposphere,stratosphere):
    """transform_end_members.
    A utilitiy that transform the end members into the right format
    for NNLS method 
    The endmembers ar transformed according to the solverd definition described in Hooghiem 2019. 

    Parameters
    ----------
    plume :
        plume CO, 
    troposphere :
        troposphere
    stratosphere :
        stratosphere
    Returns
    -------
    end_members 
    """
    p=np.array([1,plume[0],plume[0]*plume[1],plume[0]*plume[2]])
    t=np.array([1,troposphere[0],troposphere[0]*troposphere[1],troposphere[0]* troposphere[2]])
    s=np.array([1,stratosphere[0],stratosphere[0]*stratosphere[1],stratosphere[0]*stratosphere[2]])
    end_members=np.array([p,t,s]).T
    
    return end_members

def monte_carlo_solve(observation,end_members,weights):
    """monte_carlo_solve.
    Solves the NNLS problem. Computes the vector of unkowns, by minimalizing the
    squared residuals. 
    Parameters
    ----------
    observation :
        observation
    end_members :
        end_members
    weights :
        weights

    Returns
    -------
    fractions :
        the fractions of plume, stratosphere, and troposphere.
    error : 
        the normalized error from scipy.nnls routine 
    errorcalc :
        the absolute residuals
    """
    observation=np.array([1,observation[0],observation[0]*observation[1],observation[0]*observation[2]])
    fractions,error=nnls(np.diag(weights/observation).dot(end_members), np.diag(weights/observation).dot(observation))
    errorcalc=np.diag(weights/observation).dot(end_members).dot(fractions)-np.diag(weights/observation).dot(observation)
    return fractions,error,errorcalc

def print_results():
    """print_results.
    helper function the outputs the results
    """
    print( 'residuals squared',np.round(error,5))
    print( 'Sum mass balance',np.round(np.sum(fractions),2),' Troposphere ',np.round(np.sum(fractions[1]),2),' Stratosphere ',np.round(np.sum(fractions[2]),2)    )
    print( 'Residual mole fraction',np.round(residuals[0],2),'ppb')
    print( 'Residual d13C',np.round(residuals[1],2),'per mil')
    print( 'Residual d18O',np.round(residuals[2],2),'per mil')
    return 

def calc_residuals(observation,plume,troposphere,stratosphere,fraction):
    """calc_residuals.

    Gets the results from the NNLS and calculates the residual vector. The solver calculates normalized residuals; here the residuals are calculated without the normalization.

    Parameters
    ----------
    observation :
        observation
    plume :
        plume
    troposphere :
        troposphere
    stratosphere :
        stratosphere
    fraction :
        fraction computed by the nnls routine
    """
    mole_fractions=np.array([plume[0],troposphere[0],stratosphere[0]])
    iso_carbon=np.array([plume[1],troposphere[1],stratosphere[1]])
    iso_oxygen=np.array([plume[2],troposphere[2],stratosphere[2]])

    helper=fraction*mole_fractions

    error_mole=observation[0]-np.sum(helper)
    error_carbon=observation[1]-np.sum(helper*iso_carbon)/np.sum(helper)
    error_oxygen=observation[2]-np.sum(helper*iso_oxygen)/np.sum(helper)
    
    residuals=[error_mole,error_carbon,error_oxygen]
    return residuals

def plot_residuals(residuals):
    """plot_residuals.

    Parameters
    ----------
    residuals :
        residuals

    Retruns 
    ------
    fig : 
        matplotlib figure instance
    """
    mole =residuals.T[0]   
    carbon=residuals.T[1]  
    oxygen=residuals.T[2]  
    fig,axes=plt.subplots(1,3)

    b=100
    axes[0].hist(mole,bins=b,density='True',alpha=0.6)
    axes[1].hist(carbon,bins=b,density='True',alpha=0.6)
    axes[2].hist(oxygen,bins=b,density='True',alpha=0.6)

    axes[0].set_xlabel('CO nmol mol$^{-1}$')
    axes[1].set_xlabel('$\delta^{13}$C\\textperthousand(VPDB)')
    axes[2].set_xlabel('$\delta^{18}$O \\textperthousand(VSMOW)')
    axes[1].set_title('Residuals: $Ax-b$')
    fig.tight_layout()
    return fig    
