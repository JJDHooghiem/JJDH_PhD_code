import scan.stico as stico

import pandas as pd
import lodautil.lisa as lisa
from datetime import datetime
import numpy as np
LISA=lisa.flattened_LISA()
LISA=lisa.var_select(LISA,'d18O(CO)').reset_index()
def calcfc(x_s,x_c,drift):
    '''
    x_s is sample mole fraction
    x_c is mole fraction of the contamintation source
    drift is the change in mole fraction with respect to contamination
    '''
    fc=drift/(x_c-x_s)
    return fc

import matplotlib.pyplot as plt
## value for the contamination
## molefraction in ppb 
## delta values of the conatmination c 
## From Mak2003 northern hemisphere estimates Figure 2
## looked at october values 
x_c = 150
d_c_c = -29
d_c_o =  0
# contaminated, e.g. more summer like variables 
# x_c   = 50
# d_c_c = -26
# d_c_o = 4
# drift rate in ppb per day
dr = 0.05
print("date\t\tco\tdt\tdrift\tDd13c\tDd18o")
print("yyyy-mm-dd\tppb\tdays\tppb\tpm\tpm")
for i in range(0,len(LISA)):
    dt=(pd.to_datetime(LISA['IRMS date'][i])-pd.to_datetime(LISA['Date'][i])).total_seconds()/(3600*24)
    drift=dr*dt
    co=LISA['CO'][i]
    c13=LISA['d13C(CO)'][i]
    o18=LISA['d18O(CO)'][i]
    fc=calcfc(co,x_c,drift)
    # Dc13=(d_c_c-c13)*fc
    # Do18=(d_c_o-o18)*fc
    Dc13=c13-((co+drift)*c13-x_c*d_c_c*fc)/((1-fc)*co)
    Do18=o18-((co+drift)*o18-x_c*d_c_o*fc)/((1-fc)*co)
    date=LISA['Date'][i]
    # print("%s\t%.0f\t%.0f\t%.0f\t%.1f\t%.1f" % (date,co,dt,drift,Dc13,Do18))
    plt.plot(c13-Dc13,o18-Do18,marker='d',color='k')
    plt.plot(c13,o18,marker='o',color='b')
    print("%s\t%.0f\t%.0f\t%.0f\t%.1f\t%.1f" % (date,co,dt,drift,c13-Dc13,o18-Do18))

plt.show()
