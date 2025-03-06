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
from glob import glob
from io import StringIO
import pandas as pd
import numpy as np
import lodautil.cams
import lodautil.echam
import config
# lttex={'Date':r'Date', 'Time of sampling':r't', 'Temperature':r'$T$~(K)', 'Theta (K)':r'$\theta$ (K)', 'Relative Humidtiy':'$\phi$~(\%)', 'Lon':'Lon', 'Lat':'Lat', 'Weighted p(mbar)':'$p', 'p start', 'p stop', 'Altitude', 'Altitude start', 'Altitude stop', 'Samplesize (L)', 'Vertical resolution', 'Sampling time(s)', 'mean speed (m/s)', 'CO2', 'CO2 un', 'CH4', 'CH4 un', 'CO', 'CO un', 'H2O', 'H20 un', 'IRMS date', 'CO IRMS', 'd13C(CO)', 'd13C(CO) un', 'd18O(CO)', 'd18O(CO) un', 'N2O', 'N2O un', 'CO JKADS', 'CO un JKADS']


def LoadLisaWeights(path):
    """
    Retrieves the wieghts of a single LISA fligth
    """
    data = pd.read_csv(path)
    data = data[(data['SampleFlag'] == 1) | (data['SampleFlag'] == 2) | (
        data['SampleFlag'] == 3) | (data['SampleFlag'] == 4)][['PR', 'Weights', 'SampleFlag']]
    return data

def LoadLisa(path):

    with open(path, 'r') as result:
        headerstring = result.read()
        header, data = headerstring.split('End of header information\n')
        data = StringIO(data)
        data = pd.read_csv(data, sep=",")
        unit_str, header = header.split('End of unit declaration\n')
    return unit_str, header, data

def get_headers():
    LISA_dir = config.DataDir+'/LISA_Measurements/'
    files = glob(LISA_dir+'*/Processed/*flight*.csv')

    data = {}
    for f in files:
        date = f.split('/')[-3].split('_S')[0].replace('_', '')
        unit_str, header, df = LoadLisa(f)

        data[date] = unit_str
    return data

def import_LISA(LISA_dir):
    files = glob(LISA_dir+'*/Processed/*flight*.csv')

    data = {}
    for f in files:
        date = f.split('/')[-3].split('_S')[0].replace('_', '')
        unit_str, header, df = LoadLisa(f)

        data[date] = df
    return data

def import_LISA_weights(LISA_dir):
    files = glob(LISA_dir+'*/Processed/*metdata*.csv')

    data = {}
    for f in files:
        date = f.split('/')[-3].split('_S')[0].replace('_', '')
        data[date] = LoadLisaWeights(f)
    return data

def LISA_load_weights():
    """
    Load the LISA data set containing the isotope data
    """

    LISA_dir = config.DataDir+'/LISA_Measurements/'
    LISA = import_LISA_weights(LISA_dir)
    return LISA


def LISA_load():
    """
    Load the LISA data set containing the isotope data
    """

    LISA_dir = config.DataDir+'/LISA_Measurements/'
    LISA = import_LISA(LISA_dir)
    return LISA


def flattened_LISA():
    """TODO: Docstring for flatten_LISA.
    Returns
    -------
    TODO

    """
    LISA_dict = LISA_load()
    LISA = [LISA_dict[dat] for dat in (LISA_dict.keys())]
    LISA = pd.concat(LISA, ignore_index=True)
    return LISA


def wildfire_mask(LISA):
    data_05 = LISA["20170905"]
    LISA["20170905"] = data_05[1:].reset_index()
    return


def time_int(time):
    """TODO: Docstring for LISA_datetime_to_int.
    :returns: TODO

    """
    hh, mm, ss = [int(a) for a in time.split(':')]
    return hh, mm, ss


def date_int(date):
    """TODO: Docstring for LISA_datetime_to_int.
    :returns: TODO

    """
    year, month, day = [int(a) for a in date.split('-')]
    return year, month, day


def var_select(LISA, var):
    """var_select.
    Selects finites in the columng with keyword var,
    returns a dataframe witth sample data for wich var exists
    Parameters
    ----------
    LISA :
        LISA flattened dataframe
    var :
        var
    """
    a = LISA[:][np.isfinite(LISA[var])]
    return a


def date_select(LISA, date):
    """date_select.

    Parameters
    ----------
    LISA :
        LISA flattened dataframe
    date :
        date
    """
    a = LISA[:][(LISA['Date'] == date)]
    return a


def get_dates(LISA):
    """get_dates.
    returns a list with unique flight dates 
    Parameters
    ----------
    LISA :
        LISA flattened dataframe
    """
    dates = np.unique(LISA['Date'])
    return dates


def get_sample_dt(LISA, model='ECHAM5'):
    """get_sample_paramsLtoE.

    Parameters
    ----------
    LISA :
        LISA
    """
    times = []
    dates = []
    for date, time in zip(LISA['Date'], LISA['Time of sampling']):
        y, m, d = date_int(date)
        h, mm, s = time_int(time)
        if model == "CAMS":
            times.append(lodautil.cams.date_to_hour(y, m, d, h, mm, s))
        else:
            times.append(lodautil.echam.date_to_day(y, m, d, h, mm, s))
        dates.append(date)
    return times, dates


def get_unique_dates(LISA=None):
    if not isinstance(LISA, pd.DataFrame):
        LISA = lodautil.flattened_LISA()
    LISA = LISA.iloc[np.unique(LISA['Date'], return_index=True)[1]]
    times, dates = get_sample_dt(LISA)
    dates, times = zip(*sorted(zip(dates, times)))
    return times, dates
