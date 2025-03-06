import numpy as np
import scipy.signal as signal
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt


def moving_average_outlier_detection(data,window_size,strict_factor=2):
    finites=np.isfinite(data)
    convoluted_data=np.empty(len(data))
    convoluted_data[:]=np.nan
    convoluted_data[finites]=np.convolve(data[finites], np.ones(window_size)/window_size, mode='same')
    dif=data-convoluted_data
    std=np.nanstd(dif)
    sel=(np.abs(dif)<strict_factor*std)
    return sel 

def asym_convolve(xdata, ydata, std,return_mask=False):
    # stdp = int(np.ceil(std))
    # N = len(x_evenly_spaced)
    # print(N)

    mask = (np.isfinite(xdata))&(np.isfinite(ydata))
    xdata = np.array(xdata[mask])
    ydata = np.array(ydata[mask])

    window = signal.windows.gaussian(10001, 1000)
    x_evenly_spaced = std * np.linspace(-5000, 5000, 10001)/1000
    # plt.plot(x_evenly_spaced, window, 'o')
    # plt.xlim(-std, std)
    # plt.savefig('testlol.pdf')
    # weights_even = window/np.sum(window)  # weights
    ydata_convoluted = np.empty(len(ydata))
    for i in range(0, len(xdata)):
        # center around xdata[i]=0 so that this will interfere with the gaussian maximum
        diff = xdata-xdata[i]
        # print(diff)
        window_uneven = interp1d(
            x_evenly_spaced, window, fill_value=0, bounds_error=False)(diff)
        weights_uneven = window_uneven/np.sum(window_uneven)
    #     print(window_uneven)
        ydata_convoluted[i] = np.sum(weights_uneven*ydata)
    if return_mask == True:
        return mask,ydata_convoluted 
    else:
        return xdata,ydata_convoluted 
