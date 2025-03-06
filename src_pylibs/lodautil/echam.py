"""
Author: Joram Jan Dirk Hooghiem

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
from datetime import datetime
import numpy as np
from netCDF4 import Dataset
from scipy.interpolate import interp1d, interpn
import config

# Used for getting mumol mol-1 and nmol mol.
echam_unit = {'CO': 1E9,
              'CO2': 1E6,
              'CH4': 1E9,
              'Cl': 1E15,
              'O1D': 1E18,
              'OH': 1E15,
              'N2O': 1E9
              }


def date_to_day(year, month, day, hour=0, minutes=0, seconds=0):
    """TODO: Docstring for date_to_day.
    :returns: TODO

    """

    days_since = (datetime(year, month, day, hour, minutes, seconds) -
                  datetime(2000, 1, 1, 0, 0, 0)).total_seconds()/(3600.0*24.0)
    return days_since


def get_ECHAM_tt(time, var, dataset):
    """TODO: Docstring for get_ECHAM_time.
    :returns: TODO

    """
    dataset = dataset
    time = time
    lev = dataset['lev'][:]
    mesh_interest = np.array(np.meshgrid(time, lev))
    point_of_interest = np.rollaxis(mesh_interest, 0, 3).reshape(len(lev), 2)
    # for some reason interpn is complaining about the descending order of the latitude ence ::-1
    profile = np.array(interpn(
        (dataset['time'][:], dataset['lev'][:]), dataset[var][:, :], point_of_interest))
    return profile
def get_ECHAM_time(dataset):
    time=np.array(dataset['time'][:])
    return time
def get_ECHAM_pp(time, dataset, hyam=None, hybm=None):
    """TODO: Docstring for get_ECHAM_time.
    :returns: TODO

    """
    time = np.array(time)
    if not isinstance(hyam, np.ndarray):
        data = Dataset(
            config.DataDir+'/ECHAM/LISA/SICM-z4/SICM-z4________20170426_0010_s4d_LISA.nc')
        hyam = data['hyam'][:]
        hybm = data['hybm'][:]
    dataset['time'][:], dataset['g3b_aps'][:]
    x = dataset['time'][:][(dataset['g3b_aps'][:] != -99999)]
    y = dataset['g3b_aps'][:][(dataset['g3b_aps'][:] != -99999)]
    g3b_aps = interp1d(x, y)(time)
    pressure = g3b_aps * hybm + hyam
    return pressure.compressed()


def get_ncfid(interpolated=False, daymean=False, experiment='z4'):
    """
    z4 
    eq1z 
    """
    if daymean:
        prefix = 'daymean_'
    else:
        prefix = ''
    if interpolated:
        ncfid = Dataset(config.DataDir+'/ECHAM/LISA/SICM-' +
                        experiment+'/'+prefix+'SICM-'+experiment+'_LISA.nc')
    else:
        ncfid = Dataset(config.DataDir+'/ECHAM/LISA/SICM-' +
                        experiment+'/'+prefix+'SICM-'+experiment+'_LISA-ni.nc')
    return ncfid


def get_echam_trtr(var1, var2, time, ncfid, ph=20000, pl=2500):
    """TODO: Docstring for get_ECHAM_trtr.
    :returns:two tracers 

    """
    d_var1 = get_ECHAM_tt(time, var1, ncfid)
    d_var2 = get_ECHAM_tt(time, var2, ncfid)
    pressure = get_ECHAM_pp(time, ncfid)
    d_var1 = d_var1[(pressure >= pl) & (pressure <= ph)]
    d_var2 = d_var2[(pressure >= pl) & (pressure <= ph)]
    return d_var1.compressed(), d_var2.compressed()


def check_echam_ch4(ch4):
    for r in range(1, len(ch4)):
        if ch4[r] <= ch4[r-1]:
            index = r-1
            break
        elif r == len(ch4)-1:
            index = r
            break
    return index


def hybrid_interpolation(time, pres, ch4, key, ncfid):
    """TODO: Docstring for hybrid_interpolation.
    time / pres / ch4 mole fraction at  which to obtain the value of parameter key in dataset ncfid
    Parameters
    ----------
    arg1 : TODO

    Returns
    -------
    TODO

    """
    press = get_ECHAM_pp(time, ncfid)
    pmask = (press > 2500) & (press < 25000)
    press = np.array(press[pmask])
    echam_ch4 = np.array(
        1E9*get_ECHAM_tt(time, 'tracer_gp_CH4', ncfid)[pmask])
    ch4_index = check_echam_ch4(echam_ch4)
    varEcham = []
    echam_at_obs = []
    if key == 'p':
        echam_var = press
    else:
        echam_var = np.array(get_ECHAM_tt(
            time, key, ncfid)[pmask])
    for p, ch4 in zip(pres, ch4):
        if ch4 <= echam_ch4[ch4_index] and p < press[ch4_index]:
            echam_at_obs.append(interp1d(
                echam_ch4[:ch4_index], echam_var[:ch4_index], bounds_error=False, fill_value='extrapolate')(ch4))
        else:
            echam_at_obs.append(
                interp1d(press, echam_var, bounds_error=False, fill_value='extrapolate')(p))
    return echam_at_obs


def verticalparams(method):
    """verticalparams.

    Parameters
    ----------
    vertical :
        vertical
    """
    if method == "p":
        v_unit = 100      # Vertical unit conversion for LISA
        echamx = 'press'
        lisaxkey = "p"
    elif method == "pot":
        v_unit = 1      # Vertical unit conversion for LISA
        echamx = "pot"
        lisaxkey = "PT"
    elif method == "CH4":
        v_unit = 1      # Vertical unit conversion for LISA
        echamx = "CH4"
        lisaxkey = "CH4"
    elif method == "hyb":
        v_unit = 100      # Vertical unit conversion for LISA
        echamx = "hyb"
        lisaxkey = "p"
    return v_unit, echamx, lisaxkey


def get_echam_at_LISA(time, pres, key, ncfid, method='press', ch4=None):
    '''
    if interpolation method is via hybrid lisa_p should be given in Pa 
    '''
    echam_pres = get_ECHAM_pp(time, ncfid)
    if key == 'p':
        varEcham = echam_pres
    else:
        varEcham = get_ECHAM_tt(time, key, ncfid)
    if method == 'press':
        xvar = echam_pres
    elif method == 'CH4':
        xvar = 1E9 * \
            get_ECHAM_tt(time, 'tracer_gp_CH4', ncfid)

    elif method == 'pot':
        xvar = get_ECHAM_tt(time, 'ECHAM5_tpot', ncfid)

    mask = (echam_pres >= 2500) & (echam_pres <= 25000)

    if method == 'hyb':
        echam_at_obs = hybrid_interpolation(
            time, pres, ch4, key, ncfid)
    else:
        x, y = xvar[mask], varEcham[mask]
        echam_at_obs = interp1d(x, y, bounds_error=False,
                                fill_value='extrapolate')(pres)
    if not isinstance(echam_at_obs, np.ndarray):
        echam_at_obs = np.array(echam_at_obs)

    return echam_at_obs

#
# gets both datasets for lisa and echam


def collect_lisa_echam(lisakey, echamy, ncfid, method="p"):
    '''
    Function that returns al LISA data and echam at the lisa data for a given altitude match
    '''
    from lodautil.lisa import LISA_load, wildfire_mask, get_sample_dt
    LISA = LISA_load()
    wildfire_mask(LISA)
    lisa = []
    echam = []
    v_unit, echamx, lisaxkey = verticalparams(method)
    for dat in LISA.keys():
        data = LISA[dat]
        try:
            lisa.extend(data[lisakey])
        # first sample that was taken:
            lisa_time = get_sample_dt(data)[0][-1]
            lisax = data[lisaxkey]*v_unit
            if method != 'hyb':
                echam.extend(get_echam_at_LISA(
                    lisa_time, lisax, echamy, ncfid, echamx))
            else:
                lisa_ch4 = data['CH4']
                echam.extend(get_echam_at_LISA(lisa_time, lisax,
                                               echamy, ncfid, echamx, ch4=lisa_ch4))
        except KeyError:
            pass
    lisa = np.array(lisa)
    echam = np.array(echam)
    if lisakey in echam_unit.keys():
        echam = echam*echam_unit[lisakey]
    if lisakey == "p":
        lisa = lisa*100
    # make sure that they are not nan
    lisa = lisa[np.isfinite(echam)]
    echam = echam[np.isfinite(echam)]
    return lisa, echam


def get_echam_tracers_gp(time, press, tracers, ncfid, **kwargs):
    """echamFractions.

    Parameters
    ----------
    time :
        time
    ncfid :
        ncfid
    see also get_echam_at_LISA
    """
    # Tracers
    echam_results = {}
    for echamy in tracers:
        echam_results[echamy] = get_echam_at_LISA(time, press, 'tracer_gp_'+echamy, ncfid, **kwargs)
    return echam_results
