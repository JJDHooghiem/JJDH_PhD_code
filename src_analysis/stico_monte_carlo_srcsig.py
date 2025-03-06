#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Don't remove the line below, it is checked by "one to run them all"
# --otrta-s--
# extension p means parallel, s is for single
import scantools
import config
import scan.stico as stico
import numpy as np
from scipy import stats
import multiprocessing
from scipy.optimize import lsq_linear
import time

# mode='seasonpipe'
# ['13C','18O']
# 1 3 41 for simple 
# 1 2 33 pipe and season (larger uncertainy on te residual terms 
mode='simple'

fractionation=1
offset=True
echam_enrich=True
number=1000000


global results
global lisa
global A
global isotope
global bl
global bh
isotope='18O'
bounds='res'
# isotope='13C'
xbase,res,residual,lisa,A,b=stico.run_inversion(isotope,mode=mode,sens_obs=False,offset=offset,fractionation=fractionation,echam_enrich=echam_enrich,bounds=bounds)

bh,bl=stico.get_bounds(isotope,len(A[0]),bounds)
# results=np.empty((number,3))
manager =multiprocessing.Manager()
results=manager.list([None]*number)
# for i in range(0,number):
def random_frac(f):
    frac=np.random.normal(f,f*0.1)
    return frac
def kick_matrix(A):
    N,M=np.shape(A)
    A_prime=np.empty((N,M))
    for i in range(0,N):
        res_n=-1
        fco2,fch4,fo1d,res=tuple(A[i])
        while res_n<0:
            fco2_n=0
            fo1d_n=0
            fch4_n=0
            while (fco2_n<=0)|(fco2_n>=1):

                fco2_n=random_frac(fco2)
            while (fo1d_n<=0)|(fo1d_n>=1):
                fo1d_n=random_frac(fo1d)
            while (fch4_n<=0)|(fch4_n>=1):
                fch4_n=random_frac(fch4)
            res_n=1-fco2_n-fo1d_n-fch4_n
            
        A_prime[i]= np.array([fco2_n,fch4_n,fo1d_n,res_n])
        # print(np.sum(A_prime[i]))
    # print(A[0])
    return A_prime
def worker(i):    
    b_prime = stico.get_obs(lisa, isotope=isotope, fractionation=fractionation,offset=offset,echam_enrich=echam_enrich)
    # b_prime = stico.get_obs(lisa, isotope=isotope, fractionation='3st',offset=True)
    A_prime = kick_matrix(A)

    res_prime = lsq_linear(A_prime, b_prime, bounds=(bl,bh), method='bvls',tol=1e-40 , max_iter=1000)
# residual = calc_residual(A, res['x'], lisa_prime, isotope, fractionation)

    opt = stico.result_to_d(res_prime['x'], isotope=isotope)
    results[i]=opt
    return

t = time.time()
pool =multiprocessing.Pool()
pool.map(worker,range(number))
pool.close()
pool.join()
print(time.time()-t)
results=np.array(results).T

co2,ch4,o1d=results[:3]
alpha = 0.01
k2, p = stats.normaltest(co2)
print(p)
if p > alpha:
    print('CO2 is probably normal, at the %.2f confidence level' % (1-alpha))
k2, p = stats.normaltest(ch4)

print(p)
if p > alpha:
    print('CH4 is probably normal, at the %.2f confidence level' % (1-alpha))
k2, p = stats.normaltest(o1d)

print(p)
if p > alpha:
    print('O(1D) is probably normal, at the %.2f confidence level' % (1-alpha))

print(np.mean(results,axis=1))
print(np.std(results,axis=1))
exit()
ylabs=[config.axl['pdensn']]*3
# xlabs=[config.axl['osigco2'],config.axl['osigch4'],config.axl['osigosd']]
xlabs=[config.axl['18oco']]*2#,config.axl['osigch4'],config.axl['osigosd']]
fig,axes=scantools.plot_init(1,2,xlabs=xlabs,ylabs=ylabs)
# axes[0].hist(co2,bins=100,density=True,color=config.GruvBoxColors[0])
# axes[1].hist(ch4,bins=100,density=True,color=config.GruvBoxColors[1])
# axes[2].hist(o1d,bins=100,density=True,color=config.GruvBoxColors[3])
axes[0].hist(co2,bins=51,density=True,color=config.GruvBoxColors[0])
axes[0].hist(ch4,bins=51,density=True,color=config.GruvBoxColors[1])
axes[1].hist(o1d,bins=51,density=True,color=config.GruvBoxColors[3])
fig.tight_layout()
fig.savefig(config.FigDir+'stico_prob_dens_src_sig.pdf')

# import matplotlib.pyplot as plt
# plt.close()
# plt.plot(co2,ch4)
# plt.show()
