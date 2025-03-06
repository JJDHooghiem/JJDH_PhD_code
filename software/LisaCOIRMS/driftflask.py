import pandas as pd
import lodautil.lisa as lisa
from datetime import datetime
import numpy as np
lisa=lisa.LISA_load()
# (order in samples altitude is 170,120,120,170)
samples2020=pd.read_csv('/home/joram/research/data/SampleDrift/samples.csv',sep=',')
dates=['20180629','20180629']

data29=lisa['20180629'][:2]
re29=samples2020[:2]
print(data29.keys())
data19=lisa['20180619'][:2]
re19=samples2020[2:][::-1]

print(re19.keys())
dt29=(datetime(2020,7,24)-datetime(2018,6,29)).total_seconds()/(3600*24)
dt19=(datetime(2020,7,24)-datetime(2018,6,19)).total_seconds()/(3600*24)

key='CO'

driftco29=(np.array(re29[key])-np.array(data29[key]))/dt29
driftco19=(np.array(re19[key])-np.array(data19[key]))/dt19
## checking data visually: 
for d,p,dd,pp in zip(data29['CH4'],data29['p'],re29['CH4'],re29['preslev']):
    print(d,p,dd,pp)

print('drift rate %s %.4f +/- %.4f (ppb per day)'  % (key,np.mean(np.concatenate((driftco29,driftco19))),np.std(np.concatenate((driftco29,driftco19)))))
# print(np.mean(np.concatenate((driftco29,driftco19)))*100)
#
key='CO2'

driftco29=(np.array(re29[key])-np.array(data29[key]))/dt29
driftco19=(np.array(re19[key])-np.array(data19[key]))/dt19

print('drift rate %s %.4f +/- %.4f (ppm per day)'  % (key,np.mean(np.concatenate((driftco29,driftco19))),np.std(np.concatenate((driftco29,driftco19)))))

key='CH4'

driftco29=(np.array(re29[key])-np.array(data29[key]))/dt29
driftco19=(np.array(re19[key])-np.array(data19[key]))/dt19

print('drift rate %s %.4f +/- %.4f (ppb per day)'  % (key,np.mean(np.concatenate((driftco29,driftco19))),np.std(np.concatenate((driftco29,driftco19)))))

key='H2O'

driftco29=(np.array(re29[key])-np.array(data29[key]))/dt29
driftco19=(np.array(re19[key])-np.array(data19[key]))/dt19

print('drift rate %s %.4f +/- %.4f (%% per day)'  % (key,np.mean(np.concatenate((driftco29,driftco19))),np.std(np.concatenate((driftco29,driftco19)))))
key='CO'

driftco29=np.array(re29[key])-np.array(data29[key])
driftco19=np.array(re19[key])-np.array(data19[key])

print('difference\t%s\t%.4f +/- %.4f (ppb)'  % (key,np.mean(np.concatenate((driftco29,driftco19))),np.std(np.concatenate((driftco29,driftco19)))))
# print(np.mean(np.concatenate((driftco29,driftco19)))*100)
#
key='CO2'

driftco29=np.array(re29[key])-np.array(data29[key])
driftco19=np.array(re19[key])-np.array(data19[key])

print('difference\t%s\t%.4f +/- %.4f (ppm)'  % (key,np.mean(np.concatenate((driftco29,driftco19))),np.std(np.concatenate((driftco29,driftco19)))))

key='CH4'

driftco29=np.array(re29[key])-np.array(data29[key])
driftco19=np.array(re19[key])-np.array(data19[key])

print('difference\t%s\t%.4f +/- %.4f (ppb)'  % (key,np.mean(np.concatenate((driftco29,driftco19))),np.std(np.concatenate((driftco29,driftco19)))))

key='H2O'

driftco29=np.array(re29[key])-np.array(data29[key])
driftco19=np.array(re19[key])-np.array(data19[key])

print('difference\t%s\t%.4f +/- %.4f (%%)'  % (key,np.mean(np.concatenate((driftco29,driftco19))),np.std(np.concatenate((driftco29,driftco19)))))

