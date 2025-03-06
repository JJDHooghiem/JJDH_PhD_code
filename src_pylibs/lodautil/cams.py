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
import lodautil.lisa as ls
from scipy.interpolate import interp1d, interpn
import config

def date_to_hour(year, month, day, hour=0, minutes=0, seconds=0):
    """TODO: Docstring for get_CAMS_profile.
    :returns: TODO
    computes the amount of hours since 1900-01-01 
    according to the gregorian calendar 
    """

    hours_since = (datetime(year, month, day, hour, minutes, seconds) -
                   datetime(1900, 1, 1, 0, 0, 0)).total_seconds()/3600
    return hours_since


def get_cams_profile(var, hours, lat, lon, dataset):
    """TODO: Docstring for get_CAMS_profile.
    :returns: TODO
    hours is the amount of hours elapsed since 1900-01-01
    as specified by the netcdf cams datasets

    """

    lev = dataset['level'][:]

    mesh_interest = np.array(np.meshgrid(hours, lev, lat, lon))
    point_of_interest = np.rollaxis(mesh_interest, 0, 5).reshape(len(lev), 4)
    # for some reason interpn is complaining about the descending order of the latitude ence ::-1
    profile = np.array(interpn((dataset['time'][:], dataset['level'][:], dataset['latitude']
                                [::-1], dataset['longitude'][:]), dataset[var][:, :, ::-1, :], point_of_interest))

    return profile


def get_cams_pressure(date, lat, lon, cams_hours, daymean=False):
    # daymean shouldn't be used until the proper time is added"
    var = 'sp'
    if daymean == True:
        ncfid = config.DataDir+'/ECMWF_CAMS/'+date+'_cams_eac4_surf-dm.nc'
        dataset = Dataset(ncfid)
        mesh_interest = np.array(np.meshgrid(lat, lon))
        point_of_interest = np.rollaxis(mesh_interest, 0, 3).reshape(1, 2)
        # for some reason interpn is complaining about the descending order of the latitude ence ::-1
        press = np.array(interpn((dataset['latitude']
                                  [::-1], dataset['longitude'][:]), dataset[var][::-1, :][0], point_of_interest))
    else:
        ncfid = config.DataDir+'/ECMWF_CAMS/'+date+'_cams_eac4_surf.nc'
        dataset = Dataset(ncfid)

        mesh_interest = np.array(np.meshgrid(cams_hours,  lat, lon))
        point_of_interest = np.rollaxis(mesh_interest, 0, 4).reshape(1, 3)
        # for some reason interpn is complaining about the descending order of the latitude ence ::-1
        press = np.array(interpn((dataset['time'][:], dataset['latitude']
                                  [::-1], dataset['longitude'][:]), dataset[var][:, ::-1, :], point_of_interest))
        press = cams_pres(press)
    return press

def get_cams_nc_fid(date, daymean=False):
    if daymean == True:
        ncfid = config.DataDir+'/ECMWF_CAMS/'+date+'_cams_eac4_hyb-dm.nc'
    else:
        ncfid = config.DataDir+'/ECMWF_CAMS/'+date+'_cams_eac4_hyb.nc'
    return Dataset(ncfid)

cams_unit = {"CO": (28.970/28.010)*1E9, "T": 1,"CH4": (28.970/16.04)*1E9}
cams_key = {"CO": "co", "T": "t","CH4":'ch4_c'}


def collect_lisa_cams(lisakey):
    '''
    Function that returns al LISA data and echam at the lisa data for a given altitude match
    '''
    LISA =ls.LISA_load()
    ls.wildfire_mask(LISA)
    lisa = np.array([])
    cams = np.array([])
    for dat in LISA.keys():
        data = LISA[dat]
        times,_ = ls.get_sample_dt(data, model="CAMS")
        hours = times[0]
        # press = nc_fid['level'][:]*100
        lat = [np.mean(data['Lat'])]
        lon = [np.mean(data['Lon'])]
        press = get_cams_pressure(dat, lat, lon, hours)
        dataset = get_cams_nc_fid(dat)
        var = get_cams_profile(
            cams_key[lisakey], hours, lat, lon,  dataset)*cams_unit[lisakey]
        data['p']*100
        cams = np.append(cams, interp1d(press, var)(data['p']*100))
        lisa = np.append(lisa, data[lisakey])
    lisa = lisa[np.isfinite(cams)]
    cams = cams[np.isfinite(cams)]
    return lisa, cams


def cams_pres(psurf):
    press = psurf*b+a
    return press


a = np.array([20.000000	,
              38.425343	,
              63.647804	,
              95.636963	,
              134.483307	,
              180.584351	,
              234.779053	,
              298.495789	,
              373.971924	,
              464.618134	,
              575.651001	,
              713.218079	,
              883.660522	,
              1094.834717	,
              1356.474609	,
              1680.640259	,
              2082.273926	,
              2579.888672	,
              3196.421631	,
              3960.291504	,
              4906.708496	,
              6018.019531	,
              7306.631348	,
              8765.053711	,
              10376.126953	,
              12077.446289	,
              13775.325195	,
              15379.805664	,
              16819.474609	,
              18045.183594	,
              19027.695313	,
              19755.109375	,
              20222.205078	,
              20429.863281	,
              20384.480469	,
              20097.402344	,
              19584.330078	,
              18864.750000	,
              17961.357422	,
              16899.468750	,
              15706.447266	,
              14411.124023	,
              13043.218750	,
              11632.758789	,
              10209.500977	,
              8802.356445	,
              7438.803223	,
              6144.314941	,
              4941.778320	,
              3850.913330	,
              2887.696533	,
              2063.779785	,
              1385.912598	,
              855.361755	,
              467.333588	,
              210.393890	,
              65.889244	,
              7.367743	,
              0.000000	,
              0.000000	])

b = np.array([0.000000,
              0.000000,
              0.000000,
              0.000000,
              0.000000,
              0.000000,
              0.000000,
              0.000000,
              0.000000,
              0.000000,
              0.000000,
              0.000000,
              0.000000,
              0.000000,
              0.000000,
              0.000000,
              0.000000,
              0.000000,
              0.000000,
              0.000000,
              0.000000,
              0.000000,
              0.000000,
              0.000076,
              0.000461,
              0.001815,
              0.005081,
              0.011143,
              0.020678,
              0.034121,
              0.051690,
              0.073534,
              0.099675,
              0.130023,
              0.164384,
              0.202476,
              0.243933,
              0.288323,
              0.335155,
              0.383892,
              0.433963,
              0.484772,
              0.535710,
              0.586168,
              0.635547,
              0.683269,
              0.728786,
              0.771597,
              0.811253,
              0.847375,
              0.879657,
              0.907884,
              0.931940,
              0.951822,
              0.967645,
              0.979663,
              0.988270,
              0.994019,
              0.997630,
              1.000000])
