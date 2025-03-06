import cdsapi

c = cdsapi.Client()

c.retrieve(
    'cams-global-greenhouse-gas-inversion',
    {
        'version': 'latest',
        'format': 'tgz',
        'variable': 'methane',
        'quantity': 'concentration',
        'input_observations': 'surface_satellite',
        'time_aggregation': 'instantaneous',
        'year': '2018',
        'month': '10',
    },
    'download.tar.gz')
