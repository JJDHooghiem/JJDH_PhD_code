#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Don't remove the line below, it is checked by "one to run them all"
# --otrta-p--
# extension p means parallel, s is for single
import scantools
import config
import scan.stico as stico
import numpy as np
# xlabs = [r"$\delta^{13}\ch{C}$",r"$\delta^{18}\ch{O}$"]
# ylabs = [r"$p$ hPa",r"$p$ hPa"]
# xlims = [(-57,-27),(-3,13)]
# ylims = [(140,40)]*2

xlabs = [config.axl['18o']]*2
ylabs = [config.axl['ph']]*2
xlims = [(-7,13)]*2
ylims = [(140,40)]*2
# fig, axes = scantools.plot_init(1, 2, xlabs=xlabs, ylabs=ylabs,xlims=xlims,ylims=ylims)
fig, axes = scantools.plot_init(1, 2, xlabs=xlabs, ylabs=ylabs,xlims=xlims,ylims=ylims)

residuals_m = []
residuals_s = []
i='18O'
# modes=['full', 'seasonpipe','season'     , 'simple'     , 'pipe']
# modes=[ 'season']
# modes=[  'simple'     ]
texfilesrcsigall = open(config.TabDir+'src_sig_all.tex', 'w')
sets=['S1','S2','S3','S4','S5','S6']
bscens=["res","res","res",'strict','strict','strict']
modes=[ 'simple'     ,'season',   'pipe', 'simple'     ,'season',   'pipe']
axes_d=[axes[0],axes[0],axes[0],axes[1],axes[1],axes[1]]
for bscen,mode,m,l,pre,ax in zip(bscens,modes,config.Markers[1:],config.Linestyles[1:],sets,axes_d):
    # for i,ax in zip(['13C','18O'],axes):
    texfilesrcsig = open(config.TabDir+'src_sig_%s_%s.tex' % (i,mode), 'w')
    xbase,res,residual,lisa,A,b=stico.run_inversion(i,mode=mode,method='hyb',sens_obs=False,fractionation=1,echam_enrich=True,bounds=bscen)
    print('#################################################################################################################################')
    print()
    print(mode)
    print()
    print(i)
    print()
    print(res)
    print(xbase)
    print(residual)
    print('#################################################################################################################################')
    stico.src_sig_table(xbase,texfilesrcsig ,i)        
    texfilesrcsig.close()
    #print(xbase)
    mean=np.mean(residual)
    std=np.std(residual)

    
    scantools.npa_to_tex_table(np.append(np.array([pre]),np.append(xbase[:3],np.array([std]))), 0,texfilesrcsigall)
    residuals_m.append(mean)
    residuals_s.append(std)

    stico.plot_inversion(ax,residual,lisa,i,marker=m,linestyle=l,label=pre)

    # sens_results = stico.sens_fractions(i,xbase,lisa,A,b,percentage=10)
    # sens_results=stico.sens_stats(sens_results)
    # stico.sens_results_to_table(sens_results,i)

    
    # xbase,res,residual,lisa,A,b=stico.run_inversion(i,mode=mode ,offset=2)
    # print(xbase)
    # stico.src_sig_table(xbase,texfilesrcsig ,i)        

    # res,residual,lisa,A,b=stico.run_inversion(i,offset=-1)
    # xbase,res,residual,lisa,A,b=stico.run_inversion(i,mode=mode,offset=-3)
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
# stico.add_lisa(axes[0],lisa,'d13C(CO)',fmt='d',xerr=0.5)
# stico.add_lisa(axes[1],lisa,'d18O(CO)',fmt='d',xerr=0.5)
texfilesrcsigall.close()
stico.add_lisa(axes[0],lisa,'d18O(CO)',fmt='d',xerr=0.5)
stico.add_lisa(axes[1],lisa,'d18O(CO)',fmt='d',xerr=0.5)
# handles,labels=scantools.getUniqueLegend(axes[0])
handles,labels=scantools.getUniqueLegend(axes[0])
axes[0].legend(handles=handles,labels=labels)

handles,labels=scantools.getUniqueLegend(axes[1])
axes[1].legend(handles=handles,labels=labels)

# axes[0].legend(handles=handles,labels=labels)
# handles,labels=scantools.getUniqueLegend(axes[1])
# axes[1].legend(handles=handles,labels=labels)

fig.tight_layout()
fig.savefig(config.FigDir+"stico_model_res_lisa.pdf")

residuals_m = np.array(residuals_m)
residuals_s = np.array(residuals_s)
texfilesrcsig = open(config.TabDir+'src_sig_means_st.tex', 'w')
prec=1
scantools.npa_to_tex_table(residuals_m,prec,texfilesrcsig)
scantools.npa_to_tex_table(residuals_s,prec,texfilesrcsig)
texfilesrcsig.close()
# labs=['fco2','fch4',r'fo1d $\times100$','fpipe_high','fpipe_mid','fpipe_low']
# factors=[1,1,100,1,1,1]
# for date in np.unique(lisa['Date']):
#     mask=(lisa['Date']==date)
#     for i,l,c,f in zip(range(0,6),labs,colors,factors):
#         plt.plot(f*A[mask,i],lisa['PT'][mask],'o',linestyle='-',color=c,label=l)
#     plt.suptitle(date)
#     plt.legend()
#     plt.ylabel(r'$\theta$ K')
#     plt.xlabel(r'$f(\ch{X})$ K')
#     plt.savefig(config.FigDir+'stico_fracinv_'+date+'.pdf')
#     plt.close()

# labs=['fco2','fch4',r'fo1d','fpipe_high','fpipe_mid','fpipe_low']
# factors=[1,1,1,1,1,1]

# for i in range(0,6):
#     for date,l,c in zip(np.unique(lisa['Date']),labs,colors):
#         mask=(lisa['Date']==date)
#         plt.plot(A[mask,i],lisa['PT'][mask],'o',linestyle='-',color=c,label=date)
#     plt.suptitle(labs[i])
#     plt.legend()
#     plt.ylabel(r'$\theta$ K')
#     plt.xlabel(r'$f(\ch{X})$ K')
#     plt.savefig(config.FigDir+'stico_fracinv_'+labs[i]+'.pdf')
#     plt.close()
#     # plt.plot(d,d+res,'o',label="LISA")
#     # plt.plot(d+res,p,'o',label="inversion")

# # plt.xlabel('$\delta^{18}\ch{O}(\ch{CO})$')

# # plt.ylabel('$p$ (hPa)')
# # plt.legend()
# # plt.savefig(config.FigDir+'stico_inversionLISA.pdf')
