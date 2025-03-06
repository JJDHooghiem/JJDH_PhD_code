#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 20 10:22:56 2018

@author: joram
"""
from glob import glob
import pandas as pd
import numpy as np
import os
import subprocess
import multiprocessing
import sys
import matplotlib
from io import StringIO
from datetime import datetime
import stisolib
# =============================================================================
# LISA data assimilation
# =============================================================================

def LoadLisa(path):
  
    #path='2017-04-26_LISA_flight.csv'
    with open(path,'r') as result:
        headerstring=result.read()
        header,data=headerstring.split('End of header information\n')
        data = StringIO(data)
        data = pd.read_csv(data, sep=",")
        unit_str, header=header.split('End of unit declaration\n')
    return unit_str,header,data
def import_LISA(LISA_dir):
    os.chdir(LISA_dir)
    files=glob('*/Processed/*flight*.csv')

    data={}
    for f in files:
        date=f.split('/')[0].split('_S')[0]
        unit_str,header,df=LoadLisa(f)
        
        data[date]=df
    return data
def check_COstab(data):
    data=data
    data_to_kill=[]
    for dat in data:
        if not 'd13C(CO)' in data[dat].keys():
            print( 'deleting '+dat+' from the dataset to be modelled')
            data_to_kill.append(dat)
    for dat in data_to_kill:
        del(data[dat])
    print(data.keys())
    return data
def prep_input_old(DATA_DICT,ini_con):
    '''
    Take in data from LISA-sampler 
    ?CO2 bias in LISA
    Which data to use for CO2 stable isotopes? ask Farilde
    '''
    DATA_DICT=check_COstab(DATA_DICT)  
    data_set=[]
    for key in DATA_DICT.keys():
        data=DATA_DICT[key]
        date=key
        times=['w','w','w','s','s','s','s','s','s','w','w','w']
        for i in range(len(data)):
    #kpp global parameters:
            flight_variables={}
            flight_variables['date']=date
            flight_variables['ALT']=data['Altitude'][i]
            flight_variables['PRES']=data['Weighted p(mbar)'][i]
            flight_variables['TEMP']=data['Temperature'][i]
            flight_variables['LAT']=data['Lat'][i]
            flight_variables['LON']=data['Lon'][i]
            flight_variables['LEV']=obtain_jval_lev(flight_variables['PRES'])
            flight_variables['CFACTOR']=ndens(flight_variables['TEMP'],flight_variables['PRES'])
            flight_variables['CAIR']=flight_variables['CFACTOR']
            # handle chemistry

            df=ini_con
            df.loc[df['Species']=='CH4','Value']=data[ 'CH4'][i]
            df.loc[df['Species']=='CO2','Value']=data[ 'CO2'][i]
            CH4=float(df['Value'][df['Species']=='CH4'])
            Bry,Cly,NOy=initialize_chemistry(CH4)
            df.loc[df['Species']=='HBr','Value']=Bry
            df.loc[df['Species']=='HCl','Value']=Cly
            df.loc[df['Species']=='HNO3','Value']=NOy
            df.loc[df['Species']=='H2O','Value']=h2o_ppm(data[ 'Relative Humidtiy'][i]/100,flight_variables['TEMP'], flight_variables['PRES'])
            df.loc[df['Species']=='_13_CH4','Value']=ch4_to_c13(data[ 'CH4'][i],times[int(date.split('_')[1])])
            df=pre_process(df)
            for key,value in zip(df['Species'],df['Fractions']):
                flight_variables[key]=value
            data_set.append(flight_variables)
    return data_set



def get_N2O(CH4):
    '''
    From McKenna2002b. CH4 in ppm, here in ppb so devide by 1000.
    Valid range 0.48 ppm 1.84 ppm
    '''
    if 0.48>CH4/1000. or 1.84<CH4/1000.:
        print("CH4 outside confidence range")
    a,b,c,d,e=-82.71,323.7,-359.3 ,  340.2  , -96.37
    x=CH4/1000.
    N2Oy=a + b*x + c*x**2 + d*x**3 + e*x**4 
    return N2Oy

def get_NOy(N2O):
    """
    N2O NOy has several regimes

    """
    if 7.0<N2O or 145.0>N2O:
        a,b=10.33,8.798E-3
        NOy=a + b*N2O 
    elif 145.0<=N2O or 220.0>N2O:
        a,b,c,d,e=5.71,-2.28,11.8,-2.14,-1.04
        NOy=a + b*N2O + c*N2O**2 + d*N2O**3 + e*N2O**4 
    elif 220.0<=N2O or 315.0>N2O:
        a,b=20.7,-0.0644
        NOy=a + b*N2O 
    else:
        print("N2O outside confidence range")
    
    return NOy

def get_Bry(N2O):
    """

    Not recommended to use due to increase?
    """
    
    if 0<=N2O or 313.50>N2O:
        a,b,c=8.388,-0.4422,4.056E-3
        CFC11=a + b*N2O + c*N2O**2 
    
    if 10.0<=CFC11 or 260.0>CFC11:
        a,b,c,d,e=20.03,0.0041,-6.631E-4,3.188E-6,-6.713E-9
        Bry=a + b*CFC11 + c*CFC11**2 + d*CFC11**3 + e*CFC11**2 
    return Bry

def get_Cly(N2O):
    if 18<=N2O or 313.50>N2O:
        a,b,c=3344.0,1.497,-0.03637
        Cly=a + b*N2O + c*N2O**2 
    

    return Cly

def initialize_chemistry(CH4):
    N2O=get_N2O(CH4)
    Bry=get_Bry(N2O)
    Cly=get_Cly(N2O)
    NOy=get_NOy(N2O)
    return Bry,Cly,NOy

def filename_constructor(INPUT_DICTIONARY):        
    p=str(int(np.round(INPUT_DICTIONARY['PRES'])))
    name=INPUT_DICTIONARY['date']+'_'+p+'hPa'
    return name

# =============================================================================
# Runtime functions for automatic changing namelists
# =============================================================================
#%%
def change_kpp_input(INPUT_DICTIONARY,sim_name,kpp_dir):
    import shutil
    base_file=kpp_dir+'models/'+sim_name+'/strato_CO_base.def'
    f=open(base_file,'r')
    
#    f=open('/Users/joram/Documents/Software/Modelling/kpp_py_interface/Results_try/2017_09_06_159hPa/strato_CO_base.def','r')
    lines=f.readlines()
    f.close()

    infilenewval = kpp_dir+'models/'+sim_name+'/strato_CO_base.def'+'.new'
    f=open(infilenewval,'w')
 
    species=0
    for line in lines:
        newline = line
        for key in INPUT_DICTIONARY.keys():
            if key in line:
                if ';' and '=' in line: 
                    if line.split('=')[0].strip()==key:
                        newline = line.split('=')[0]+'\t='+'\t'+ str(INPUT_DICTIONARY[key])+';\n'    
                elif '=' in line:
                    newline = line.split('=')[0]+'\t='+' '+str(INPUT_DICTIONARY[key])+'\n'
        f.write(newline)
    f.close()
    shutil.copy(infilenewval, base_file)

    os.remove(infilenewval)
    return
def change_kpp_base_path(sim_name):
    import shutil

    f=open('strato_CO.kpp','r')
    lines=f.readlines()
    f.close()

    infilenewval = 'strato_CO.kpp'+'.new'
    f=open(infilenewval,'w')
    species=0
    for line in lines:
        newline = line
        if '#MODEL' in line:
            newline= '#MODEL      '+sim_name+'/'+'strato_CO_base\n'
        f.write(newline)
    f.close()
    shutil.copy(infilenewval, 'strato_CO.kpp')
    os.remove(infilenewval)
    return

# =============================================================================
# Atmosphere and chemistry funcitons 
# =============================================================================

def obtain_jval_lev(pres):
    from scipy.interpolate import interp1d as interpolate
    jval_levs=np.linspace(1,19,19) 

    jval_pres = np.array([  #Pa
        1000., 3000., 5040., 7339., 10248., 14053., 18935., 24966., 32107., 
        40212., 49027., 58204., 67317., 75897., 83472., 89631., 94099.,     
        96838., 98169. ])/100
    lev=float(interpolate(jval_pres,jval_levs,fill_value="extrapolate")(pres))
    return lev



#varspecies=(''.join(varspecies))
#varspecies=varspecies.replace('\n','').replace('(r)','').replace('(n)','').strip()
#varspecies = " ".join(re.replace("\s+",'t' varspecies, flags=re.UNICODE))
def ndens(temp,pres):
    '''
    takes in pressure in mbar, T in kelvin and calculates the local number density
    '''
    
    ndens=pres*100./(8.3144598*temp) #(MOL/M3) Gas constant (48) kg m2 mol−1 K−1 s−2 gas constant in SI units 
    ndens=ndens*6.022140758e+23/10**6 #(molecules per cm3 )
    return ndens

def h2o_ppm(h2o,T,p):
    '''
    Calculates the mole fraction from temperature (K) pressure and RH
    according to saturation presse ps = 6.11 * exp(0.067*T) where T is in celcius
    p_satu is in hPa or mbar
    '''
    p_satu=6.11*np.exp(0.067*(T-273.15))
    p_h2o=p_satu*h2o
    h2o_pct=1E6*p_h2o/p
    return h2o_pct

#      ( (p_temp > tmelt) .OR. (l_liquid.AND.(p_temp > lowlim)) ) ) THEN
#      ! water vapor saturation pressure over liquid:
#      psat_mk = EXP( 54.842763_dp - 6763.22_dp/p_temp &
#        - 4.21_dp*LOG(p_temp) + 0.000367_dp*p_temp    &
#        + TANH(0.0415_dp*(p_temp-218.8_dp))           &
#        * (53.878_dp - 1331.22_dp/p_temp              &
#        - 9.44523_dp*LOG(p_temp) + 0.014025_dp*p_temp) )
#    ELSEIF ((p_temp <= tmelt).AND.(.NOT.l_liquid).AND.(p_temp > lowlim)) THEN
#      ! water vapor saturation pressure over ice:
#      psat_mk = EXP( 9.550426_dp - 5723.265_dp/p_temp &
#        + 3.53068_dp*LOG(p_temp) - 0.00728332_dp*p_temp )
#    ELSE
#      WRITE(*,'(A,F10.3,A,F10.3,A,F10.3,A)') '  WARNING psat_mk: &
#        & temperature (', p_temp, ') out of valid temperature range [', &
#        lowlim, ',', uplim, ']'
def ch4_to_c13(CH4,time):
    '''
    Function that transforms methane mole fraction of methane into C13 (CH4) in per mill VPDB
    

        
    Parameters
    ----------
    CH4 : array_like
        Array containing mole fraction to be calculated
    time : string
        string specifying the type of profile:
        'wv'    'Winter Vortex'
        'w'     'Winter_non_vortex'
        's'     'Summer'
        'es'    'Extended summer'   
                
    Returns
    -------
    C13(CH$) : array_like
        the modelled arctic profile of c13ch4
            
    '''
    
    key=time
    opt={
        'wv': [-3.54574878461, -0.059925867126, 2.90405008109e-05, -5.18519551365e-09],
        'w': [-3.497122633, -0.0723283471856, 4.4351782608e-05, -9.99956105036e-09],
        's': [-4.10876345315, -0.0611286350897, 3.12909478767e-05, -6.02819339316e-09],
        'es':[-1.63863220447, -0.0673637996103, 3.65518611225e-05, -7.45099020146e-09]}
    if type(CH4)==np.ndarray:
        C13_CH4=opt[key][0]+opt[key][1]*CH4+opt[key][2]*CH4**2+opt[key][3]*CH4**3
    else:
        CH4=np.array(CH4)
        C13_CH4=opt[key][0]+opt[key][1]*CH4+opt[key][2]*CH4**2+opt[key][3]*CH4**3
    return C13_CH4
# =============================================================================
# Isotope pre_processor
# =============================================================================
def pre_process(DATA):
    ini_con=DATA
    ini_con['Fractions']=np.repeat(0.0,len(ini_con))

    for fam in np.unique(ini_con['Family']):
        
        selected=ini_con['Family']==fam #family set of isotopologues to be calculated
        fam_set=ini_con[selected]
        
        carbon_rlist=[]     #Required for RSUM
        oxygen_rlist=[]     #
        
        weights=[]
        rlist=[]
        
        carbon_weights=[]
        oxygen_exponent=0
        carbon_exponent=0
#        print(fam_set)
        for spec,value,unit,weight in zip(fam_set['Species'],fam_set['Value'],fam_set['Unit'],fam_set['Weight']):

            if spec!=fam:
#                print(unit)
                weights.append(weight)
                if unit=='VPDB13':
                    rlist.append(delta_to_ratio(value,unit))
                    carbon_rlist.append(delta_to_ratio(value,unit))
                    carbon_weights.append(weight)
                    carbon_exponent=weight
                elif unit=='VSMOW17' or unit=='VSMOW18':
                    rlist.append(delta_to_ratio(value,unit))
                    oxygen_rlist.append(delta_to_ratio(value,unit))
                    oxygen_exponent=weight
            else:
                rlist.append(1)
                oxygen_rlist.append(1)
                carbon_rlist.append(1)
                weights.append(weight)
                tot=fraction_mole(value,unit)  
        # make combined lists by concatenating one to the other. 
#        print oxygen_exponent
        Rsum=(sum(carbon_rlist)**carbon_exponent)*(sum(oxygen_rlist)**oxygen_exponent)
        scale_factor=tot/Rsum
        values=np.array(weights)*np.array(rlist)*scale_factor

        ini_con.loc[selected,('Fractions')]=values
        
#        f=open('kpp.txt','w')
#        for spec,value in zip(ini_con['Species'],ini_con['Fractions']):
#            f.write('\t{0}\t=\t {1};\n'.format(spec,value))
#        f.close()
    return ini_con    

def delta_to_ratio(delta,standard):
    r=Isotope_Standards_ratios[standard]
    ratio=((delta/1000.)+1)*r            
    return ratio

def ratio_to_delta(ratio,standard):
    r=Isotope_Standards_ratios[standard]
    delta=(ratio/r-1)*1000           
    return delta

#
# Isotope ratio as from Coplen     
#
Isotope_Standards_ratios={
        'VPDB13':0.011179601,
        'VSMOW18':0.002005171104125155,
        'VSMOW17':0.00037990394344302836
        }
units={
    'pct':1E-2,
    'ppm':1E-6,
    'ppb':1E-9,
    'ppt':1E-12,
    'ppq':1E-15,
    'frac':1.0
       }

def fraction_mole(mole_fraction,unit):  
    return mole_fraction*units[unit]

def mole_fraction(mole_fraction,unit):  
    return mole_fraction/units[unit] 

# =============================================================================
# load and combine kpp output data
# =============================================================================
def get_columns(filename):
    columns=['Time']
    species=get_species(filename)
    columns.extend(species)
    return columns

def clean_data(key,data):
    d=data[key]
    newd=[]
    for item in d:
        try:
            item=float(item)
        except ValueError:
                
            item=0.0
            
        newd.append(item)
    
    return newd      




def kpp_load_data(mapfile,datfile):     
    mapfile=mapfile
    data=pd.read_csv(datfile,sep='\s+',header=None,names=get_columns(mapfile),dtype=None)   
    
    for key in data.columns.values:
        data[key]=clean_data(key,data)
    return data

def orderspecies(species):
    number=[]
    species_ordered=[]
    for i in species:
        i=i.replace('\n','').replace('(r)','').replace('(n)','').split()
        for j in range(0,int(len(i)/3)):
            number.append(int(i[j*3]))
            species_ordered.append(i[j*3+2])        
    number,species_ordered=zip(*sorted(zip(number,species_ordered)))   
    return list(species_ordered)   
   
def get_species(filename):
    f=open(filename,'r')
    counter=0
    varspecies=[]
    fixspecies=[]
    for line in f:
        if line.startswith('###') or line.startswith('Variable species') or line.startswith('Fixed species'):
            counter=0
        if counter==1:
            varspecies.append( line)
        if counter==2:
            fixspecies.append( line)
        if line.startswith('Variable species'):
            counter=1
        if line.startswith('Fixed species'):
            counter=2

    species=orderspecies(varspecies)
    species.extend(orderspecies(fixspecies))
    return species


def post_process(ini_con,data):
    for fam in np.unique(ini_con['Family']):
        selected=ini_con['Family']==fam #family set of isotopologues to be calculated
        fam_set=ini_con[selected]
        tot=sum([data[spec] for spec in fam_set['Species']])
        
        carbon_rlist=[]     #Required for RSUM
        oxygen_rlist=[]     #
        carbon_rlist.append(1)    #Required for RSUM
        oxygen_rlist.append(1)   #

        oxygen_exponent=0
        carbon_exponent=0
        
        for spec,unit,weight in zip(fam_set['Species'],fam_set['Unit'],fam_set['Weight']):
            if spec!=fam:
                ratio=(1./weight)*data[spec]/data[fam]
#                print data[fam]
                data.loc[:,(spec)]=ratio_to_delta(ratio,unit)
                if unit=='VPDB13':
                    carbon_rlist.append(ratio)
                    carbon_exponent=weight
                elif unit=='VSMOW17' or unit=='VSMOW18':
                    oxygen_rlist.append(ratio)
                    oxygen_exponent=weight
            else:
                tot=data[spec][:] 
                u=unit    
#        print carbon_rlist
        Rsum=(sum(carbon_rlist)**carbon_exponent)*(sum(oxygen_rlist)**oxygen_exponent)
        
        tot=mole_fraction(tot*Rsum,u)
        data.loc[:,(fam)]=tot
    return data
 #%%
import matplotlib as mpl
import matplotlib.pyplot as plt
#plt.ioff()
def make_kpp_figures(data):
    for key in data.keys():
        if key!='Time':
            fig,ax=plt.subplots()
            ax.plot(data['Time'],data[key],'-')
            ax.set_xlabel('Time')
            ax.set_ylabel(key)
            fig.savefig(key+'.pdf',bbox_inches='tight')
            plt.close() 
    return

def check_kpp_balance(data,species):
    checker=[0.0000]*len(data)

    for key in data.keys():
        if species in key and key!='N2':
            if species+'2' in key:
                checker+=2*data[key]
            else:
                checker+=data[key]
            plt.plot(data['Time'],data[key],label=key)   
    plt.plot(data['Time'],checker,label='Total '+species)   
    if species=='N':
        ylab=r'NO$_y$'
        plt.ylabel(ylab)
    else:
        plt.ylabel(species+'$_y$')
    plt.xlabel('Time')
    plt.legend()
    #plt.off()
    plt.savefig('Balance_'+species+'.pdf')
    plt.close()
    return
        

