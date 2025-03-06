#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Don't remove the line below, it is checked by "one to run them all"
# --otrta-p--
# extension p means parallel, s is for single
import scan.stico as stico
import config
import scantools
import numpy as np
xlabs = [config.axl['13c'],config.axl['18o']]
ylabs = [config.axl["ph"]]*2
xlims = [(-60,-20),(-5,15)]
ylims = [(150,25)]*2
fig, axes = scantools.plot_init(1, 2, xlabs=xlabs, ylabs=ylabs,xlims=xlims,ylims=ylims)


# mode='seasonpipe'
mode='simple'
# mode='simple'
fractionation=1
offset=False
echam_enrich=True

isotope='18O'
for i,ax in zip(['18O'],axes):

    texfilesrcsig = open(config.TabDir+'src_sig_%s.tex' % i, 'w')


    xbase,res,residual,lisa,A,b,sens_obs=stico.run_inversion(isotope,mode=mode,sens_obs=True,offset=offset,fractionation=fractionation,echam_enrich=echam_enrich,bounds='res')
    print(sens_obs)
    # stico.plot_inversion(ax,residual,lisa,i,marker='*')
    print(xbase)
    sens_results = stico.sens_fractions(i,xbase,lisa,A,b,percentage=10)
    sens_results=stico.sens_stats(sens_results)
    stico.sens_results_to_table(sens_results,i)
    stico.src_sig_table(xbase,texfilesrcsig ,i)        
    
    # xbase,res,residual,lisa,A,b=stico.run_inversion(i,mode=mode ,offset=1)
    # print(xbase)
    # stico.src_sig_table(xbase,texfilesrcsig ,i)        

    # res,residual,lisa,A,b=stico.run_inversion(i,offset=-1)
    # xbase,res,residual,lisa,A,b=stico.run_inversion(i,mode=mode,offset=-1)
    # print(xbase)
    # stico.src_sig_table(xbase,texfilesrcsig ,i)        
    # stico.plot_inversion(ax,residual,lisa,i,marker='d')
    # xbase = stico.result_to_d(res['x'], isotope=i)
    # print(xbase)

    # res,residual,lisa,A,b=stico.run_inversion(i,mode='pipe')
    # stico.plot_inversion(ax,residual,lisa,i,marker='>')
    # xbase = stico.result_to_d(res['x'], isotope=i)
    # print(xbase)

    # res,residual,lisa,A,b=stico.run_inversion(i,method='press')
    # stico.plot_inversion(ax,residual,lisa,i,marker='<')
    # xbase = stico.result_to_d(res['x'], isotope=i)
    # print(xbase)

    # texfilesrcsig.close()

# stico.add_lisa(axes[0],lisa,'d13C(CO)')
# stico.add_lisa(axes[1],lisa,'d18O(CO)')

# axes[0].legend()
# fig.tight_layout()
# fig.savefig(config.FigDir+"stico_model_res_lisa.pdf")
