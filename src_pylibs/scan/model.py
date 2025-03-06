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
import numpy as np
import numpy.linalg as la
import stisolib
import lodautil
import scan.stico as stico
bO2    = 0.497   # preference for O16 0.5 means no preference, 0.4 means 40 percent of O16O18 binds the O16 To C and ends up in CO. 

def fwm_isotope(pres,temp,CH4,Cl,OH,O1D,O1Dd17=atmos.O1Dd17,O1Dd18=atmos.O1Dd18,C13H4=-30.0,CO2=0,J_CO2=0.0):
    """fwm_isotope.

    Parameters
    ----------
    pres :
        pres
    temp :
        temp
    CH4 :
        CH4
    Cl :
        Cl
    OH :
        OH
    O1D :
        O1D
    O1Dd17 :
        O1Dd17
    O1Dd18 :
        O1Dd18
    C13H4 :
        C13H4
    CO2 :
        CO2
    J_CO2 :
        J_CO2
    """
    '''
    Calculates, under steady state assumption, C18O. 
    temp: Temperature in Kelvin,
    pres: pressure in Pa,
    CH4,CL,OH,O1D: Mole fractions mol per mol air
    O1Dd18: d18O of O1D. its not measured, but estimated.
    '''
    pres   = pres #pressure
    temp   = temp #temperature
    nden   = atmos.ndens(temp,pres)
    
    C13H4  = C13H4
    CH4    = CH4
    Cl     = Cl
    OH     = OH
    O1D    = O1D
    # from mole fraction to number denisties in per cm3 
    Cl     = Cl    *nden
    OH     = OH    *nden
    O1D    = O1D   *nden
    O2     = atmos.xO2  *nden
        # Get CO2 isotopic composition from relationts
    if len(CO2)>1: 
        d13C,d17O,d18O=atmos.CO2iso(CO2,CH4)
        x626,x636,x628,x627,x637,x638,x728,x738,x727,x828,x737,x838=stisolib.stat_distr_full_CO2(d13C,d17O,d18O)
        CO2 = CO2 * nden
        N26 =(0.5*(x627 + x628) + x626) * CO2 * J_CO2
        N36 =(x636 + 0.5*(x637+x638)) * CO2 * J_CO2
        N28 = stico.alpha_co2*(0.5*x628 + x828) * CO2 * J_CO2
        N27 =(0.5*x627 + x727) * CO2 * J_CO2
    elif CO2!=0:
        d13C,d17O,d18O=atmos.CO2iso(CO2,CH4)
        x626,x636,x628,x627,x637,x638,x728,x738,x727,x828,x737,x838=stisolib.stat_distr_full_CO2(d13C,d17O,d18O)
        CO2 = CO2 * nden
        N26=(0.5*(x627 + x628) + x626) * CO2 * J_CO2
        N36=(x636 + 0.5*(x637+x638)) * CO2 * J_CO2
        N28=(0.5*x628 + x828) * CO2 * J_CO2
        N27=(0.5*x627 + x727) * CO2 * J_CO2
    else:
        N26=0     
        N36=0 
        N28=0
        N27=0
    CH4 = CH4 * nden
    # print(1/(J_CO2*3600*24*365))
    # print(stisolib.ratio_to_delta(N28/N26,"VSMOW18"),stisolib.ratio_to_delta(N27/N26,"VSMOW17"))
    # print(N28/N26,N27/N26)
    # statistically distribute the oxygen molecules (reassingin above defs)
    # we only use the terminal oxygen atom in ozone, QOO or OOQ NOT: OQO

    x16,x17,x18=stisolib.stat_distr_full_O(O1Dd17,O1Dd18,1) 
    n_O1D= O1D * x16
    n_O1Dd17= O1D * x17 
    n_O1Dd18= O1D * x18 

    x16,x17,x18=stisolib.stat_distr_full_O(atmos.O2d17,atmos.O2d18,2)
    n_O2= O2 * x16
    n_O2d17= O2 * x17 
    n_O2d18= O2 * x18 

    x12,x13=stisolib.stat_distr_full_C(C13H4,1)
    n_CH4 = CH4 *x12
    n_CH4d13= CH4 * x13

    # CH4 sink reactions:
    k_O1D = atmos.rate_arr(1.75E-10,0.0,temp) # --reac--
    # k_O1D = atmos.rate_arr(1.91E-10,0.0,temp)
    k_Cl  = atmos.rate_arr(7.1E-12,1270.0,temp) # --reac--
    k_OH  = atmos.rate_arr(2.45E-12,1775.0,temp) #  

    # k_O1D = 1.75E-10*np.exp(temp*0)
    # k_Cl  = 6.6E-12*np.exp(-1240./temp) #Atkinson 2006
    # k_OH  = 1.85E-20*np.exp(2.82*np.log(temp)-987./temp) #1627
     
    # CO + OH
    k_CO=(1.57E-13+(3.54E-33)*nden)
    
    # CH3 + O2:
    k_O2= atmos.rate_3rd(temp,nden,4.0E-31,3.6,1.20E-12,-1.1)
    
    #Doubled reactions: 
    k_O2d17=k_O2*stisolib.alpha_mu(15.0,32.0,33.0)
    k_O2d18=k_O2*stisolib.alpha_mu(15.0,32.0,34.0)

    k_COd17=k_CO*stisolib.alpha_oh_o17(pres)
    k_COd18=k_CO*stisolib.alpha_oh_o18(pres)

    k_O1Dd17 =k_O1D*stisolib.alpha_mu(16.0,16.0,17.0)
    k_O1Dd18 =k_O1D*stisolib.alpha_mu(16.0,16.0,18.0)
    
#    C13Sink reactions
    a_13CH4_OH = 1/1.0039
    a_13CH4_Cl = stisolib.alpha_temp(1/1.043, 6.46,temp)
    a_13CH4_O1D = 1/1.013
    a_13CO_OH=stisolib.alpha_oh_c13(pres)

    C12O_p=(k_O1D * O1D +
            k_Cl * Cl +
            k_OH * OH )*n_CH4 + N26 
    source_fractions=np.array([k_O1D * O1D*n_CH4/C12O_p, k_Cl * Cl*n_CH4/C12O_p,k_OH * OH*n_CH4/C12O_p,N26/C12O_p])
    C12O_s= k_CO *OH

    C12O_stst=C12O_p/C12O_s

    C13O_p=(k_O1D * a_13CH4_O1D * O1D +
            k_Cl * a_13CH4_Cl * Cl +
            k_OH * a_13CH4_OH * OH )*n_CH4d13 + N36

    C13O_s=a_13CO_OH * k_CO * OH

    C13O_stst=C13O_p/C13O_s
    COd13=stisolib.ratio_to_delta(C13O_stst/C12O_stst,"VPDB13")
    # in steady state the production is gona be determined by the production fo CH3. We take overal O2 nden here, not isotope specific
    CH3_stst=((0.75 *k_O1D * O1D + 
                     k_Cl  * Cl  +
                     k_OH  * OH)*CH4)/(k_O2*O2)

    #p for production 
    C16O_p=(k_O2 * CH3_stst * n_O2 +
           (1-bO2) * k_O2d18 * CH3_stst * n_O2d18 +
           (1-bO2) * k_O2d17 * CH3_stst * n_O2d17 +
           0.25* k_O1D   * n_O1D*CH4) + N26


    #s for sink
    C16O_s=k_CO*OH
    C16O_stst=C16O_p/C16O_s
    #p for production
    C18O_p=(bO2 * k_O2d18 * CH3_stst * n_O2d18 +
            0.25* k_O1Dd18* n_O1Dd18*CH4) + N28
    #s for sink
    C18O_s=k_COd18*OH
    C18O_stst=C18O_p/C18O_s
    COd18=stisolib.ratio_to_delta(C18O_stst/C16O_stst,'VSMOW18')
    #
    C17O_p=(bO2 * k_O2d17 * CH3_stst * n_O2d17 +
            0.25* k_O1Dd17* n_O1Dd17*CH4) + N27

    #s for sink
    C17O_s=k_COd17*OH
    C17O_stst=C17O_p/C17O_s
    COd17=stisolib.ratio_to_delta(C17O_stst/C16O_stst,'VSMOW17') 

    CO_mol=1E9*(C17O_stst+C16O_stst+C18O_stst)/nden
    return CO_mol,COd13,COd17,COd18,source_fractions

def inv_C13(temp,pres,CO,d13CO,CH4,d13CH4):
    """
    Calculates the number densities of OH Cl O1D
    temperature in kelvin
    Pressure in pa
    CO mole fraction 
    CH4 mole fraction  
    Isotope composition in per mil
    """
    #print("stisolib.stat_distr_simple does not yet accomodate mif. morever it assumes 17O doesn't exist") 
    pres  = pres  # pressur  e
    temp  = temp  # temperature
    nden = atmos.ndens(temp, pres)

    # Regular species 
    nCO = CO *  nden
    nCH4 = CH4 *  nden

    x12,x13=stisolib.stat_distr_full_C(d13CO,1)
    nCO    = nCO *  x12
    nCOd13 = nCO *  x13

    x12,x13=stisolib.stat_distr_full_C(d13CH4,1)
    nCH4 = nCH4*x12
    nC13H4 = nCH4*x13

    # Statistical distribution of O1D and Oxygen factor 0.5 is there because half of 16O18O leads to C18O 
    k_CH4_OH = atmos.rate_arr(2.45E-12,1775.0,temp)
    k_CH4_Cl = atmos.rate_arr(7.1E-12,1270.0,temp)
    k_CH4_O1D = atmos.rate_arr(1.75E-10,0.0,temp)

    k_CO_OH  = (1.57E-13+(3.54E-33)*nden)
     
    # fractionation factors
    a_13CH4_OH = 1/1.0039
    a_13CH4_Cl = stisolib.alpha_temp(1/1.043, 6.46,temp)
    a_13CH4_O1D = 1/1.013
    a_13CO_OH=stisolib.alpha_oh_c13(pres)
    # setup matrix Ax=b check out the report for its definition 
    # oxygen reactions without fractionation
    x1 = k_CO_OH * nCO/nCH4 - k_CH4_OH
    x2 = a_13CO_OH* k_CO_OH * nCOd13/nC13H4 - a_13CH4_OH * k_CH4_OH
    x=np.array([x1,x2])
    a11 = k_CH4_Cl 
    a12 = k_CH4_O1D 
    a21 = a_13CH4_Cl  * k_CH4_Cl 
    a22 = a_13CH4_O1D * k_CH4_O1D
    A=np.array([[a11,a12],[a21,a22]])

    nCl_OH,nO1D_OH=la.solve(A,x)

    # check succsefull calculation
    return nCl_OH,nO1D_OH

def inv_O18(temp,pres,CO,CH4,d13CO,d18CO,d13CH4,O1Dd18=atmos.O1Dd18,O1Dd17=atmos.O1Dd17):
    """
    Calculates the number densities of OH Cl O1D
    temperature in kelvin
    Pressure in Pa 
    CO mole fraction 
    CH4 mole fraction  
    Isotope composition in per mil
    """
    #print("stisolib.stat_distr_simple does not yet accomodate mif. morever it assumes 17O doesn't exist") 
    pres  = pres  # pressur  e
    temp  = temp  # temperature
    nden = atmos.ndens(temp, pres)

    # Regular species 
    nCO = CO *  nden
    nCH4 = CH4 *  nden
         
#    O18 species
    d17CO = calc_d17o_mdf(d18CO)

    x16,x17,x18=stisolib.stat_distr_full_O(d17CO,d18CO,1)
    x12,x13=stisolib.stat_distr_full_C(d13CO,1)
    n18CO = nCO * x18 * x12
    nCO_all=nCO
    nCO = nCO * x16 * x12
    x12,x13=stisolib.stat_distr_full_C(d13CH4,1)
    nC12H4 = nCH4*x12
    # Statistical distribution of O1D and Oxygen factor 0.5 is there because half of 16O18O leads to C18O 
    # fraction of 18O1D = n_18O1D/n_O1D=x18 * n_O1D/n_O1D = x18 
    x16,x17,x18=stisolib.stat_distr_full_O(O1Dd17,O1Dd18,1) 
    f_O1D= x18 
    # Same for oxygen 
    x16,x17,x18=stisolib.stat_distr_full_O(atmos.O2d17,atmos.O2d18,2) 
    f_O2 = x18 
    # Rate reactions 

    k_CH4_OH = atmos.rate_arr(2.45E-12,1775.0,temp)
    k_CH4_Cl = atmos.rate_arr(7.1E-12,1270.0,temp)
    k_CH4_O1D = atmos.rate_arr(1.75E-10,0.0,temp)

    k_CO_OH  = (1.57E-13+(3.54E-33)*nden)
     
    # fractionation factors
    a_18CO_OH = stisolib.alpha_oh_o18(pres)
    a_CH3_O2  = 1 * stisolib.alpha_mu(15.0,32.0,34.0)
    a_CH4_O1D = 1 *  stisolib.alpha_mu(16.0,16.0,18.0)
    # setup matrix Ax=b check out the report for its definition 
    # oxygen reactions without fractionation
    x1 = k_CO_OH * nCO/nCH4 - k_CH4_OH
    x2 = a_18CO_OH * k_CO_OH * n18CO/nCH4 - bO2 * a_CH3_O2 * f_O2 * k_CH4_OH
    x=np.array([x1,x2])
    a11 = k_CH4_Cl 
    a12 = k_CH4_O1D 
    a21 = a_CH3_O2 * bO2 * f_O2 * k_CH4_Cl 
    a22 = (0.75 * a_CH3_O2 * bO2 * f_O2 * k_CH4_O1D +
           0.25 * a_CH4_O1D * f_O1D * k_CH4_O1D)
    A=np.array([[a11,a12],[a21,a22]])

    nCl_OH,nO1D_OH=la.solve(A,x)

    # check succsefull calculation
    return nCl_OH,nO1D_OH

def echamModelAtLisa(interpolated=False):
    """echamModelAtLisa.

    Parameters
    ----------
    interpolated :
        interpolated
    """
    LISA=lodautil.flattened_LISA()
    LISA=lodautil.var_select(LISA,'d18O(CO)')
    model_results={}
    ncfid=lodautil.get_ncfid(interpolated=False,daymean=True)
    for dat in lodautil.get_dates(LISA):
        data=lodautil.date_select(LISA,dat)
        # CH4=data['CH4']*1E-9
        time=np.floor(lodautil.get_sample_dt(data)[0][-1])+0.5
        # get daily mean variables  

        # This is only CH4 derived CO2? 
        # FCMCO2/CO2 = (JCO2*XFCMCO2)/(JCO2*CO2) = PTLFCMCO2/XPTLCO2
        # XPTLCO2 = CO2/FCMCO2
        CO2  = lodautil.echam.get_ECHAM_tt(time,'tracer_gp_CO2',ncfid)
        FCMCO2  = lodautil.echam.get_ECHAM_tt(time,'tracer_gp_FCMCO2',ncfid)
        JCO2 = (CO2/FCMCO2)*lodautil.echam.get_ECHAM_tt(time,'tracer_gp_XPTLFCMCO2',ncfid)

        O1D  = lodautil.echam.get_ECHAM_tt(time,'tracer_gp_O1D',ncfid)
        OH   = lodautil.echam.get_ECHAM_tt(time,'tracer_gp_OH',ncfid)
        CH4  = lodautil.echam.get_ECHAM_tt(time,'tracer_gp_CH4',ncfid)
        d13CH4=stisolib.ch4_to_c13(CH4*1E9,'wv')
        CO   = lodautil.echam.get_ECHAM_tt(time,'tracer_gp_CO',ncfid)
        Cl   = lodautil.echam.get_ECHAM_tt(time,'tracer_gp_Cl',ncfid)
        CO2  = lodautil.echam.get_ECHAM_tt(time,'tracer_gp_CO2',ncfid)
        press=lodautil.echam.get_ECHAM_pp(time,ncfid)

        temp = lodautil.echam.get_ECHAM_tt(time,'ECHAM5_tm1',ncfid)

        nden= atmos.ndens(temp,press)
        theta=   atmos.theta(temp,press)
        model_results[dat] = (fwm_isotope(press,temp,CH4,Cl,OH,O1D,C13H4=d13CH4,CO2=CO2,J_CO2=JCO2/CO2),theta,CO)
    return model_results

def ModelAtLisa(Cl=0):
    """ModelAtLisa.

    Parameters
    ----------
    Cl :
        Cl
    """
    jvalresults                                           = '/home/joram/research/data/JVALresults/'
    f90                                                   = glob(jvalresults+'*/*.f90')
    nlev=25
    LISA=lodautil.LISA_load()
    LISA=check_COstab(LISA)
    lat=67.368
    lon=26.633
    nc_fid=Dataset('/home/joram/research/data/ECMWF_CAMS/Ozone_CAMS_annual.nc')
    months=[4,8,9]
    model_results={}
    for dat in LISA.keys():
        month=int(dat[4:6])
        data=LISA[dat]

        CO2=data['CO2']*1E-6
        CH4=data['CH4']
        d13CH4=stisolib.ch4_to_c13(CH4,'wv')
        CH4=data['CH4']*1E-9

        for jval in f90:
            monthjval=int(jval.split('run')[0].split('/')[-1])
            if monthjval==month:
                sza=atmos.mean_sza_month(lat,month)
                press, ozone,temp=lodautil.obtain_jval(jval)
                nden = atmos.ndens(temp,press)
                th=atmos.theta(temp,press)
                ncjval=jval.replace('jval.f90','.nc')
                break         

        lev=np.linspace(1,nlev,nlev)
        JCO2=lodautil.get_jvalues(Dataset(ncjval),'J_CO2',sza,lev)
        JO1D=lodautil.get_jvalues(Dataset(ncjval),'J_O1D',sza,lev)

        O1D=nden*ozone*JO1D/(nden*(0.78084*atmos.rate_arr(2.15E-11,-110.0,temp)
                +0.20946*atmos.rate_arr(3.3E-11,-55.0,temp)))

        hours=lodautil.date_to_hours(2017,month,1)

        cams_OH=lodautil.get_CAMS_profile('oh',hours,lat,lon,nc_fid)*(28.970/17.007)
        cams_CH4=lodautil.get_CAMS_profile('ch4_c',hours,lat,lon,nc_fid)*(28.970/16.042)
        cams_CO=lodautil.get_CAMS_profile('co',hours,lat,lon,nc_fid)*(28.970/28.010)
        #get interpolators on isentropic surfaces 
        interpoland=th
    #    interpoland=cams_CH4
        int_ozone=interp1d(interpoland,ozone,fill_value="extrapolate" )
        int_CH4=interp1d(interpoland,cams_CH4,fill_value="extrapolate" )
        int_CO=interp1d(interpoland,cams_CO,fill_value="extrapolate" )
        int_temp=interp1d(interpoland,temp  ,fill_value="extrapolate" )
        int_press=interp1d(interpoland,press,fill_value="extrapolate" )
        int_O1D =interp1d(interpoland,O1D   ,fill_value="extrapolate" )
        int_OH=interp1d(interpoland,cams_OH      ,fill_value="extrapolate" )
        int_JCO2 =interp1d(interpoland,JCO2 ,fill_value="extrapolate" )
        int_th =interp1d(interpoland,th,fill_value="extrapolate" )
        interpoland=data['PT']
    #    interpoland=CH4
        O1D_LISA  =(interpoland)
        OH_LISA   =int_OH(interpoland)
        JCO2_LISA =int_JCO2(interpoland)
        CO_LISA =int_CO(interpoland)
    
        press=data['p']*100
        temp=data['T']
        #press=int_press(interpoland)
        #temp=int_temp(interpoland)
        nden= atmos.ndens(temp,press)

        model_results[dat] = (fwm_isotope(press,temp,CH4,Cl,OH_LISA,O1D_LISA/nden,C13H4=d13CH4,CO2=CO2,J_CO2=JCO2_LISA),CO_LISA)
    return model_results
