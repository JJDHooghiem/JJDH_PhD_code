# /usr/bin/env python
'''
info on what this is:
https://apmonitor.com/che263/index.php/Main/PythonRegressionStatistics
cleaner code obtained from 
https://stackoverflow.com/questions/27116479/calculate-confidence-band-of-least-square-fit
All 
Adopted by Joram

'''

import numpy as np
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import summary_table

def weight_stats(values, weights):
    """
    Return the weighted average and standard deviation.

    values, weights -- Numpy ndarrays with the same shape.
    https://stackoverflow.com/questions/2413522/weighted-standard-deviation-in-numpy
    """
    average = numpy.average(values, weights=weights)
    # Fast and numerically precise:
    variance = numpy.average((values-average)**2, weights=weights)
    return (average, math.sqrt(variance))


def mad(arr):
    """mad
    Median Absolute Deviation: a "Robust" version of standard deviation.
    Indices variabililty of the sample.
    https://en.wikipedia.org/wiki/Median_absolute_deviation 

    Parameters
    ----------
    arr : 
        Array containing the data 


    Returns
    -------
    mad : float
        Median Absolute deviation.
    """

    med = np.median(arr)
    mad = np.median(np.abs(arr - med))
    return mad


def regression(x, y, conf=.95, intercept=True):
    """regression.
    Performs a linear regression using statsmodels.OLS

    Parameters
    ----------
    x :
        x
    y :
        y
    conf :
        confidence level 

    fitparams,r2,fittedvalues,cb_low,cb_upp,pb_low,pb_upp,ci
    """
    X = x
    if intercept == True:
        X = sm.add_constant(X)
    re = sm.OLS(y, X).fit()
    alpha = 1-conf
    ci = re.conf_int(alpha=alpha)
    st, data, ss2 = summary_table(re, alpha=alpha)
    fittedvalues = data[:, 2]
    fitparams = re.params
    r2 = re.rsquared
    p=re.f_pvalue
    predict_mean_se = data[:, 3]
    cb_low, cb_upp = data[:, 4:6].T
    pb_low, pb_upp = data[:, 6:8].T
    return fitparams, r2, fittedvalues, cb_low, cb_upp, pb_low, pb_upp, ci, p
