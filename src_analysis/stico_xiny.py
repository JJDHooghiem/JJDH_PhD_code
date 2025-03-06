import scan.stico as stico
import matplotlib.pyplot as plt
import config
import scantools
var1 = 'FMO1DCH4'
var2 = 'CH4'
# var1='FMO1DHCHO'
# var2='FOZHCHO'

varlist=['CH3O2','HCHO','CH3O','CH2OO',"CO2"]
for prefix in ['FOZ','FCM',"FMO1D"]:
    for var2 in varlist:
        var1=prefix+var2
        xlabs = [var1+'/'+var2]
        ylabs = [config.axl['ph']]
        fig, axes = scantools.plot_init(1, 1, xlabs=xlabs, ylabs=ylabs)
        stico.echamfx(axes, var1, var2)
        plt.savefig(config.FigDir+'stico_'+var1.lower() +
                    '_'+var2.lower()+'.pdf', format='pdf')
        plt.close()

# for var2 in varlist:
#     var1='FOZ'+var2
#     fig=stico.echamFX(var1,var2)
#     plt.savefig(config.FigDir+'stico_'+var1.lower()+'_'+var2.lower()+'.pdf',format='pdf')

#     fig=stico.echamFX(var1,var2)
#     plt.savefig(config.FigDir+'stico_'+var1.lower()+'_'+var2.lower()+'.pdf',format='pdf')
