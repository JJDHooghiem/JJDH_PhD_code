#!/usr/bin/env python
import cdsapi
import lodautil
import numpy as np

# https://ads.atmosphere.copernicus.eu/cdsapp#!/dataset/cams-global-reanalysis-eac4?tab=form
lisa = lodautil.LISA_load()
dates = list(lisa.keys())


def latlon_cams(lat, lon):
    minlat = 10*np.floor(lat/10)
    maxlat = minlat+10
    minlon = 10*np.floor(lon/10)
    maxlon = minlon+10
    return maxlat, minlat, maxlon, minlon


def ECMWFDateFormat(date):
    """
    Assumes date in format "yyyymmdd"
    and retuerns the string
    "yyyy-mm-dd/to/yyyy-mm-{dd+1}"
    """
    year = date[:4]
    month = date[4:6]
    day = date[6:]
    endday = str(int(day)+1)
    if len(endday) != 2:
        endday = '0'+endday
    c = '-'
    date_ecmwf = year+c+month+c+day+'/'+year+c+month+c+endday
    return date_ecmwf


for d in dates:
    date_ecmwf = ECMWFDateFormat(d)

    maxlat, minlat, maxlon, minlon = latlon_cams(
        lisa[d]['Lat'][0], lisa[d]['Lon'][0])

    c = cdsapi.Client()

    c.retrieve(
        'cams-global-reanalysis-eac4',
        {
            'format': 'grib',
            'variable': [
                'methane_chemistry',
                # 'carbon_monoxide', 'hydroxyl_radical', 'ozone',
                # 'temperature', 'surface_pressure',
            ],
            'model_level': [
                '1', '2', '3',
                '4', '5', '6',
                '7', '8', '9',
                '10', '11', '12',
                '13', '14', '15',
                '16', '17', '18',
                '19', '20', '21',
                '22', '23', '24',
                '25', '26', '27',
                '28', '29', '30',
                '31', '32', '33',
                '34', '35', '36',
                '37', '38', '39',
                '40', '41', '42',
                '43', '44', '45',
                '46', '47', '48',
                '49', '50', '51',
                '52', '53', '54',
                '55', '56', '57',
                '58', '59', '60',
            ],
            'date': '%s' % d,
            'time': [
                '00:00', '03:00', '06:00',
                '09:00', '12:00', '15:00',
                '18:00', '21:00',
            ],
            'area': [
                int(maxlat), int(minlon), int(minlat),
                int(maxlon),
            ],
        },
        '%s_cams_eac4.grib' % d)
