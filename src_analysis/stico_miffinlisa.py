#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Don't remove the line below, it is checked by "one to run them all"
# --otrta-p--
# extension p means parallel, s is for single
"""
This code was written for the analysis presented in the dissertation of Joram Jan Dirk Hooghiem
"""
import numpy as np
import scan.stico as stico
import config
import scantools


fractionation='conv'
xbase,res,residual,lisa,A,b=stico.run_inversion('18O', interpolated=True,method='hyb',daymean=False,mode='simple',fractionation=1,offset=False,sens_obs=False,bounds='res',echam_enrich=True)
alphas = stico.calc_model_alphas(xbase)
# ylabs = [r'$\theta$ (K)']*4
ylabs = [config.axl['ph']]*4
ylims = [(150, 25)]*4
xlims = [(0,15),(-0.5,0)]

xlabs = [ config.axl['D17o'],config.axl['E13c'] ]

mif,error=stico.compute_mif(xbase,A,lisa,miftype='mif',fractionation=1 ,alphas=alphas,echam_enrich=True)
print(mif)
print(error)
fig, axes = scantools.plot_init( 1, 2, xlabs=xlabs, ylabs=ylabs,  ylims=ylims,xlims=xlims)
# for l,miftype in zip(config.Linestyles,['mdf','mif','mdfalpha','mifalpha']):
for l,miftype in zip(config.Linestyles,['mdfalpha']):
# for l,miftype in zip(config.Linestyles,['mdf']):

    # mif,error=stico.compute_mif(xbase,A,lisa,miftype=miftype ,res=res,fractionation=fractionation)
    mif,error=stico.compute_mif(xbase,A,lisa,miftype=miftype ,fractionation=1 ,alphas=alphas,echam_enrich=True)
    stico.plot_dat_lisa(axes[0], mif , lisa ,  linestyle=l)
    stico.plot_dat_lisa(axes[1], error , lisa , linestyle=l)

# stico.add_lisa(axes[1], lisa,'d13C(CO)')
for ax in axes:
    handles,labels=scantools.getUniqueLegend(ax)
    ax.legend(handles=handles,labels=labels)

fig.tight_layout()
fig.savefig(config.FigDir+'stico_mif_cor.pdf')

exit()
# lisa['ECHAM_time'], _ = lodautil.get_sample_dt(lisa)
# p = np.array(lisa['p']*100)
# lisa_d18 = np.array(lisa['d18O(CO)'])
# lisa_c13 = np.array(lisa['d13C(CO)'])

A = stico.get_matrix(lisa, ncfid, method='hyb',mode='season')

res = lsq_linear(A, b,  tol=1e-40,max_iter=1000)
x18 = res['x']
d18_obs_mod = stico.calc_residual(A, x18, lisa,fractionation='conv')+lisa_d18
d18o_src_sig = stico.result_to_d(x18,'18O')
# A x = b
# list of source signatures CO2, CH4, O1D  , delta values in per mill

# Eventually we should get alpha from d18O results and retrieve mass dependent results for x


# mdf case
print(compute_mif(xbase,A,p,miftype='mdf',alphas=None))
print(compute_mif(xbase,A,p,miftype='mif',alphas=None))
print(compute_mif(xbase,A,p,miftype='mdfalpha',alphas=alphas))
print()
exit()
#
# all mif case
#
x_mod = stico.calc_r_term(x17, standard='VSMOW17')
r_term = A.dot(x_mod)
N = len(r_term)
result = np.empty(N)
for i in range(0, N):

    result[i] = stico.calc_d_r_term(
        r_term[i], stisolib.alpha_oh_o17(p[i]), standard='VSMOW17')
# compute capital del 17
mif = stisolib.calc_mif(result, lisa_d18)
error = stisolib.calc_mif_cor(lisa_c13, lisa_d18, result)-lisa_c13

r_term = A.dot(x_mod)
N = len(r_term)
result = np.empty(N)
for i in range(0, N):
    result[i] = stico.calc_d_r_term(
        r_term[i], stisolib.alpha_oh_o17(p[i]), standard='VSMOW17')
# compute capital del 17
mif = stisolib.calc_mif(result, lisa_d18)
error = stisolib.calc_mif_cor(lisa_c13, lisa_d18, result)-lisa_c13
print(mif)
print(error)
# Likely case, get fractionation factors by using the known d18O process
# then get assume know mdf in process, and inherit miff from mif in sources

#
#















